"""Add weather models (locations, weather_observations, alerts)

Revision ID: 0002_add_weather_models
Revises: 0001_enable_postgis_pgvector
Create Date: 2026-09-21 01:05:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "0002_add_weather_models"
down_revision: Union[str, None] = "0001_enable_postgis_pgvector"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Locations table
    op.create_table(
        "locations",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("lat", sa.Float(), nullable=False),
        sa.Column("lon", sa.Float(), nullable=False),
        sa.Column("state", sa.String(length=100), nullable=True),
        sa.Column("country", sa.String(length=10), server_default="IN", nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_locations_id", "locations", ["id"], unique=False)
    op.create_index("ix_locations_name", "locations", ["name"], unique=False)
    op.create_index("idx_location_lat_lon", "locations", ["lat", "lon"], unique=False)

    # 2. Weather Observations table
    op.create_table(
        "weather_observations",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("location_id", sa.Integer(), nullable=False),
        sa.Column("temperature", sa.Float(), nullable=False),
        sa.Column("humidity", sa.Float(), nullable=False),
        sa.Column("rainfall", sa.Float(), server_default="0.0", nullable=False),
        sa.Column("wind_speed", sa.Float(), nullable=False),
        sa.Column("wind_direction", sa.Float(), nullable=True),
        sa.Column("condition", sa.String(length=100), nullable=False),
        sa.Column("source", sa.String(length=50), server_default="openweather", nullable=False),
        sa.Column("timestamp", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["location_id"], ["locations.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_weather_observations_id", "weather_observations", ["id"], unique=False)
    op.create_index("ix_weather_observations_location_id", "weather_observations", ["location_id"], unique=False)
    op.create_index("ix_weather_observations_timestamp", "weather_observations", ["timestamp"], unique=False)
    op.create_index("idx_observation_loc_time", "weather_observations", ["location_id", "timestamp"], unique=False)

    # 3. Alerts table
    op.create_table(
        "alerts",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("location_id", sa.Integer(), nullable=False),
        sa.Column("type", sa.String(length=100), nullable=False),
        sa.Column("severity", sa.String(length=50), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("source", sa.String(length=50), server_default="imd", nullable=False),
        sa.Column("valid_from", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("valid_until", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["location_id"], ["locations.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_alerts_id", "alerts", ["id"], unique=False)
    op.create_index("ix_alerts_location_id", "alerts", ["location_id"], unique=False)


def downgrade() -> None:
    op.drop_table("alerts")
    op.drop_table("weather_observations")
    op.drop_table("locations")
