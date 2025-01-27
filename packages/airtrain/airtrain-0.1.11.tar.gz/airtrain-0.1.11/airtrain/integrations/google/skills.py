from typing import Optional, Dict, Any
from pydantic import Field
from airtrain.core.skills import Skill, ProcessingError
from airtrain.core.schemas import InputSchema, OutputSchema
from .credentials import GoogleCloudCredentials


class VertexAIInput(InputSchema):
    """Schema for Google Vertex AI input"""

    user_input: str = Field(..., description="User's input text")
    system_prompt: str = Field(
        default="You are a helpful assistant.",
        description="System prompt to guide the model's behavior",
    )
    model: str = Field(default="text-bison", description="Vertex AI model to use")
    max_tokens: int = Field(default=1024, description="Maximum tokens in response")
    temperature: float = Field(
        default=0.7, description="Temperature for response generation", ge=0, le=1
    )


class VertexAIOutput(OutputSchema):
    """Schema for Vertex AI output"""

    response: str = Field(..., description="Model's response text")
    used_model: str = Field(..., description="Model used for generation")
    usage: Dict[str, Any] = Field(default_factory=dict, description="Usage statistics")


class VertexAISkill(Skill[VertexAIInput, VertexAIOutput]):
    """Skill for Google Vertex AI - Not Implemented"""

    input_schema = VertexAIInput
    output_schema = VertexAIOutput

    def __init__(self, credentials: Optional[GoogleCloudCredentials] = None):
        raise NotImplementedError("VertexAISkill is not implemented yet")

    def process(self, input_data: VertexAIInput) -> VertexAIOutput:
        raise NotImplementedError("VertexAISkill is not implemented yet")
