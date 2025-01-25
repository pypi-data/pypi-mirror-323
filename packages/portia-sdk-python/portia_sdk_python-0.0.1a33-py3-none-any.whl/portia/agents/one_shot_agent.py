"""A simple OneShotAgent that is optimized for simple tool calling tasks.

It invokes the OneShotToolCallingModel up to four times but each individual attempt is a one shot.
This agent is useful when the tool call is simple as it minimizes cost, but the VerifierAgent will
be more successful on anything but simple tool calls.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from langchain_core.messages import SystemMessage
from langchain_core.prompts import ChatPromptTemplate, HumanMessagePromptTemplate
from langgraph.graph import END, START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode

from portia.agents.agent_node_utils.summarizer import LLMSummarizer
from portia.agents.base_agent import BaseAgent, Output
from portia.agents.execution_utils import (
    AgentNode,
    next_state_after_tool_call,
    process_output,
    tool_call_or_end,
)
from portia.agents.toolless_agent import ToolLessAgent
from portia.context import get_execution_context
from portia.llm_wrapper import LLMWrapper
from portia.workflow import Workflow

if TYPE_CHECKING:
    from langchain.tools import StructuredTool
    from langchain_core.language_models.chat_models import BaseChatModel

    from portia.config import Config
    from portia.plan import Step
    from portia.tool import Tool
    from portia.workflow import Workflow


class OneShotToolCallingModel:
    """OneShotToolCallingModel is a one shot model for calling the given tool.

    The tool and context are given directly to the LLM and we return the results.
    This model is useful for simple tasks where the arguments are in the correct form
    and are all present. The OneShotToolModel will not carry out validation of arguments,
    for example it will not complain about missing arguments.

    Prefer to use the VerifierAgent if you have more complicated needs.
    """

    tool_calling_prompt = ChatPromptTemplate.from_messages(
        [
            SystemMessage(
                content="You are very powerful assistant, but don't know current events.",
            ),
            HumanMessagePromptTemplate.from_template(
                [
                    "query:",
                    "{query}",
                    "context:",
                    "{context}",
                    "Use the provided tool. You should provide arguments that match the tool's"
                    "schema using the information contained in the query and context."
                    "Make sure you don't repeat past errors: {past_errors}",
                ],
            ),
        ],
    )

    def __init__(
        self,
        llm: BaseChatModel,
        context: str,
        tools: list[StructuredTool],
        agent: OneShotAgent,
    ) -> None:
        """Initialize the model."""
        self.llm = llm
        self.context = context
        self.agent = agent
        self.tools = tools

    def invoke(self, state: MessagesState) -> dict[str, Any]:
        """Invoke the model with the given message state."""
        model = self.llm.bind_tools(self.tools)
        messages = state["messages"]
        past_errors = [msg for msg in messages if "ToolSoftError" in msg.content]
        response = model.invoke(
            self.tool_calling_prompt.format_messages(
                query=self.agent.step.task,
                context=self.context,
                past_errors=past_errors,
            ),
        )
        return {"messages": [response]}


class OneShotAgent(BaseAgent):
    """Agent responsible for achieving a task by using langgraph.

    This agent does the following things:
    1. Calls the tool with unverified arguments.
    2. Retries tool calls up to 4 times.
    """

    def __init__(
        self,
        step: Step,
        workflow: Workflow,
        config: Config,
        tool: Tool | None = None,
    ) -> None:
        """Initialize the agent."""
        super().__init__(step, workflow, config, tool)

    def execute_sync(self) -> Output:
        """Run the core execution logic of the task."""
        if not self.tool:
            return ToolLessAgent(
                self.step,
                self.workflow,
                self.config,
                self.tool,
            ).execute_sync()

        context = self.get_system_context()
        llm = LLMWrapper(self.config).to_langchain()
        tools = [
            self.tool.to_langchain(
                return_artifact=True,
                ctx=get_execution_context(),
            ),
        ]
        tool_node = ToolNode(tools)

        workflow = StateGraph(MessagesState)
        workflow.add_node(
            AgentNode.TOOL_AGENT,
            OneShotToolCallingModel(llm, context, tools, self).invoke,
        )
        workflow.add_node(AgentNode.TOOLS, tool_node)
        workflow.add_node(AgentNode.SUMMARIZER, LLMSummarizer(llm).invoke)
        workflow.add_edge(START, AgentNode.TOOL_AGENT)

        # Use execution manager for state transitions
        workflow.add_conditional_edges(
            AgentNode.TOOL_AGENT,
            tool_call_or_end,
        )
        workflow.add_conditional_edges(
            AgentNode.TOOLS,
            lambda state: next_state_after_tool_call(state, self.tool),
        )
        workflow.add_edge(AgentNode.SUMMARIZER, END)

        app = workflow.compile()
        invocation_result = app.invoke({"messages": []})

        return process_output(invocation_result["messages"][-1], self.tool)
