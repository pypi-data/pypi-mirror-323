from typing import List, Optional, Dict, Any, TypeVar, Type
from pydantic import Field, BaseModel
from openai import OpenAI
import base64
from pathlib import Path
from loguru import logger

from airtrain.core.skills import Skill, ProcessingError
from airtrain.core.schemas import InputSchema, OutputSchema
from .credentials import OpenAICredentials


class OpenAIInput(InputSchema):
    """Schema for OpenAI chat input"""

    user_input: str = Field(..., description="User's input text")
    system_prompt: str = Field(
        default="You are a helpful assistant.",
        description="System prompt to guide the model's behavior",
    )
    model: str = Field(default="gpt-4o", description="OpenAI model to use")
    max_tokens: int = Field(default=8192, description="Maximum tokens in response")
    temperature: float = Field(
        default=0.2, description="Temperature for response generation", ge=0, le=1
    )
    images: Optional[List[Path]] = Field(
        default=None,
        description="Optional list of image paths to include in the message",
    )
    functions: Optional[List[Dict[str, Any]]] = Field(
        default=None,
        description="Optional function definitions for function calling",
    )
    function_call: Optional[str] = Field(
        default=None,
        description="Controls function calling behavior",
    )


class OpenAIOutput(OutputSchema):
    """Schema for OpenAI chat output"""

    response: str = Field(..., description="Model's response text")
    used_model: str = Field(..., description="Model used for generation")
    usage: Dict[str, Any] = Field(
        default_factory=dict, description="Usage statistics from the API"
    )
    function_call: Optional[Dict[str, Any]] = Field(
        default=None, description="Function call information if applicable"
    )


class OpenAIChatSkill(Skill[OpenAIInput, OpenAIOutput]):
    """Skill for interacting with OpenAI's models"""

    input_schema = OpenAIInput
    output_schema = OpenAIOutput

    def __init__(self, credentials: Optional[OpenAICredentials] = None):
        """Initialize the skill with optional credentials"""
        super().__init__()
        self.credentials = credentials or OpenAICredentials.from_env()
        self.client = OpenAI(
            api_key=self.credentials.openai_api_key.get_secret_value(),
            organization=self.credentials.openai_organization_id,
        )

    def _encode_image(self, image_path: Path) -> Dict[str, Any]:
        """Convert image to base64 for API consumption"""
        try:
            if not image_path.exists():
                raise FileNotFoundError(f"Image file not found: {image_path}")

            with open(image_path, "rb") as img_file:
                encoded = base64.b64encode(img_file.read()).decode()
                return {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{encoded}"},
                }
        except Exception as e:
            logger.error(f"Failed to encode image {image_path}: {str(e)}")
            raise ProcessingError(f"Image encoding failed: {str(e)}")

    def process(self, input_data: OpenAIInput) -> OpenAIOutput:
        """Process the input using OpenAI's API"""
        try:
            logger.info(f"Processing request with model {input_data.model}")

            # Prepare message content
            content = []

            # Add text content
            content.append({"type": "text", "text": input_data.user_input})

            # Add images if provided
            if input_data.images:
                logger.debug(f"Processing {len(input_data.images)} images")
                for image_path in input_data.images:
                    content.append(self._encode_image(image_path))

            # Prepare messages
            messages = [
                {"role": "system", "content": input_data.system_prompt},
                {"role": "user", "content": content},
            ]

            # Create completion parameters
            params = {
                "model": input_data.model,
                "messages": messages,
                "temperature": input_data.temperature,
                "max_tokens": input_data.max_tokens,
            }

            # Add function calling if provided
            if input_data.functions:
                params["functions"] = input_data.functions
                params["function_call"] = input_data.function_call

            # Create chat completion
            response = self.client.chat.completions.create(**params)

            # Extract function call if present
            function_call = None
            if response.choices[0].message.function_call:
                function_call = response.choices[0].message.function_call.model_dump()

            logger.success("Successfully processed OpenAI request")

            return OpenAIOutput(
                response=response.choices[0].message.content or "",
                used_model=response.model,
                usage={
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens,
                },
                function_call=function_call,
            )

        except Exception as e:
            logger.exception(f"OpenAI processing failed: {str(e)}")
            raise ProcessingError(f"OpenAI processing failed: {str(e)}")


ResponseT = TypeVar("ResponseT", bound=BaseModel)


class OpenAIParserInput(InputSchema):
    """Schema for OpenAI structured output input"""

    user_input: str
    system_prompt: str = "You are a helpful assistant that provides structured data."
    model: str = "gpt-4o"
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    response_model: Type[ResponseT]

    class Config:
        arbitrary_types_allowed = True


class OpenAIParserOutput(OutputSchema):
    """Schema for OpenAI structured output"""

    parsed_response: BaseModel
    used_model: str
    tokens_used: int


class OpenAIParserSkill(Skill[OpenAIParserInput, OpenAIParserOutput]):
    """Skill for getting structured responses from OpenAI"""

    input_schema = OpenAIParserInput
    output_schema = OpenAIParserOutput

    def __init__(self, credentials: Optional[OpenAICredentials] = None):
        """Initialize the skill with optional credentials"""
        super().__init__()
        self.credentials = credentials or OpenAICredentials.from_env()
        self.client = OpenAI(
            api_key=self.credentials.openai_api_key.get_secret_value(),
            organization=self.credentials.openai_organization_id,
        )

    def process(self, input_data: OpenAIParserInput) -> OpenAIParserOutput:
        try:
            # Use parse method instead of create
            completion = self.client.beta.chat.completions.parse(
                model=input_data.model,
                messages=[
                    {"role": "system", "content": input_data.system_prompt},
                    {"role": "user", "content": input_data.user_input},
                ],
                response_format=input_data.response_model,
            )

            if completion.choices[0].message.parsed is None:
                raise ProcessingError("Failed to parse response")

            return OpenAIParserOutput(
                parsed_response=completion.choices[0].message.parsed,
                used_model=completion.model,
                tokens_used=completion.usage.total_tokens,
            )

        except Exception as e:
            raise ProcessingError(f"OpenAI parsing failed: {str(e)}")
