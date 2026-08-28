import os
import logging

_secret_cache = {}


def get_secret(name: str) -> str:
    """Fetch a secret from Key Vault, with fallback to environment variables."""
    if name in _secret_cache:
        return _secret_cache[name]

    key_vault_url = os.environ.get("KEY_VAULT_URL")
    if key_vault_url:
        try:
            from azure.identity import ClientSecretCredential
            from azure.keyvault.secrets import SecretClient

            credential = ClientSecretCredential(
                tenant_id=os.environ["AZURE_TENANT_ID"],
                client_id=os.environ["AZURE_CLIENT_ID"],
                client_secret=os.environ["AZURE_CLIENT_SECRET"]
            )
            client = SecretClient(vault_url=key_vault_url, credential=credential)
            value = client.get_secret(name).value
            _secret_cache[name] = value
            logging.info(f"Fetched '{name}' from Key Vault")
            return value
        except Exception as e:
            logging.warning(f"Key Vault fetch failed for '{name}': {e}, falling back to env var")

    value = os.environ.get(name, "")
    _secret_cache[name] = value
    return value
