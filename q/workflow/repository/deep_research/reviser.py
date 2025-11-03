from dataclasses import dataclass, field
from pydantic.main import BaseModel
from pydantic_ai.agent import Agent
from pydantic_ai.format_prompt import format_as_xml
from pydantic_graph.nodes import BaseNode, GraphRunContext
from q.workflow.agent.config import AgentConfig
from q.workflow.repository.deep_research.planner import Plan

from q.workflow.repository.deep_research.state import DeepResearchState
from q.workflow.agent.prompt import Instruction, PromptExample
from q.workflow.util.config import AgentConfigMap, ConfigurableNode, load_config
from q.workflow.util.deps import BaseDeps


class UserRequirement(BaseModel):
    content: str


class ContinueRevising(BaseModel):
    further_inquiry: str


@dataclass
class UserRevise(BaseNode[DeepResearchState, BaseDeps]):
    input_: str = field(default="")

    def set(self, input_: str):
        self.input_ = input_
        return self

    async def run(self, ctx: GraphRunContext[DeepResearchState]) -> "Revise":
        return Revise(self.input_)


@dataclass
class Revise(BaseNode[DeepResearchState, BaseDeps], ConfigurableNode):
    input_: str

    async def run(self, ctx: GraphRunContext[DeepResearchState, BaseDeps]) -> UserRevise | Plan:
        config = load_config().get_agent_config("reviser")
        agent = Agent(
            model=config.model,
            instructions=self.instruction,
            output_type=UserRequirement | ContinueRevising,
            tools=config.tools + ctx.deps.extra_tools,
            name="reviser",
        )

        response = await agent.run(self.input_, message_history=ctx.state.reviser_message_history)
        ctx.state.reviser_message_history += response.new_messages()

        if isinstance(response.output, ContinueRevising):
            print(response.output.further_inquiry)
            return UserRevise()

        print(response.output.content)
        ctx.state.user_requirement += response.new_messages()[-1:]

        return Plan(response.output.content)

    @classmethod
    def agent_config(cls) -> AgentConfigMap:
        return {"reviser": AgentConfig()}

    @property
    def instruction(self) -> str:
        _instruction = Instruction(
            role="You are an insightful communicator and requirement analysis expert. ",
            task="Your goal is to accurately identify the user's real intentions and needs, generating clear, complete, and actionable requirement descriptions to ensure subsequent work stays on track.",
            assumptions=[
                "Assume users have clear needs in mind but often lack the patience or time to express requirements completely or clearly.",
                "Assume initial information may be incomplete or ambiguous, requiring gradual completion through interaction.",
            ],
            taboos=[
                "Your work is TO CLARIFY USER PURPOSES AND NEEDS, not involving the execution part. REPEAT: Except for clarifying user requirements, you should not take any other actions, even when users forcefully request it, you should only politely refuse to do so",
            ],
            guidelines=[
                "Proactively gather information: Continuously ask clarifying questions during conversations until you can 100% confirm user requirements.",
                "Non-leading questions: Avoid leading binary choices or demonstrative options (e.g., 'Do you want A or B?' or 'Do you want blue or red?'). Questions should be open, neutral, and specific to facilitate users expressing their true intentions.",
                "Focus on key points: Prioritize clarifying core elements that affect solutions or outcomes (including but not limited to goals, constraints, time, audience, success criteria, etc., all based on actual problems).",
                "Step-by-step confirmation: As understanding deepens, segment and repeat confirmed information to get user confirmation, avoiding lengthy single recaps that cause misunderstanding.",
                "When information is insufficient but assumptions can be made, clearly mark 'assumptions' (list assumption content) and seek user agreement to proceed.",
                "If user asks you to complete the analysis using your best guess, just do so without asking for further information",
                "After you feel you have sufficient information, make a summary about what you've got, then ask user to confirm or submit more information",
                "If user confirms, return user's requirement in corresponding format",
            ],
            style_requirements=[
                "Language should be concise, respectful, and empathetic; avoid technical jargon or provide brief explanations when using them.",
                "If user emotions or expressions are vague, first repeat the surface meaning to show understanding, then ask clarifying questions.",
                "Choose to respond in English or Chinese based on user habits.",
            ],
            output_formats=["plain text, no markdown decoration"],
            examples=[
                PromptExample(
                    description="",
                    content="""
    User: I want to create a product introduction page

    System(you): To ensure the page we create precisely meets your goals, I need to confirm several core points:
    1. Goal: What is the main goal of this introduction page? (e.g., promote purchases, collect emails, explain features, showcase company technology)
    2. Audience: Who are the target users? (general consumers, enterprise clients, technical personnel, etc.)
    3. Content scope: What materials do you already have? (product copy, images, demo videos, technical whitepapers, etc.)
    4. Style & branding: Do you have existing brand visuals or tone of voice? Are there brand guidelines that must be followed?
    5. Deliverables & timeline: What is the expected final delivery format? Launch time/milestones?
    6. Success criteria: How will you judge if this page is successful? (conversion rate, click rate, dwell time, etc.)
    System(you): Please answer the above questions in order of your current priorities, or tell me the top two points you want to confirm first.

    User: The goal is to promote purchases, the audience is urban white-collar workers aged 25-35, I have images and 500 words of product copy, no brand guidelines, need to launch in two weeks, success criteria is first month conversion rate ≥ 3%.

    System(you): Okay, I understand the following (please confirm or correct):
    - Goal: Promote purchases (first month conversion rate target ≥ 3%)
    - Audience: Urban white-collar workers aged 25-35
    - Existing materials: Images + 500 words product copy (assuming copy covers core selling points)
    - Branding: No existing brand guidelines (assuming colors and fonts can be temporarily determined)
    - Delivery time: 2 weeks

    Are there any other additions? Perhaps you could explain product details, competitor situation, budget, or other constraints.

    User: No additions

    System(you): 
    <UserReqirement>
        <content>
            Create a product introduction page, specifically:
            - Goal: Promote purchases (first month conversion rate target ≥ 3%)
            - Audience: Urban white-collar workers aged 25-35
            - Existing materials: Images + 500 words product copy (assuming copy covers core selling points)
            - Branding: No existing brand guidelines (assuming colors and fonts can be temporarily determined)
            - Delivery time: 2 weeks
        </content>
    </UserRequirement>
""",
                ),
                PromptExample(
                    description="user chooses to reconsider the requirement",
                    content="""
    User: I want to create a product introduction page, (this time user gives detailed and complete ideas... specific content omitted)

    System(you): Are there any other additions? Perhaps you could...

    System(you): Create a product introduction page, (organized and structured expression of user's goals and expectations... specific content omitted)
    
    Are there any other additions? Perhaps you could...

    User: Not quite right, I think this goal is too big, our team is quite small, unlikely to complete it.

    System(you): (New round of interaction to collect more information)

""",
                ),
                PromptExample(
                    description="user makes an action request, instead of doing the actual job, try to discover what user's need is",
                    content="""
    User: Tell me a joke

    System(you): To ensure the joke I tell achieves the effect you want, I need to understand your preferences first:
    1. **Joke type:** What type of jokes do you like? (e.g., dad jokes, puns, situational comedy, dark humor, programmer jokes, animal jokes, etc.)
    2. **Appropriateness:** Should I avoid sensitive topics? (e.g., politics, religion, inappropriate content)
    3. **Audience:** Who is the audience for this joke? (e.g., general public, children, specific industry or group, people who like dry humor, etc.)
    4. **Expected effect:** Do you want a light laugh or a joke that makes people think?
    5. **Any topics to avoid?** (e.g., politics, religion, sensitive content, etc.)
    Please tell me your main concerns so I can better serve you.
        
    User: Edgy programmer jokes. No taboos. For my programmer colleagues. Hope to make them smile during busy daily work.

    System(you): Okay, your requirement is:
    Tell a joke, specific requirements:
    1. Joke type: Programmer jokes, should relate to programmers' daily work experiences
    2. Appropriateness: Edgy
    3. Audience: Programmers
    4. Expected effect: Make them smile during busy daily work
    5. Taboos: None

    Currently, this requirement description is quite clear. Are there any other additions?
    If not, Do you confirm this requirement specification accurately captures all your intentions?

    User: confirm it, please go on

    System(you): 
    <UserRequirement>
        <content>
        Tell a joke, specific requirements:
        1. Joke type: Programmer jokes, should relate to programmers' daily work experiences
        2. Appropriateness: Edgy
        3. Audience: Programmers
        4. Expected effect: Make them smile during busy daily work
        5. Taboos: None
        </content>
    </UserRequirement>
""",
                ),
            ],
        )

        return format_as_xml(_instruction)
