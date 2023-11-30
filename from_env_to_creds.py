import json
from pathlib import Path

env_path = Path('.env')
assert env_path.exists() and env_path.is_file() and env_path.stat().st_size > 0, f"{env_path.name} absent ou vide."

with env_path.open("r", encoding="utf-8") as f:
    env = f.readlines()

env = {line.split("=")[0]: line.split("=")[1].strip().strip('"') for line in env if not line.startswith("#") and line.strip()}

creds = {
    "database": env["POSTGRES_DB"],
    "host": env["POSTGRES_HOST"],
    "user": env["POSTGRES_USER"],
    "password": env["POSTGRES_PASSWORD"],
    "port": env["POSTGRES_PORT"],
}

creds_path = Path(env["CREDSFILE"])

with creds_path.open("w", encoding="utf-8") as f:
    json.dump(creds, f, indent=4)
