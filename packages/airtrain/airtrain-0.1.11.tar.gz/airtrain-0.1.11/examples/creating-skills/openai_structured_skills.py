import sys
import os
from typing import Type, TypeVar, Optional, List, Dict, Any
from pydantic import BaseModel, Field, validator
from openai import OpenAI

parent_dir = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
sys.path.append(parent_dir)

from airtrain.core.skills import Skill, ProcessingError
from airtrain.core.schemas import InputSchema, OutputSchema

# Initialize OpenAI client
client = OpenAI()

# Generic type variable for Pydantic response models
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

    def process(self, input_data: OpenAIParserInput) -> OpenAIParserOutput:
        try:
            # Use parse method instead of create
            completion = client.beta.chat.completions.parse(
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


# Example Response Models
class PersonInfo(BaseModel):
    """Example response model for person information"""

    name: str
    age: int
    occupation: str
    skills: List[str]
    contact: Optional[Dict[str, str]] = Field(default_factory=dict)

    class Config:
        json_schema_extra = {"required": ["name", "age", "occupation", "skills"]}


class MovieReview(BaseModel):
    """Example response model for movie review"""

    title: str
    year: int
    rating: float
    genre: List[str]
    review: str
    pros: List[str]
    cons: List[str]

    class Config:
        json_schema_extra = {
            "required": ["title", "year", "rating", "genre", "review", "pros", "cons"]
        }

    @validator("rating")
    def validate_rating(cls, v):
        """Validate rating after parsing"""
        if not 0 <= v <= 10:
            raise ValueError("Rating must be between 0 and 10")
        return v


# Usage example
if __name__ == "__main__":
    # Test person info parsing
    parser_skill = OpenAIParserSkill()
    person_input = OpenAIParserInput(
        user_input="Tell me about John Doe, a 30-year-old software engineer",
        system_prompt="You are an assistant that extracts structured information about people.",
        response_model=PersonInfo,
    )

    try:
        person_result = parser_skill.process(person_input)
        print("\nPerson Info:")
        print(person_result.parsed_response.model_dump_json(indent=2))
        print(f"Tokens Used: {person_result.tokens_used}")
    except ProcessingError as e:
        print(f"Error: {e}")

    # Test movie review parsing
    movie_input = OpenAIParserInput(
        user_input="Review the movie 'Inception' (2010)",
        system_prompt="You are a movie critic that provides structured reviews.",
        response_model=MovieReview,
    )

    try:
        movie_result = parser_skill.process(movie_input)
        print("\nMovie Review:")
        print(movie_result.parsed_response.model_dump_json(indent=2))
        print(f"Tokens Used: {movie_result.tokens_used}")
    except ProcessingError as e:
        print(f"Error: {e}")
