from typing import Optional, Dict, Any
from pydantic import Field
from airtrain.core.skills import Skill, ProcessingError
from airtrain.core.schemas import InputSchema, OutputSchema
from .credentials import SambanovaCredentials


class SambanovaInput(InputSchema):
    """Schema for Sambanova input"""

    user_input: str = Field(..., description="User's input text")
    system_prompt: str = Field(
        default="You are a helpful assistant.",
        description="System prompt to guide the model's behavior",
    )
    model: str = Field(default="sambanova-llm", description="Sambanova model to use")
    max_tokens: int = Field(default=1024, description="Maximum tokens in response")
    temperature: float = Field(
        default=0.7, description="Temperature for response generation", ge=0, le=1
    )


class SambanovaOutput(OutputSchema):
    """Schema for Sambanova output"""

    response: str = Field(..., description="Model's response text")
    used_model: str = Field(..., description="Model used for generation")
    usage: Dict[str, Any] = Field(default_factory=dict, description="Usage statistics")


class SambanovaChatSkill(Skill[SambanovaInput, SambanovaOutput]):
    """Skill for Sambanova - Not Implemented"""

    input_schema = SambanovaInput
    output_schema = SambanovaOutput

    def __init__(self, credentials: Optional[SambanovaCredentials] = None):
        raise NotImplementedError("SambanovaChatSkill is not implemented yet")

    def process(self, input_data: SambanovaInput) -> SambanovaOutput:
        raise NotImplementedError("SambanovaChatSkill is not implemented yet")
