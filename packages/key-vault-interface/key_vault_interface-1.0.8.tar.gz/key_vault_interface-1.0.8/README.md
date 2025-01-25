<!-- key vault interface documentation master file, created by
sphinx-quickstart on Tue Dec 17 11:19:41 2024.
You can adapt this file completely to your liking, but it should at least
contain the root `toctree` directive. -->

# key vault interface documentation

# API Reference

### *class* key_vault_interface.KeyVaultInterface(\*args, \*\*kwargs)

Bases: `object`

This class serves as an interface for interacting with Azure Key Vault.

Implements a singleton pattern to ensure only one instance is created.
It handles the interaction with Azure Key Vault to retrieve secrets and manage them in memory.

* **Parameters:**
  * **key_vault_name** – The Azure Key Vault name.
  * **tenant_id** – Azure AD Tenant ID.
  * **client_id** – Azure Client ID.
  * **client_secret_var_name** – The environment variable to use to load the client secret matching the client ID.
  * **secrets_to_load** (*dict* *,* *optional*) – Optional dictionary of secrets to load into the interface.

#### forget_secret(alias: str) → None

Removes a secret from memory.

* **Parameters:**
  **alias** (*str*) – Alias of the secret to remove.
* **Raises:**
  **KeyError** – If the secret alias is not found in the loaded secrets.

#### get(secret_name: str) → str

Retrieve a secret value from loaded secrets.

* **Parameters:**
  **secret_name** (*str*) – Name of the secret.
* **Returns:**
  Value of the secret or None if not found.
* **Return type:**
  str
* **Raises:**
  **ValueError** – If the secret_name is not a string.

#### load_secrets() → None

Loads all secrets specified in ‘secrets_to_load’ into memory.

Iterates over the secrets_to_load dictionary and fetches each secret from the Azure Key Vault.

#### update_and_reload_secrets(new_secrets: Dict[str, str]) → None

Updates the list of secrets to load and reloads them.

* **Parameters:**
  **new_secrets** (*dict*) – Dictionary of new secrets to load.
* **Raises:**
  **TypeError** – If new_secrets is not a dictionary.
