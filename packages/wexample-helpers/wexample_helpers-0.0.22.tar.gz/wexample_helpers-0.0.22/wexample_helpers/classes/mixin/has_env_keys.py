from typing import List, Any

from wexample_helpers.const.types import StringsList


class HasEnvKeys:
    """Mixin class to handle environment variables validation."""

    def model_post_init(self, *args, **kwargs):
        """
        Validate environment variables right after initialization.
        This method is called by Pydantic after the model is initialized.
        """
        super().model_post_init(*args, **kwargs)
        self.validate_env_keys()

    def get_expected_env_keys(self) -> List[str]:
        """
        Returns a list of required environment variable keys.
        Should be overridden by child classes.
        """
        return []

    def validate_env_keys(self) -> None:
        """
        Validates that all required environment variables are set.
        Raises MissingRequiredEnvVarError if any required variable is missing.
        """
        missing_keys = self._get_missing_env_keys(
            self.get_expected_env_keys()
        )

        if missing_keys:
            from wexample_helpers.errors.missing_required_env_var_error import MissingRequiredEnvVarError

            raise MissingRequiredEnvVarError(missing_keys)

    def _get_missing_env_keys(self, required_keys: StringsList) -> StringsList:
        import os

        return [key for key in required_keys if not os.environ.get(key)]

    def get_env_parameter(self, key: str) -> Any:
        import os

        value = os.getenv(key)
        if value is None:
            raise ValueError(f'Environment variable "{key}" is not defined.')
        return value