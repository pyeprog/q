from dataclasses import dataclass, field

from pydantic_ai.messages import ModelMessage


@dataclass
class DeepResearchState:
    reviser_message_history: list[ModelMessage] = field(default_factory=list)
    user_requirement: list[ModelMessage] = field(default_factory=list)
    research_plan: list[ModelMessage] = field(default_factory=list)
    superviser_message_history: list[ModelMessage] = field(default_factory=list)
    research_report: list[ModelMessage] = field(default_factory=list)
    reviewer_message_history: list[ModelMessage] = field(default_factory=list)
