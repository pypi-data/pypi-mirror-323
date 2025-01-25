import os
import logging
import json as js
import traceback as tb

from datetime import datetime as dt, timezone as tz
from typing import Dict, Optional

from azure.identity import ClientSecretCredential
from azure.keyvault.secrets import SecretClient

log = logging.getLogger(__name__)

try:
    from dotenv import find_dotenv, load_dotenv

    _env = find_dotenv(".env")

    if _env:
        load_dotenv(_env)

except:
    log.warning("unable to load env vars via dotenv")


def resolve_string_or_env(_str, env_var_name: str) -> str:
    """
    Return a non-empty string from the given argument or environment variable.

    :param _str: A possible string value. If provided and non-empty, it is returned as is.
    :type _str: str or None
    :param env_var_name: The environment variable name to use if `_str` is empty or None.
    :type env_var_name: str
    :raises Exception: If both `_str` and the environment variable are empty or unset.
    :return: A valid, non-empty string.
    :rtype: str
    """
    if isinstance(_str, str) and _str:
        return _str

    _str = os.getenv(env_var_name)
    if isinstance(_str, str) and _str:
        return _str

    raise Exception(
        f"Value not defined: provide a non-empty string or set the environment variable '{env_var_name}'"
    )


class KeyVaultInterface:
    """
    Interface for interacting with Azure Key Vault.

    This class handles authentication to Azure Key Vault using `ClientSecretCredential`,
    and retrieves secrets which are kept in memory. Optionally allows loading an initial
    set of secrets.

    :param key_vault_name: The Azure Key Vault name or an environment variable name.
    :type key_vault_name: str or None
    :param tenant_id: Azure AD Tenant ID or an environment variable name.
    :type tenant_id: str or None
    :param client_id: Azure Client ID or an environment variable name.
    :type client_id: str or None
    :param client_secret_var_name: The environment variable to load the client secret from.
    :type client_secret_var_name: str or None
    :param secrets_to_load: Optional dictionary mapping aliases to secret names in Key Vault.
    :type secrets_to_load: dict or None
    """

    def __init__(
        self,
        key_vault_name=None,
        tenant_id=None,
        client_id=None,
        client_secret_var_name=None,
        secrets_to_load: Optional[Dict[str, str]] = None,
    ):
        """
        Initialize the KeyVaultInterface and load secrets.

        :param key_vault_name: The Azure Key Vault name or an environment variable name.
        :type key_vault_name: str or None
        :param tenant_id: Azure AD Tenant ID or an environment variable name.
        :type tenant_id: str or None
        :param client_id: Azure Client ID or an environment variable name.
        :type client_id: str or None
        :param client_secret_var_name: The env var to load the client secret from (defaults to 'KEY_VAULT_SECRET').
        :type client_secret_var_name: str or None
        :param secrets_to_load: Dictionary of aliases to secret names to load immediately.
        :type secrets_to_load: dict or None
        :raises ValueError: If the client secret environment variable is not set.
        """

        key_vault_name = resolve_string_or_env(key_vault_name, 'KEY_VAULT_NAME')
        client_id = resolve_string_or_env(client_id, 'KEY_VAULT_CLIENT_ID')
        tenant_id = resolve_string_or_env(tenant_id, 'KEY_VAULT_TENANT_ID')

        self.key_vault_name = key_vault_name

        if not isinstance(client_secret_var_name, str) or not client_secret_var_name:
            client_secret_var_name = 'KEY_VAULT_SECRET'

        self.secrets_to_load = secrets_to_load or {}
        self.loaded_secrets = {}

        client_secret = os.getenv(client_secret_var_name)
        if not client_secret:
            raise ValueError(
                f"{client_secret_var_name} environment variable is required but not set."
            )

        if False:
            """
            Disabled since it could lead to conflict in cases where more instances are created
            and the same env var is needed, this wasn't the starting usage idea, but it's better
            to handle all the scenarios until the flow is standardized
            """
            self._clear_env_from_var(client_secret_var_name)

        self.credentials = ClientSecretCredential(
            tenant_id=tenant_id, client_id=client_id, client_secret=client_secret
        )
        self.kv_address = f"https://{key_vault_name}.vault.azure.net/"
        self.key_vault_client = SecretClient(
            vault_url=self.kv_address, credential=self.credentials
        )

        self.load_secrets()
        log.info("Key Vault Interface initialized")
        self.initialized = True

    @classmethod
    def from_json(cls, config: dict, secrets: dict = None, _raise: bool = False):
        """
        Initialize a KeyVaultInterface from a JSON-like config dict and optional secrets.

        :param config: A dictionary containing keys like 'name', 'tenant_id', 'client_id', etc.
        :type config: dict
        :param secrets: Additional secrets to load, mapped as {alias: key_vault_secret_name}.
        :type secrets: dict, optional
        :param _raise: Whether to re-raise exceptions if initialization fails.
        :type _raise: bool
        :return: A KeyVaultInterface instance or None if initialization fails (and _raise is False).
        :rtype: KeyVaultInterface or None
        """
        if not isinstance(config, dict):
            config = {}

        prefix = config.get("secrets_prefix", "")
        if not (isinstance(prefix, str) and prefix):
            prefix = os.getenv('F40_APP_NAME')
            if isinstance(prefix, str) and prefix:
                prefix = f'{prefix}-'

        try:
            secrets_to_load = cls.apply_prefix_to_strings(prefix, secrets)
            custom_secrets = config.get("secrets_to_load", {})

            if isinstance(custom_secrets, dict):
                secrets_to_load.update(custom_secrets)

            return cls(
                key_vault_name=config.get("name"),
                tenant_id=config.get("tenant_id"),
                client_id=config.get("client_id"),
                client_secret_var_name=config.get("client_secret_var_name", "KEY_VAULT_SECRET"),
                secrets_to_load=secrets_to_load,
            )
        except Exception as e:
            if _raise:
                log.error(
                    f"failed to initialize key vault interface from json:\n{tb.format_exc()}"
                )
                raise e
            return None

    @staticmethod
    def apply_prefix_to_strings(prefix: str, string_map: dict) -> dict:
        """
        Prepend a prefix to each value in a dictionary of alias-to-secret_name pairs.

        :param prefix: The prefix to apply.
        :type prefix: str
        :param string_map: Dictionary with {alias: secret_name}.
        :type string_map: dict
        :return: A new dictionary with each secret_name prefixed.
        :rtype: dict
        """
        if not isinstance(prefix, str):
            prefix = ""

        if isinstance(string_map, dict):
            secrets = {
                alias: f"{prefix}{key_name}"
                for alias, key_name in string_map.items()
                if isinstance(key_name, str)
            }
        else:
            secrets = {}

        return secrets

    def get(self, secret_name: str) -> Optional[str]:
        """
        Retrieve a secret value from loaded secrets.

        :param secret_name: Name (alias) of the secret to retrieve.
        :type secret_name: str
        :return: The secret value or None if not found.
        :rtype: str or None
        :raises ValueError: If secret_name is not a string.
        """
        if not isinstance(secret_name, str):
            raise ValueError(f"Expected str for secret name, got {type(secret_name)}")

        if secret_name not in self.loaded_secrets:
            log.warning(f"{secret_name} not present in loaded secrets. Returning None.")
        return self.loaded_secrets.get(secret_name)

    def _clear_env_from_var(self, client_secret_var_name: str) -> None:
        """
        Remove the client_secret from the environment variable for security.

        :param client_secret_var_name: The name of the environment variable to clear.
        :type client_secret_var_name: str
        """
        try:
            os.environ.pop(client_secret_var_name)
            log.info(f"Removed {client_secret_var_name} from runtime environment")
        except Exception as e:
            log.warning(f"Failed to clean {client_secret_var_name}: {e}")

    def __get_secret_from_kv(self, secret_name: str) -> Optional[str]:
        """
        Retrieve a single secret value from Azure Key Vault.

        :param secret_name: The name of the secret in Key Vault.
        :type secret_name: str
        :return: The secret value, or None if it is expired, not yet valid, or on error.
        :rtype: str or None
        """
        try:
            secret = self.key_vault_client.get_secret(secret_name)

            if secret.properties.expires_on and secret.properties.expires_on <= dt.now(tz=tz.utc):
                log.error(f"Secret {secret_name} is expired as of {secret.properties.expires_on}")
                return None

            if secret.properties.not_before and secret.properties.not_before >= dt.now(tz=tz.utc):
                log.error(f"Secret {secret_name} is not valid until {secret.properties.not_before}")
                return None

            secret_value = secret.value

            if secret.properties.content_type == "json":
                try:
                    secret_value = js.loads(secret_value)
                except Exception:
                    log.error(
                        f"Failed to parse secret {secret_name} as JSON:\n{tb.format_exc()}"
                    )

            return secret_value

        except Exception as e:
            log.error(f"Failed to retrieve secret {secret_name} from Key Vault: {e}")
            return None

    def load_secrets(self) -> None:
        """
        Load secrets specified in 'secrets_to_load' from Azure Key Vault into memory.
        """
        for alias, secret_name in self.secrets_to_load.items():
            self._load_secret(alias, secret_name)

    def _load_secret(self, alias: str, secret_name: str) -> None:
        """
        Load a single secret from Azure Key Vault into memory under a given alias.

        :param alias: The alias to store the secret as.
        :type alias: str
        :param secret_name: The actual name of the secret in Key Vault.
        :type secret_name: str
        """
        try:
            secret = self.__get_secret_from_kv(secret_name)
            self.loaded_secrets[alias] = secret
            log.info(f"Secret '{secret_name}' loaded under alias '{alias}'.")
        except Exception as e:
            log.error(f"Failed to load secret '{secret_name}': {e}")

    def forget_secret(self, alias: str) -> None:
        """
        Remove a secret from memory.

        :param alias: Alias of the secret to remove.
        :type alias: str
        """
        if alias in self.loaded_secrets:
            self.loaded_secrets.pop(alias)
            log.info(f"Secret '{alias}' removed from memory.")
        else:
            log.warning(f"Secret '{alias}' is not loaded.")

    def update_and_reload_secrets(self, new_secrets: Dict[str, str]) -> None:
        """
        Update the list of secrets to load and then reload them from Key Vault.

        :param new_secrets: A dictionary of alias-to-secret_name pairs to add or update.
        :type new_secrets: dict
        """
        if not isinstance(new_secrets, dict):
            log.error(f"Expected dict, got {type(new_secrets)}")
            return

        self.secrets_to_load.update(new_secrets)
        self.load_secrets()
