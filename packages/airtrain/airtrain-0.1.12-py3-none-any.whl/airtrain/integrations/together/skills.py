from typing import Optional, Dict, Any
from pydantic import Field
from airtrain.core.skills import Skill, ProcessingError
from airtrain.core.schemas import InputSchema, OutputSchema
from .credentials import TogetherAICredentials


class TogetherAIInput(InputSchema):
    """Schema for Together AI input"""

    user_input: str = Field(..., description="User's input text")
    system_prompt: str = Field(
        default="You are a helpful assistant.",
        description="System prompt to guide the model's behavior",
    )
    model: str = Field(
        default="togethercomputer/llama-2-70b", description="Together AI model to use"
    )
    max_tokens: int = Field(default=1024, description="Maximum tokens in response")
    temperature: float = Field(
        default=0.7, description="Temperature for response generation", ge=0, le=1
    )


class TogetherAIOutput(OutputSchema):
    """Schema for Together AI output"""

    response: str = Field(..., description="Model's response text")
    used_model: str = Field(..., description="Model used for generation")
    usage: Dict[str, Any] = Field(default_factory=dict, description="Usage statistics")


class TogetherAIChatSkill(Skill[TogetherAIInput, TogetherAIOutput]):
    """Skill for Together AI - Not Implemented"""

    input_schema = TogetherAIInput
    output_schema = TogetherAIOutput

    def __init__(self, credentials: Optional[TogetherAICredentials] = None):
        raise NotImplementedError("TogetherAIChatSkill is not implemented yet")

    def process(self, input_data: TogetherAIInput) -> TogetherAIOutput:
        raise NotImplementedError("TogetherAIChatSkill is not implemented yet")
