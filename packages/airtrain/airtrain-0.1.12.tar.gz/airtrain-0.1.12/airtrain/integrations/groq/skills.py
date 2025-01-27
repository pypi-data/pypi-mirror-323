from typing import Optional, Dict, Any
from pydantic import Field
from airtrain.core.skills import Skill, ProcessingError
from airtrain.core.schemas import InputSchema, OutputSchema
from .credentials import GroqCredentials


class GroqInput(InputSchema):
    """Schema for Groq input"""

    user_input: str = Field(..., description="User's input text")
    system_prompt: str = Field(
        default="You are a helpful assistant.",
        description="System prompt to guide the model's behavior",
    )
    model: str = Field(default="mixtral-8x7b", description="Groq model to use")
    max_tokens: int = Field(default=1024, description="Maximum tokens in response")
    temperature: float = Field(
        default=0.7, description="Temperature for response generation", ge=0, le=1
    )


class GroqOutput(OutputSchema):
    """Schema for Groq output"""

    response: str = Field(..., description="Model's response text")
    used_model: str = Field(..., description="Model used for generation")
    usage: Dict[str, Any] = Field(default_factory=dict, description="Usage statistics")


class GroqChatSkill(Skill[GroqInput, GroqOutput]):
    """Skill for Groq - Not Implemented"""

    input_schema = GroqInput
    output_schema = GroqOutput

    def __init__(self, credentials: Optional[GroqCredentials] = None):
        raise NotImplementedError("GroqChatSkill is not implemented yet")

    def process(self, input_data: GroqInput) -> GroqOutput:
        raise NotImplementedError("GroqChatSkill is not implemented yet")
