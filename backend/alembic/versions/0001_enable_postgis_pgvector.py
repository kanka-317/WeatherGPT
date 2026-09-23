"""Enable PostGIS and pgvector extensions

Revision ID: 0001_enable_postgis_pgvector
Revises: 
Create Date: 2026-09-21 01:00:00.000000

"""
from typing import Sequence, Union
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0001_enable_postgis_pgvector"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Enable PostGIS extension for geospatial operations
    op.execute("CREATE EXTENSION IF NOT EXISTS postgis;")
    # Enable pgvector extension for LLM embeddings and similarity search
    op.execute("CREATE EXTENSION IF NOT EXISTS vector;")


def downgrade() -> None:
    # Drop extensions on rollback
    op.execute("DROP EXTENSION IF EXISTS vector;")
    op.execute("DROP EXTENSION IF EXISTS postgis;")
