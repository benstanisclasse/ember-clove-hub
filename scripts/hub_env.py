"""Load Hub config and secrets.

Secrets come only from Windows user environment variables (see config/hub.json
"secrets"); this module never prints or writes their values.
"""
import json
import os
from pathlib import Path

# EMBERCLOVE_HUB_ROOT lets tests run against a scratch copy instead of the real records.
HUB_ROOT = Path(os.environ.get("EMBERCLOVE_HUB_ROOT") or Path(__file__).resolve().parent.parent)
CONFIG_PATH = HUB_ROOT / "config" / "hub.json"


def load_config():
    with open(CONFIG_PATH, encoding="utf-8") as f:
        return json.load(f)


def _read_user_env(name):
    value = os.environ.get(name)
    if value:
        return value
    # Processes started before `setx` don't see the new variable; read it from the registry.
    if os.name == "nt":
        import winreg
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment") as key:
                return winreg.QueryValueEx(key, name)[0]
        except FileNotFoundError:
            return None
    return None


def get_secret(key):
    env_name = load_config()["secrets"][key]
    value = _read_user_env(env_name)
    if not value:
        raise RuntimeError(f"Secret '{key}' not found: set the {env_name} user environment variable.")
    return value


def higgsfield_credentials():
    """Return the Higgsfield API credentials and expose them as HF_CREDENTIALS for the SDK."""
    creds = get_secret("higgsfield_api")
    os.environ["HF_CREDENTIALS"] = creds
    return creds


if __name__ == "__main__":
    cfg = load_config()
    for key, env_name in cfg["secrets"].items():
        try:
            get_secret(key)
            print(f"{key}: OK ({env_name} is set)")
        except RuntimeError as e:
            print(f"{key}: MISSING - {e}")
