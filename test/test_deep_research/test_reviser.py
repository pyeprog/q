import os
from pathlib import Path
from pydantic_graph.graph import Graph
from pydantic_graph.persistence.in_mem import SimpleStatePersistence
import pytest

from q.workflow.agent.internal_tool import InternalToolMap
from q.workflow.repository.deep_research.planner import Plan
from q.workflow.repository.deep_research.reviewer import Review
from q.workflow.repository.deep_research.reviser import Revise, UserRevise
from q.workflow.repository.deep_research.state import DeepResearchState
from q.workflow.repository.deep_research.superviser import Supervise
from q.workflow.util.deps import BaseDeps


@pytest.mark.asyncio
async def test_reviser_for_video_making():
    graph = Graph(
        nodes=(Revise, UserRevise, Plan, Supervise, Review),
        state_type=DeepResearchState,
    )
    state = DeepResearchState()
    persistence = SimpleStatePersistence()
    node = Revise(
        "I want to make a video about how to use AI agent, I want to teach newbie the basic concept in casual and humorous fashion. I will put it on youtube."
    )
    deps = BaseDeps(working_dir=Path(__file__).parent, tool_map=InternalToolMap)
    async with graph.iter(node, state=state, persistence=persistence, deps=deps) as run:
        node = await run.next()
        assert isinstance(node, UserRevise)

    print(
        "User>> fill the information gap for me. You can have random guess if you are not sure. I just want to make a simple introduction course for my colleagues"
    )
    node = Revise(
        "fill the information gap for me. You can have random guess if you are not sure. I just want to make a simple introduction course for my colleagues"
    )
    async with graph.iter(node, state=state, persistence=persistence, deps=deps) as run:
        node = await run.next()
        assert isinstance(node, UserRevise)

    print("User>> confirm and no additional information")
    node = Revise("confirm and no additional information")
    async with graph.iter(node, state=state, persistence=persistence, deps=deps) as run:
        node = await run.next()
        assert isinstance(node, Plan)


@pytest.mark.asyncio
async def test_reviser_for_joke_making():
    graph = Graph(
        nodes=(Revise, UserRevise, Plan, Supervise, Review),
        state_type=DeepResearchState,
    )
    state = DeepResearchState()
    persistence = SimpleStatePersistence()
    node = Revise("make a joke for me, I'd like to use it to welcome our new colleague")
    deps = BaseDeps(working_dir=Path(__file__).parent, tool_map=InternalToolMap)
    async with graph.iter(node, state=state, persistence=persistence, deps=deps) as run:
        node = await run.next()
        assert isinstance(node, UserRevise)

    print("User>> I just want a simple tech joke, no forbidden topic, fill the information gap for me")
    node = Revise("I just want a simple tech joke, no forbidden topic, fill the information gap for me")
    async with graph.iter(node, state=state, persistence=persistence, deps=deps) as run:
        node = await run.next()
        assert isinstance(node, Plan)
