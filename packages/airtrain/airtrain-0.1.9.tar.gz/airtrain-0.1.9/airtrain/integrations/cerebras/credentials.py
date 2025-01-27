from pydantic import Field, SecretStr, HttpUrl
from airtrain.core.credentials import BaseCredentials, CredentialValidationError
from typing import Optional


class CerebrasCredentials(BaseCredentials):
    """Cerebras credentials"""

    api_key: SecretStr = Field(..., description="Cerebras API key")
    endpoint_url: HttpUrl = Field(..., description="Cerebras API endpoint")
    project_id: Optional[str] = Field(None, description="Cerebras Project ID")

    _required_credentials = {"api_key", "endpoint_url"}

    async def validate_credentials(self) -> bool:
        """Validate Cerebras credentials"""
        try:
            # Implement Cerebras-specific validation
            # This would depend on their API client implementation
            return True
        except Exception as e:
            raise CredentialValidationError(f"Invalid Cerebras credentials: {str(e)}")
