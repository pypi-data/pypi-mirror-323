# test_key_vault_interface.py

import os
import pytest
from datetime import datetime as dt, timezone as tz
from unittest.mock import patch, MagicMock
from key_vault_interface.key_vault_interface import KeyVaultInterface

@pytest.fixture(autouse=True)
def reset_singleton():
    KeyVaultInterface._instance = None

@pytest.fixture
def mock_env(monkeypatch):
    # Provide a mock environment variable for the client secret
    monkeypatch.setenv("KEY_VAULT_CLIENT_SECRET", "fake-client-secret")


@pytest.fixture
def mock_secret_client():
    mock_client = MagicMock()
    mock_secret = MagicMock()
    mock_secret.properties.expires_on = None
    mock_secret.properties.not_before = None
    mock_secret.properties.content_type = None
    mock_secret.value = "mocked-secret-value"
    mock_client.get_secret.return_value = mock_secret
    return mock_client


@patch("key_vault_interface.key_vault_interface.SecretClient", autospec=True)
def test_initialization(mock_sc_class, mock_env, monkeypatch, mock_secret_client):
    mock_sc_class.return_value = mock_secret_client

    kv = KeyVaultInterface(
        key_vault_name="testvault",
        tenant_id="fake-tenant",
        client_id="fake-client",
        client_secret_var_name="KEY_VAULT_CLIENT_SECRET",
        secrets_to_load={"alias1": "secret1"},
    )
    assert kv.key_vault_name == "testvault"
    assert "alias1" in kv.loaded_secrets
    assert kv.loaded_secrets["alias1"] == "mocked-secret-value"

    # Check environment var removal
    with pytest.raises(KeyError):
        os.environ["KEY_VAULT_CLIENT_SECRET"]


@patch("key_vault_interface.key_vault_interface.SecretClient", autospec=True)
def test_get_secret(mock_sc_class, mock_env, monkeypatch, mock_secret_client):
    mock_sc_class.return_value = mock_secret_client

    kv = KeyVaultInterface(
        key_vault_name="testvault",
        tenant_id="fake-tenant",
        client_id="fake-client",
        client_secret_var_name="KEY_VAULT_CLIENT_SECRET",
        secrets_to_load={"alias1": "secret1"},
    )
    secret_value = kv.get("alias1")
    assert secret_value == "mocked-secret-value"

    # Test get on a non-existent alias
    missing_secret = kv.get("not_found")
    assert missing_secret is None


@patch("key_vault_interface.key_vault_interface.SecretClient", autospec=True)
def test_forget_secret(mock_sc_class, mock_env, mock_secret_client):
    mock_sc_class.return_value = mock_secret_client

    kv = KeyVaultInterface(
        key_vault_name="testvault",
        tenant_id="fake-tenant",
        client_id="fake-client",
        client_secret_var_name="KEY_VAULT_CLIENT_SECRET",
        secrets_to_load={"alias1": "secret1"},
    )

    # Initially alias1 should be loaded
    assert "alias1" in kv.loaded_secrets

    # Forget the secret
    kv.forget_secret("alias1")
    assert "alias1" not in kv.loaded_secrets

    # Forget non-existent secret (should just warn, no exception)
    kv.forget_secret("not_exists")


@patch("key_vault_interface.key_vault_interface.SecretClient", autospec=True)
def test_update_and_reload_secrets(mock_sc_class, mock_env, mock_secret_client):
    mock_sc_class.return_value = mock_secret_client

    # Start with one secret
    kv = KeyVaultInterface(
        key_vault_name="testvault",
        tenant_id="fake-tenant",
        client_id="fake-client",
        client_secret_var_name="KEY_VAULT_CLIENT_SECRET",
        secrets_to_load={"alias1": "secret1"},
    )

    assert "alias1" in kv.loaded_secrets
    assert "alias2" not in kv.loaded_secrets

    # Update secrets to load and reload
    kv.update_and_reload_secrets({"alias2": "secret2"})
    # After reload, alias2 should be present
    assert "alias2" in kv.loaded_secrets
    # alias1 should still be there
    assert "alias1" in kv.loaded_secrets


@patch("key_vault_interface.key_vault_interface.SecretClient", autospec=True)
def test_invalid_secret_name_type(mock_sc_class, mock_env, mock_secret_client):
    mock_sc_class.return_value = mock_secret_client

    kv = KeyVaultInterface(
        key_vault_name="testvault",
        tenant_id="fake-tenant",
        client_id="fake-client",
        client_secret_var_name="KEY_VAULT_CLIENT_SECRET",
        secrets_to_load={},
    )

    with pytest.raises(ValueError):
        kv.get(123)  # secret name should be a string, not int


@patch("key_vault_interface.key_vault_interface.SecretClient", autospec=True)
def test_expired_secret(mock_sc_class, mock_env):
    # Mock a secret that is expired
    class MockExpiredSecret:
        value = "expired-value"
        properties = MagicMock()
        # Set expires_on to a past time
        properties.expires_on = dt(2000, 1, 1, tzinfo=tz.utc)
        properties.not_before = None
        properties.content_type = None

    mock_client = MagicMock()
    mock_client.get_secret.return_value = MockExpiredSecret()
    mock_sc_class.return_value = mock_client

    kv = KeyVaultInterface(
        key_vault_name="testvault",
        tenant_id="fake-tenant",
        client_id="fake-client",
        client_secret_var_name="KEY_VAULT_CLIENT_SECRET",
        secrets_to_load={"alias_expired": "secret_expired"},
    )

    # The expired secret should be None
    assert kv.get("alias_expired") is None


@patch("key_vault_interface.key_vault_interface.SecretClient", autospec=True)
def test_not_yet_valid_secret(mock_sc_class, mock_env):
    # Mock a secret that is not yet valid (not_before in the future)
    class MockNotYetValidSecret:
        value = "future-value"
        properties = MagicMock()
        # Set not_before to a future time
        properties.not_before = dt(3000, 1, 1, tzinfo=tz.utc)
        properties.expires_on = None
        properties.content_type = None

    mock_client = MagicMock()
    mock_client.get_secret.return_value = MockNotYetValidSecret()
    mock_sc_class.return_value = mock_client

    kv = KeyVaultInterface(
        key_vault_name="testvault",
        tenant_id="fake-tenant",
        client_id="fake-client",
        client_secret_var_name="KEY_VAULT_CLIENT_SECRET",
        secrets_to_load={"alias_future": "secret_future"},
    )

    # The not-yet-valid secret should be None
    assert kv.get("alias_future") is None


@patch("key_vault_interface.key_vault_interface.SecretClient", autospec=True)
def test_json_secret(mock_sc_class, mock_env):
    # Mock a secret with JSON content type
    class MockJsonSecret:
        properties = MagicMock()
        properties.expires_on = None
        properties.not_before = None
        properties.content_type = "json"
        value = '{"key": "value"}'

    mock_client = MagicMock()
    mock_client.get_secret.return_value = MockJsonSecret()
    mock_sc_class.return_value = mock_client

    kv = KeyVaultInterface(
        key_vault_name="testvault",
        tenant_id="fake-tenant",
        client_id="fake-client",
        client_secret_var_name="KEY_VAULT_CLIENT_SECRET",
        secrets_to_load={"alias_json": "secret_json"},
    )

    # The JSON secret should be parsed
    secret_value = kv.get("alias_json")
    assert isinstance(secret_value, dict)
    assert secret_value["key"] == "value"
