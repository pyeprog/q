from pydantic_graph.graph import Graph
import pytest

from q.workflow.agent.util import model_response
from q.workflow.repository.deep_research.halt import BackToResearchConducting, Halt
from q.workflow.repository.deep_research.reviewer import Review
from q.workflow.repository.deep_research.state import DeepResearchState
from q.workflow.util.deps import BaseDeps


@pytest.fixture
def user_requirement_text() -> str:
    return "I need a comprehensive report on the current and future impact of Artificial Intelligence (AI) on the global job market. Please include both positive and negative effects, and potential strategies for adaptation. The report should be accessible to a non-technical audience but backed by solid research."


@pytest.fixture
def research_plan_text() -> str:
    return """
	1.	Which industries and job roles are most susceptible to automation and displacement by AI technologies in the next 5-10 years?
    2.	What new job categories and skills are emerging or expected to emerge as a direct result of AI development and adoption?	
    3.	What are the potential economic impacts of AI on wages, income inequality, and overall employment levels across different regions?	
    4.	What strategies (e.g., policy, education, reskilling) can individuals, businesses, and governments adopt to mitigate negative impacts and leverage the opportunities presented by AI?	
    5.	What are the ethical and societal considerations related to AI's influence on the workforce, including issues of bias, surveillance, and job quality?	
    6.	How does the pace of AI adoption vary geographically, and what are the implications for global labor markets?
    """


@pytest.fixture
def research_report_text() -> str:
    return """
Research Report
Title: The Transformative Impact of Artificial Intelligence on the Global Job Market: Analysis, Implications, and Actionable Recommendations
Executive Summary:
Artificial Intelligence (AI) is rapidly reshaping the global job market, presenting both significant challenges and unprecedented opportunities. While certain routine and predictable job roles, particularly in manufacturing and administrative services, are highly susceptible to automation, AI is also a powerful catalyst for the creation of new industries, job categories, and skill demands. Economically, AI's influence is complex, often exacerbating income disparities due to skill-biased technological change, while simultaneously boosting productivity. Effective adaptation strategies, encompassing government policy, educational reform, and continuous reskilling, are crucial to navigate this transition equitably. Ethical considerations, including algorithmic bias in hiring and increased workplace surveillance, demand proactive attention and robust regulatory frameworks. This report provides an in-depth analysis supported by examples and proposes actionable recommendations for various stakeholders.
Conclusion:
The advent of Artificial Intelligence represents an irreversible and profound inflection point for the global job market. While the challenges of job displacement, potential wage inequality, and ethical dilemmas are substantial and require vigilant management, the opportunities for economic growth, enhanced productivity, and the creation of entirely new forms of work are equally significant. Ensuring a positive and inclusive future of work in the age of AI requires a multi-pronged, collaborative, and proactive approach with specific, actionable recommendations:
Actionable Recommendations:
	•	For Governments:
	▪	Invest in Public Goods: Massively increase investment in public education, digital infrastructure, and accessible lifelong learning programs, including free or subsidized vocational training in AI-relevant skills.	▪	Strengthen Social Safety Nets: Explore and implement robust social safety nets, including re-evaluation of unemployment benefits, wage insurance, and UBI pilots to cushion the impact of job transitions.	▪	Regulate Ethically: Develop and enforce clear, adaptable regulations for AI in the workplace, focusing on data privacy, algorithmic transparency, and mitigating bias in hiring and management.	▪	Foster Innovation & Entrepreneurship: Create tax incentives and funding programs for businesses developing ethical AI solutions and for startups creating new, AI-complementary job roles.	•	For Businesses:
	▪	Prioritize Reskilling & Upskilling: Proactively invest in continuous learning and development programs for their workforce, focusing on AI literacy, data skills, and uniquely human capabilities, fostering internal mobility rather than external hiring for new AI roles.	▪	Adopt Human-Centric AI: Design AI implementation strategies that augment human capabilities and improve job quality, rather than purely automating tasks, promoting collaboration between humans and AI.	▪	Ensure Ethical AI Deployment: Implement internal ethical AI guidelines, conduct regular bias audits of AI systems, and ensure transparency in AI-driven decision-making processes affecting employees.	•	For Individuals:
	▪	Embrace Lifelong Learning: Actively seek out opportunities for continuous learning and skill development, focusing on AI literacy, critical thinking, creativity, and emotional intelligence. Leverage online platforms and vocational programs.	▪	Cultivate Adaptability: Be prepared for career transitions and fluid job roles, developing a resilient and adaptable mindset.	▪	Focus on Unique Human Strengths: Hone skills that are inherently human and difficult for AI to replicate, such as complex interpersonal communication, strategic reasoning, and creative problem-solving.
By acting decisively and collaboratively, societies can harness AI's transformative power to build a more productive, equitable, and fulfilling future of work for all.
"""


@pytest.mark.asyncio
async def test_reviewer(user_requirement_text, research_plan_text, research_report_text):
    graph = Graph(nodes=(Review, Halt), state_type=DeepResearchState)
    state = DeepResearchState(
        user_requirement=[model_response([user_requirement_text])],
        research_plan=[model_response([research_plan_text])],
    )
    node = Review(research_report_text)

    async with graph.iter(node, state=state, deps=BaseDeps()) as run:
        node = await run.next()
        assert isinstance(node, Halt)
        assert isinstance(node.review, BackToResearchConducting)
        assert node.review.feedback
