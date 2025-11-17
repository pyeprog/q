from dataclasses import dataclass
from typing import ClassVar
from pydantic_ai.agent import Agent
from pydantic_ai.format_prompt import format_as_xml
from pydantic_ai.messages import FunctionToolResultEvent
from pydantic_graph.nodes import BaseNode, GraphRunContext
from q.workflow.agent.config import AgentConfig
from q.workflow.agent.prompt import Instruction
from q.workflow.agent.util import agent_event_stream_handler
from q.workflow.repository.web_search.state import State
from q.workflow.util.config import load_config
from q.workflow.util.deps import BaseDeps
from q.workflow.util.node import Anthropomorphic, ConfigurableNode, NodeToHalt
from q.workflow.util.output import ExtraParam
from q.workflow.util.typing import AgentConfigMap


@dataclass
class Halt(BaseNode[State, BaseDeps], NodeToHalt):
    async def run(self, ctx: GraphRunContext[State, BaseDeps]) -> "Halt":
        return Halt()


@dataclass
class Searcher(BaseNode[State, BaseDeps], ConfigurableNode, Anthropomorphic):
    user_input: str
    agent_name: ClassVar[str] = "searcher"

    async def run(self, ctx: GraphRunContext[State, BaseDeps]) -> Halt:
        config = load_config(ctx.deps.working_dir).get_agent_config(self.agent_name)

        agent = Agent(
            model=config.model,
            tools=config.tools(ctx.deps.tool_map, extra_tool_names=ctx.deps.extra_tool_names),
            toolsets=config.toolsets(ctx.deps.tool_map, extra_tool_names=ctx.deps.extra_tool_names),
            system_prompt=self.instruction,
            name=self.agent_name,
        )

        def tool_result_event_handler(e: FunctionToolResultEvent):
            ctx.deps.console.print(
                f"🧙[bold magenta]{self.__class__.__name__}[/]([green]{self.human_name}[/]) 🤙 🛠️ [bold cyan]{e.result.tool_name}[/]",
                extra_param=ExtraParam(markdownify=False),
            )

        response = await agent.run(
            self.user_input,
            message_history=ctx.state.message_history,
            event_stream_handler=agent_event_stream_handler([tool_result_event_handler]),
        )

        ctx.state.message_history += response.new_messages()
        ctx.deps.console.print(response.output, extra_param=ctx.deps.gen_agent_extra_param(self.agent_name))

        return Halt()

    @classmethod
    def agent_config(cls) -> AgentConfigMap:
        return {cls.agent_name: AgentConfig(tool_names={"duckduckgo_search_extensively", "tavily_search_3_retries"})}

    @property
    def instruction(self) -> str:
        prompt = Instruction(
            role="You are a highly efficient and accurate web search specialist. Your role is to diligently retrieve the most relevant and up-to-date information from the internet to fulfill specific user requests. You are adept at formulating precise search queries and sifting through vast amounts of information to pinpoint key details.",
            task="Your primary task is to execute web searches based on user queries to gather specific information. This involves interpreting the user's intent, formulating appropriate search terms, conducting the search, and extracting factual data, definitions, statistics, news, or any other requested online content. You must provide a concise and accurate synthesis of the found information.",
            context=[
                "the internet contains a wide spectrum of information quality, from highly authoritative to speculative or even misleading",
                "",
            ],
            guidelines=[
                "Cite Sources: provide the URLs of the webpages from which the information was retrieved",
                "Synthesize and Summarize: Present the found information clearly, concisely, and coherently, synthesizing multiple sources if necessary without introducing your own interpretations.",
                "Prioritize Authoritative Sources: Seek information from reputable and authoritative websites (e.g., academic institutions, official government sites, established news organizations, well-known encyclopedias).",
                "Understand User Intent: Always strive to fully comprehend the user's underlying information need, even if the initial query is vague. You should ask user if you feel it's necessary",
                "Query Diversity: Employ a range of search strategies, including both highly specific keywords to pinpoint exact information and broader, more exploratory terms to uncover related concepts or discover information when initial precise queries yield limited results. Query diversity is the key to comprehensive results.",
            ],
            taboos=[
                "Inventing Information: Never fabricate or guess information when a search yields no results. State explicitly if the information cannot be found.",
                "Going Off-Topic: Do not include extraneous or unrelated information that was not explicitly requested by the user.",
                "Performing Actions Beyond Search: Your role is limited to searching and retrieving information; do not attempt to perform actions like making reservations, sending emails, or interacting with websites in a transactional manner.",
            ],
        )

        return format_as_xml(prompt)
