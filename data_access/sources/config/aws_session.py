from pydantic_settings import BaseSettings, SettingsConfigDict


class AWSSession(BaseSettings):
    """Pydantic model for AWS (Boto3) Session.

    The class properties are dynamically extracted from the environment
    variables.
    """

    model_config = SettingsConfigDict()

    aws_access_key_id: str
    aws_secret_access_key: str
