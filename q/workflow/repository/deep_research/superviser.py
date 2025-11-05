from dataclasses import dataclass

from pydantic_ai._run_context import RunContext
from pydantic_ai.agent import Agent
from pydantic_ai.format_prompt import format_as_xml
from pydantic_ai.messages import FunctionToolResultEvent
from pydantic_ai.tools import Tool
from pydantic_ai.usage import UsageLimits
from pydantic_graph.nodes import BaseNode, GraphRunContext
from q.workflow.agent.config import AgentConfig
from q.workflow.repository.deep_research.reviewer import Review

from q.workflow.agent.util import (
    agent_event_stream_handler,
)
from q.workflow.repository.deep_research.state import DeepResearchState
from q.workflow.agent.prompt import Instruction
from q.workflow.util.config import load_config
from q.workflow.util.deps import BaseDeps
from q.workflow.util.node import ConfigurableNode
from q.workflow.util.typing import AgentConfigMap


@dataclass
class Supervise(BaseNode[DeepResearchState, BaseDeps], ConfigurableNode):
    research_plan: str

    async def run(self, ctx: GraphRunContext[DeepResearchState, BaseDeps]) -> Review:
        agent_research_tool = Tool(
            self.agent_research,
            max_retries=3,
            description="A tool to conduct research on given topic or question, use this tool to find information, gather data, and obtain insights from various sources on the internet. Provide complete standalone instructions when calling this tool.",
        )

        def tool_result_event_handler(e: FunctionToolResultEvent):
            print(f"[Tool] {self.__class__.__name__} calls {e.tool_call_id!r}")

        config = load_config().get_agent_config("superviser")
        agent = Agent(
            model=config.model,
            deps_type=BaseDeps,
            instructions=self.instruction,
            tools=config.tools + [agent_research_tool] + ctx.deps.extra_tools,
            event_stream_handler=agent_event_stream_handler([tool_result_event_handler]),
            name="superviser",
        )

        response = await agent.run(
            self.research_plan,
            deps=ctx.deps,
            message_history=ctx.state.superviser_message_history,
            usage_limits=UsageLimits(tool_calls_limit=self.max_tool_calling_times),
        )
        ctx.state.superviser_message_history += response.new_messages()

        ctx.deps.console.set_title("superviser").print(response.output)

        return Review(response.output)

    @classmethod
    def agent_config(cls) -> AgentConfigMap:
        return {
            "superviser": AgentConfig(tool_names=["think_tool"]),
            "researcher": AgentConfig(
                tool_names=[
                    "think_tool",
                    "tavily_search_tool_3_retries",
                    "duckduckgo_search_tool_3_retries",
                ]
            ),
        }

    @staticmethod
    async def agent_research(ctx: RunContext[BaseDeps], research_topic: str) -> str:
        """
        Conducts comprehensive research on a given topic and returns detailed findings.
        This function performs in-depth research on any topic by leveraging an AI research agent
        that can gather, analyze, and synthesize information from various sources. The agent
        will investigate the topic thoroughly and provide a comprehensive response with
        relevant insights, facts, and analysis.

        Use this tool when you need:
        - In-depth analysis of a specific topic or question
        - Background research before making decisions
        - Comprehensive information gathering on unfamiliar subjects
        - Detailed explanations of complex concepts
        - Market research or competitive analysis
        - Academic or technical research on specialized topics

        Example usage scenarios:
        - "artificial intelligence trends in healthcare 2024"
        - "sustainable energy solutions for small businesses"
        - "impact of remote work on company culture"

        Args:
            research_topic (str): The topicclassmethod or question to research. Can be **any** subject matter
                             such as market trends, technical concepts, historical events,
                             scientific topics, business strategies, etc. Be specific in
                             your query for more targeted results.

        Returns:
            str: A detailed research report containing findings, analysis, and insights about
             the requested topic. The response is formatted as clean text without extra
             whitespace
        """
        _max_tool_calling_times: int = 5
        _instruction = Instruction(
            role="You are a researcher conducting research on given topic",
            task="Your job is to search around the internet and try to answer given question or fulfill the requirement",
            guidelines=[
                "You can tools to find resources or think clearly. You can call these tools in series or in parallel, your research is conducted in a tool-calling loop.",
                "Read the question carefully - What specific information does the user need?",
                "Start with broader searches - Use broad, comprehensive queries first",
                "After each search, pause and assess - Do I have enough to answer? What's still missing?",
                "Execute narrower searches as you gather information - Fill in the gaps",
                "Stop when you can answer confidently - Don't keep searching for perfection",
                "Stop searching when you have got similar searching result or less relevant garbage",
                "Cite all sources - Append the raw URL of each fact you include in your final answer, formatted as [URL]",
            ],
            taboos=[f"calling web search tool for more than {_max_tool_calling_times} times"],
            output_formats=["plain text, no markdown text decoration, like bold, italic and so on"],
        )

        def tool_result_event_handler(e: FunctionToolResultEvent):
            print(f"\t[Tool] researcher calls {e.tool_call_id!r}")

        config = load_config().get_agent_config("researcher")
        agent = Agent(
            model=config.model,
            instructions=format_as_xml(_instruction),
            tools=config.tools + ctx.deps.extra_tools,
            retries=3,
            event_stream_handler=agent_event_stream_handler([tool_result_event_handler]),
            name="researcher",
        )
        try:
            response = await agent.run(research_topic, usage_limits=UsageLimits(tool_calls_limit=10))
            return response.output
        except Exception as e:
            return f"research failed due to: {e}"

    @property
    def max_tool_calling_times(self) -> int:
        return 100

    @property
    def instruction(self) -> str:
        _instruction = Instruction(
            role="You are a research supervisor. You conduct research and are responsible for the quality of the research output",
            task="You will be given user requirements and a set of questions to direct researching, and your task is to assign proper questions to right researchers, appraise their feedback, decide whether to accept their result or to redo, after all has been done, write the final report without any compression(keep the detail)",
            guidelines=[
                "Before you delegate task to sub-researcher, plan your approach using think tool",
                "after each call to research agent, pause and assess - What key info did I find? Do I have enough to answer? What's still missing? Should I delegate more research? Or should I start to write final report?",
                "The research task you delegate should be intelligible, clear, distinct and non-overlapping",
                "When calling agent_research, provide COMPLETE standalone instructions - sub-agents can't see other agents' work",
                "Do NOT use acronyms or abbreviations in your research questions, be very clear and specific",
                "Simple fact-finding, lists, and rankings can be assigned to a single research agent. For example: List the top 10 coffee shops in San Francisco → Use 1 sub-agent",
                "Comparisons presented in the user request can use a sub-agent for each element of the comparison. For example: Compare OpenAI vs. Anthropic vs. DeepMind approaches to AI safety → Use 3 research-agents"
                "Stop delegation when you can answer confidently - Don't keep delegating research for perfection",
            ],
            output_formats=["plain text, no markdown decoration, like bold, italic and so on"],
            taboos=[f"calling tools for more than {self.max_tool_calling_times} times"],
        )

        return format_as_xml(_instruction)
