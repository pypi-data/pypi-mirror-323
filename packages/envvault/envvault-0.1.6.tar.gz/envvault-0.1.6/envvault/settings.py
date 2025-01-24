import os
from functools import lru_cache

from pydantic import create_model
from pydantic_settings import BaseSettings

from .core import CredentialsManager


class Settings(BaseSettings):
    """
    Manages environment variables using pydantic.
    """

    @classmethod
    def from_credentials(cls, env_name="development"):
        """
        Dynamically loads environment variables from an encrypted .env.enc file.

        :param env_name: Environment name (e.g., development, production).
        :return: Settings instance.
        """
        # Initialize the CredentialsManager
        manager = CredentialsManager(env_name=env_name)
        # Decrypt the .env.enc file
        credentials = manager.decrypt_env()

        # Load environment variables into os.environ
        manager.load_to_environment()

        # Dynamically create a model
        fields = {}
        for key, value in credentials.items():
            # Infer the type based on the value's content
            if value.isdigit():
                fields[key] = (int, ...)  # Integer type
            elif value.lower() in ("true", "false"):
                fields[key] = (bool, ...)  # Boolean type
            else:
                fields[key] = (str, ...)  # Default string type

        DynamicSettings = create_model(
            "DynamicSettings", **fields, __base__=BaseSettings
        )

        # Return the dynamically created model instance
        return DynamicSettings(**credentials)


@lru_cache
def get_settings():
    return Settings.from_credentials(
        env_name=os.getenv("ENV") or os.getenv("NODE_ENV") or "development"
    )


# envvault = get_settings()
