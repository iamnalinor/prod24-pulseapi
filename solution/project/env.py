from envparse import env

__all__ = ["POSTGRES_CONN"]

POSTGRES_CONN = env.str("POSTGRES_CONN")
if "postgresql://" not in POSTGRES_CONN:
    POSTGRES_CONN = POSTGRES_CONN.replace("postgres://", "postgresql://")
