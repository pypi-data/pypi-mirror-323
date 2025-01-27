from typing import List, Optional, Dict, Any
from pydantic import Field
from anthropic import Anthropic
import base64
from pathlib import Path
from loguru import logger

from airtrain.core.skills import Skill, ProcessingError
from airtrain.core.schemas import InputSchema, OutputSchema
from .credentials import AnthropicCredentials


class AnthropicInput(InputSchema):
    """Schema for Anthropic chat input"""

    user_input: str = Field(..., description="User's input text")
    system_prompt: str = Field(
        default="You are a helpful assistant.",
        description="System prompt to guide the model's behavior",
    )
    model: str = Field(
        default="claude-3-opus-20240229", description="Anthropic model to use"
    )
    max_tokens: int = Field(default=1024, description="Maximum tokens in response")
    temperature: float = Field(
        default=0.7, description="Temperature for response generation", ge=0, le=1
    )
    images: Optional[List[Path]] = Field(
        default=None,
        description="Optional list of image paths to include in the message",
    )


class AnthropicOutput(OutputSchema):
    """Schema for Anthropic chat output"""

    response: str = Field(..., description="Model's response text")
    used_model: str = Field(..., description="Model used for generation")
    usage: Dict[str, Any] = Field(
        default_factory=dict, description="Usage statistics from the API"
    )


class AnthropicChatSkill(Skill[AnthropicInput, AnthropicOutput]):
    """Skill for interacting with Anthropic's Claude models"""

    input_schema = AnthropicInput
    output_schema = AnthropicOutput

    def __init__(self, credentials: Optional[AnthropicCredentials] = None):
        """Initialize the skill with optional credentials"""
        super().__init__()
        self.credentials = credentials or AnthropicCredentials.from_env()
        self.client = Anthropic(
            api_key=self.credentials.anthropic_api_key.get_secret_value()
        )

    def _encode_image(self, image_path: Path) -> Dict[str, Any]:
        """Convert image to base64 for API consumption"""
        try:
            if not image_path.exists():
                raise FileNotFoundError(f"Image file not found: {image_path}")

            with open(image_path, "rb") as img_file:
                encoded = base64.b64encode(img_file.read()).decode()
                return {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": f"image/{image_path.suffix[1:]}",
                        "data": encoded,
                    },
                }
        except Exception as e:
            logger.error(f"Failed to encode image {image_path}: {str(e)}")
            raise ProcessingError(f"Image encoding failed: {str(e)}")

    def process(self, input_data: AnthropicInput) -> AnthropicOutput:
        """Process the input using Anthropic's API"""
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

            # Create message
            response = self.client.messages.create(
                model=input_data.model,
                max_tokens=input_data.max_tokens,
                temperature=input_data.temperature,
                system=input_data.system_prompt,
                messages=[{"role": "user", "content": content}],
            )

            # Validate response content
            if not response.content:
                logger.error("Empty response received from Anthropic API")
                raise ProcessingError("Empty response received from Anthropic API")

            if not isinstance(response.content, list) or not response.content:
                logger.error("Invalid response format from Anthropic API")
                raise ProcessingError("Invalid response format from Anthropic API")

            first_content = response.content[0]
            if not hasattr(first_content, "text"):
                logger.error("Response content does not contain text")
                raise ProcessingError("Response content does not contain text")

            logger.success("Successfully processed Anthropic request")

            # Create output
            return AnthropicOutput(
                response=first_content.text,
                used_model=response.model,
                usage={
                    "input_tokens": response.usage.input_tokens,
                    "output_tokens": response.usage.output_tokens,
                },
            )

        except ProcessingError:
            # Re-raise ProcessingError without modification
            raise
        except Exception as e:
            logger.exception(f"Anthropic processing failed: {str(e)}")
            raise ProcessingError(f"Anthropic processing failed: {str(e)}")
