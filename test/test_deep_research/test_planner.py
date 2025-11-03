from pydantic_ai.messages import TextPart
from pydantic_graph.graph import Graph
from pydantic_graph.persistence.in_mem import SimpleStatePersistence
import pytest

from q.workflow.repository.deep_research.halt import Halt
from q.workflow.repository.deep_research.planner import Plan
from q.workflow.repository.deep_research.reviewer import Review
from q.workflow.repository.deep_research.state import DeepResearchState
from q.workflow.repository.deep_research.superviser import Supervise
from q.workflow.util.deps import BaseDeps


@pytest.mark.asyncio
async def test_planner():
    graph = Graph(nodes=(Plan, Supervise, Review, Halt), state_type=DeepResearchState)
    requirement_text = """
    I need to create a product introduction page, details as follows:
    - Goal: Promote purchases (first month conversion rate target ≥ 3%)
    - Audience: Urban white-collar workers aged 25-35
    - Existing materials: Images + 500 words product copy (assuming copy covers core selling points)
    - Branding: No existing brand guidelines (assuming colors and fonts can be temporarily determined)
    - Delivery time: 2 weeks
"""
    node = Plan(requirement_text)
    persistence = SimpleStatePersistence()
    state = DeepResearchState()
    async with graph.iter(node, state=state, persistence=persistence, deps=BaseDeps()) as run:
        node = await run.next()
        assert isinstance(node, Supervise)
        assert state.research_plan
        assert state.research_plan[0].parts
        assert isinstance(state.research_plan[0].parts[0], TextPart)
        assert state.research_plan[0].parts[0].content
        print(state.research_plan[0].parts[0].content)
