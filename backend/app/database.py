"""
Database module (no local database).

All persistent information for this project (appointments, reminder
flags, etc.) is stored in the external MCP server instead of a local
SQL database.

This file is kept only so existing imports like
`from app.database import init_db` don't break. The functions below
are simple no-ops.
"""

async def init_db() -> None:
    """
    Backwards‑compatible no-op.

    Previously this created SQL tables; now all data lives
    in the MCP server so there is nothing to initialize.
    """
    return None


