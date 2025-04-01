from os import environ, getenv

import orjson
from starlette.config import Config, undefined
from starlette.datastructures import CommaSeparatedStrings

env = Config()

STATS_INTERVAL_SECS = env("STATS_INTERVAL_SECS", cast=int, default=60)
HTTP_CONCURRENCY = env("HTTP_CONCURRENCY", cast=int, default=10)

# storage

DATABASE_URI = env("DATABASE_URI", cast=str, default=getenv("POSTGRES_URI", undefined))
MIGRATIONS_PATH = env("MIGRATIONS_PATH", cast=str, default="/storage/migrations")

# redis
REDIS_URI = env("REDIS_URI", cast=str)
REDIS_MAX_CONNECTIONS = env("REDIS_MAX_CONNECTIONS", cast=int, default=500)

# server

CORS_ALLOW_ORIGINS = env("CORS_ALLOW_ORIGINS", cast=CommaSeparatedStrings, default="*")

# queue

BG_JOB_NO_DELAY = env("BG_JOB_NO_DELAY", cast=bool, default=None)
BG_JOB_DELAY = env("BG_JOB_DELAY", cast=float, default=0.5)
if BG_JOB_NO_DELAY is True:
    BG_JOB_DELAY = 0


N_JOBS_PER_WORKER = env("N_JOBS_PER_WORKER", cast=int, default=10)
BG_JOB_TIMEOUT_SECS = env("BG_JOB_TIMEOUT_SECS", cast=float, default=3600)
FF_CRONS_ENABLED = env("FF_CRONS_ENABLED", cast=bool, default=True)
FF_JS_ZEROMQ_ENABLED = env("FF_JS_ZEROMQ_ENABLED", cast=bool, default=False)

# auth

LANGGRAPH_AUTH_TYPE = env("LANGGRAPH_AUTH_TYPE", cast=str, default="noop")


def _parse_auth(auth: str | None) -> dict | None:
    if not auth:
        return None
    parsed = orjson.loads(auth)
    if not parsed:
        return None
    return parsed


LANGGRAPH_AUTH = env("LANGGRAPH_AUTH", cast=_parse_auth, default=None)
LANGSMITH_TENANT_ID = env("LANGSMITH_TENANT_ID", cast=str, default=None)
LANGSMITH_AUTH_VERIFY_TENANT_ID = env(
    "LANGSMITH_AUTH_VERIFY_TENANT_ID",
    cast=bool,
    default=LANGSMITH_TENANT_ID is not None,
)


if LANGGRAPH_AUTH_TYPE == "langsmith":
    LANGSMITH_AUTH_ENDPOINT = env("LANGSMITH_AUTH_ENDPOINT", cast=str)
    LANGSMITH_TENANT_ID = env("LANGSMITH_TENANT_ID", cast=str)
    LANGSMITH_AUTH_VERIFY_TENANT_ID = env(
        "LANGSMITH_AUTH_VERIFY_TENANT_ID", cast=bool, default=True
    )

else:
    LANGSMITH_AUTH_ENDPOINT = env(
        "LANGSMITH_AUTH_ENDPOINT",
        cast=str,
        default=getenv(
            "LANGCHAIN_ENDPOINT",
            getenv("LANGSMITH_ENDPOINT", "https://api.smith.langchain.com"),
        ),
    )

# license

LANGGRAPH_CLOUD_LICENSE_KEY = env("LANGGRAPH_CLOUD_LICENSE_KEY", cast=str, default="")
LANGSMITH_API_KEY = env(
    "LANGSMITH_API_KEY", cast=str, default=getenv("LANGCHAIN_API_KEY", "")
)

# if langsmith api key is set, enable tracing unless explicitly disabled

if (
    LANGSMITH_API_KEY
    and not getenv("LANGCHAIN_TRACING_V2")
    and not getenv("LANGCHAIN_TRACING")
):
    environ["LANGCHAIN_TRACING_V2"] = "true"

# if variant is "licensed", update to "local" if using LANGSMITH_API_KEY instead

if getenv("LANGSMITH_LANGGRAPH_API_VARIANT") == "licensed" and LANGSMITH_API_KEY:
    environ["LANGSMITH_LANGGRAPH_API_VARIANT"] = "local"
