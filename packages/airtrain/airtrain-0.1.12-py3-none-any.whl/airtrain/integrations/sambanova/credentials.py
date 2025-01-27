from pydantic import Field, SecretStr, HttpUrl
from airtrain.core.credentials import BaseCredentials, CredentialValidationError


class SambanovaCredentials(BaseCredentials):
    """SambaNova credentials"""

    api_key: SecretStr = Field(..., description="SambaNova API key")
    endpoint_url: HttpUrl = Field(..., description="SambaNova API endpoint")

    _required_credentials = {"api_key", "endpoint_url"}

    async def validate_credentials(self) -> bool:
        """Validate SambaNova credentials"""
        try:
            # Implement SambaNova-specific validation
            # This would depend on their API client implementation
            return True
        except Exception as e:
            raise CredentialValidationError(f"Invalid SambaNova credentials: {str(e)}")
