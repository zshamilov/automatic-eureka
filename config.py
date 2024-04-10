import os
from dynaconf import Dynaconf


settings = Dynaconf(
    envvar_prefix="DYNACONF",
    settings_files=["settings.toml"],
    load_dotenv=True,
    environments=True,
    encoding="utf-8",
    force_env=os.getenv("DYNACONF_ENV_FOR_DYNACONF"),
    vault_enabled=os.getenv("VAULT_ENABLED_FOR_DYNACONF", False),
    root_path=os.path.dirname(os.path.realpath(__file__)),
    vault={
        "url": os.getenv("VAULT_URL_FOR_DYNACONF"),
        "token": os.getenv("VAULT_TOKEN_FOR_DYNACONF")
    }
)
