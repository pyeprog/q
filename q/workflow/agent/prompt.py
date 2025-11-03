from pydantic.fields import Field
from pydantic.main import BaseModel
from datetime import datetime


class PromptExample(BaseModel):
    description: str
    content: str


class Instruction(BaseModel):
    role: str | None = None
    task: str | None = None
    assumptions: list[str] = Field(default_factory=list)
    context: list[str] = Field(default_factory=list)
    guidelines: list[str] = Field(default_factory=list)
    style_requirements: list[str] = Field(default_factory=list)
    output_formats: list[str] = Field(default_factory=list)
    taboos: list[str] = Field(default_factory=list)
    examples: list[PromptExample] = Field(default_factory=list)
    datetime: str = Field(default_factory=lambda: str(datetime.now()))
