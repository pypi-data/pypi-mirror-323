from pydantic import Field, SecretStr
from airtrain.core.credentials import BaseCredentials, CredentialValidationError

# from google.cloud import storage


class GoogleCloudCredentials(BaseCredentials):
    """Google Cloud credentials"""

    project_id: str = Field(..., description="Google Cloud Project ID")
    service_account_key: SecretStr = Field(..., description="Service Account Key JSON")

    _required_credentials = {"project_id", "service_account_key"}

    async def validate_credentials(self) -> bool:
        """Validate Google Cloud credentials"""
        try:
            # Initialize with service account key
            storage_client = storage.Client.from_service_account_info(
                self.service_account_key.get_secret_value()
            )
            # Test API call
            storage_client.list_buckets(max_results=1)
            return True
        except Exception as e:
            raise CredentialValidationError(
                f"Invalid Google Cloud credentials: {str(e)}"
            )
