from envparse import env

__all__ = ["POSTGRES_CONN", "TOKEN_TTL_HOURS"]

POSTGRES_CONN = env.str("POSTGRES_CONN").replace("postgres://", "postgresql://")

TOKEN_TTL_HOURS = 12
