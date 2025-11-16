import os
from pathlib import Path
from pydantic_graph.graph import Graph
import pytest

from q.workflow.agent.internal_tool import InternalToolMap
from q.workflow.agent.util import model_response
from q.workflow.repository.deep_research.reviewer import ContinueReviewing, DeepenResearch, Review
from q.workflow.repository.deep_research.state import DeepResearchState
from q.workflow.util.deps import BaseDeps


@pytest.mark.asyncio
async def test_reviews():
    graph = Graph(nodes=(Review,), state_type=DeepResearchState)

    report = """
Okay, here's a recap of the game engine search results:

Based on the search results, here's a summary of recent game engine news:

*   **Godot 4.6 dev 3:** A development snapshot of Godot 4.6 was released in November 2025, along with a maintenance release of Godot 3.6.2. This indicates ongoing development
and updates to the Godot Engine.
*   **Unreal Engine 5:** While Unreal Engine 5 was fully released in April 2022, it's still considered a relatively new and actively developed engine. Expect announcements for
Unreal Engine 6 in the coming years.
*   **EDENSPARK:** Gaijin Entertainment announced a new open-source game engine, EDENSPARK.
"""

    state = DeepResearchState(
        user_requirement=[model_response(["research on latest popular game engine for indie game"])],
        research_plan=[model_response(["search for 3 popular game engines, then do a quick summary"])],
        research_report=[model_response([report])],
    )

    node = Review("which one has released new version in 2025?")
    deps = BaseDeps(working_dir=Path(__file__).parent, tool_map=InternalToolMap)

    async with graph.iter(start_node=node, state=state, deps=deps) as run:
        node = await run.next()
        assert isinstance(node, Review)
        node.user_input = "evaluate the research result, deepen the research if possible"
        assert isinstance(node.next_start, ContinueReviewing)

    async with graph.iter(start_node=node, state=state, deps=deps) as run:
        node = await run.next()
        assert isinstance(node, Review)
        assert isinstance(node.next_start, DeepenResearch)
        assert node.next_start.where_to_start in ["research_planning", "research_conducting"]
