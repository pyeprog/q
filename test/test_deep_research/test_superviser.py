from pydantic_ai._run_context import RunContext
from pydantic_ai.messages import (
    ModelRequest,
    UserPromptPart,
)
from pydantic_ai.usage import RunUsage
from pydantic_graph.graph import Graph
import pytest
from q.workflow.agent.util import open_router_model
from q.workflow.repository.deep_research.reviewer import Review
from q.workflow.repository.deep_research.state import DeepResearchState
from q.workflow.repository.deep_research.superviser import Supervise
from q.workflow.util.deps import BaseDeps


@pytest.mark.asyncio
async def test_agent_research():
    mock_ctx = RunContext(deps=BaseDeps(), model=open_router_model("google/gemini-2.0-flash-001"), usage=RunUsage())
    result = await Supervise.agent_research(mock_ctx, "list the top 3 most popular framework for web app frontend")
    assert isinstance(result, str)
    assert result
    print(result)


@pytest.mark.asyncio
async def test_superviser():
    graph = Graph(nodes=(Supervise, Review), state_type=DeepResearchState)
    user_requirement = """
    I need to create a product introduction page, details as follows:
    - Goal: Promote purchases (first month conversion rate target ≥ 3%)
    - Audience: Urban white-collar workers aged 25-35
    - Existing materials: Images + 500 words product copy (assuming copy covers core selling points)
    - Branding: No existing brand guidelines (assuming colors and fonts can be temporarily determined)
    - Delivery time: 2 weeks
"""
    research_plan = """
    Okay, I will generate a list of research questions to guide the creation of your product introduction page, keeping in mind the goal of driving purchases among urban white-collar workers aged 25-35.

    **I. Audience Understanding & Behavior:**

    1.  **Content Preference:** What types of content (e.g., user reviews, expert opinions, video demos, interactive tools) resonate most with urban white-collar workers aged 25-35 when learning about a new product online?
    2.  **Information Needs:** What specific information points are most important to this audience when evaluating a product for purchase? (e.g., price, features, warranty, social proof, return policy)
    3.  **Mobile vs. Desktop:** What percentage of the target audience will likely view the introduction page on a mobile device versus a desktop? How does this influence the design and content strategy?
    4.  **Call to Action Preference:** What types of calls to action (CTAs) are most effective in driving conversions for this demographic? (e.g., "Shop Now," "Learn More," "Get a Discount," "Try it Free")
    5.  **Purchasing Barriers:** What are the primary concerns or hesitations this audience might have that prevent them from purchasing the product immediately? How can the introduction page address these concerns?
    6.  **Social Media Influence:** Which social media platforms are most frequented by the target audience, and how can the introduction page leverage social proof or integration with these platforms?
    7. **Browsing Habits:** How much time does the target audience usually spend on a product introduction page before making a decision?

    **II. Design & Branding (While Temporary):**

    8.  **Color Palette:** What color palettes evoke feelings of trust, modernity, and sophistication for this audience?
    9.  **Font Selection:** What font styles (for headings and body text) are most readable and visually appealing to this demographic in a digital context?
    10. **Imagery:** What types of images (product shots, lifestyle photos, illustrations) are most effective in capturing attention and conveying the product's value proposition?
    11. **Layout & Structure:** What layout and information hierarchy will present the product information in the most digestible and engaging way?
    12. **White Space:** how to use white space effectively make the page look more clean and professional?

    **III. Content Optimization:**

    13. **Keywords:** What keywords are urban white-collar workers likely to use when searching online for products like this one? How can the introduction page be optimized for these keywords?
    14. **Value Proposition:** Is the product's core value proposition clearly and concisely communicated within the first few seconds of viewing the page?
    15. **Mobile Copy:** Is the product copy optimized for mobile viewing, with concise paragraphs and clear headings?

    **IV. Technical & Performance:**

    16. **Page Load Speed:** What is the optimal page load speed to minimize bounce rates and maximize user engagement?
    17. **Cross-Browser Compatibility:** Is the introduction page fully functional and visually consistent across all major web browsers (Chrome, Firefox, Safari, Edge)?
    18. **Analytics Tracking:** What key metrics (e.g., bounce rate, time on page, conversion rate, click-through rate) should be tracked to measure the introduction page's performance?

    **V. Competitive Analysis:**

    19. **Landing page design:** What UI/UX approaches could be learned from competitors' landing page desgin?
    20. **Marketing strategy:** What kind of marketing strategy did competitors use in their landing page?

    **VI. Open-Ended Research:**

    21. **Unstated User Needs:** What unarticulated needs or desires does this target audience have related to the product category? How can the introduction page address these needs in unexpected ways?
    22. **Unexpected Trends:** Are there any emerging trends in web design or online shopping behavior that could be leveraged to enhance the introduction page's effectiveness?
    23. **A/B Testing Ideas:** What specific elements of the introduction page (e.g., headline, CTA button, image) should be A/B tested to optimize for conversion rate?
"""
    state = DeepResearchState(
        user_requirement=[ModelRequest(parts=[UserPromptPart(content=user_requirement)])],
    )
    node = Supervise(research_plan)

    async with graph.iter(node, state=state, deps=BaseDeps()) as run:
        node = await run.next()
        assert isinstance(node, Review)
        print(node.research_report)
