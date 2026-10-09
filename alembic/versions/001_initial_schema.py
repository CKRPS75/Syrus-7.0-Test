"""Initial schema creation

Revision ID: 001_initial_schema
Revises: 
Create Date: 2026-10-08 20:45:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from geoalchemy2 import Geometry

revision: str = '001_initial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Ensure postgis extension exists
    op.execute("CREATE EXTENSION IF NOT EXISTS postgis;")

    # Travellers table
    op.create_table(
        'travellers',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('budget', sa.Float(), nullable=False, server_default='100.0'),
        sa.Column('deadline', sa.DateTime(timezone=True), nullable=True),
        sa.Column('max_walking_minutes', sa.Integer(), nullable=False, server_default='30'),
        sa.Column('accessibility_required', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('risk_tolerance', sa.Float(), nullable=False, server_default='0.5'),
        sa.Column('allowed_modes', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='["BUS", "METRO", "WALK"]'),
        sa.Column('forbidden_modes', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='[]'),
        sa.Column('transfer_tolerance', sa.Integer(), nullable=False, server_default='3'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False)
    )

    # Journeys table
    op.create_table(
        'journeys',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('traveller_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('travellers.id', ondelete='CASCADE'), nullable=False),
        sa.Column('origin', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('destination', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('departure_time', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('status', sa.String(length=50), server_default='ACTIVE', nullable=False),
        sa.Column('current_itinerary_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False)
    )

    # Itineraries table
    op.create_table(
        'itineraries',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('journey_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('journeys.id', ondelete='CASCADE'), nullable=False),
        sa.Column('total_duration', sa.Integer(), nullable=False),
        sa.Column('arrival_time', sa.DateTime(timezone=True), nullable=False),
        sa.Column('total_fare', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('walking_minutes', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('transfers', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('risk_score', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('is_current', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('is_protected', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('route_data', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False)
    )

    # Add foreign key from journeys to itineraries for current_itinerary_id
    op.create_foreign_key(
        'fk_journey_current_itinerary',
        'journeys', 'itineraries',
        ['current_itinerary_id'], ['id'],
        ondelete='SET NULL', use_alter=True
    )

    # Events table
    op.create_table(
        'events',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('event_type', sa.String(length=100), nullable=False),
        sa.Column('status', sa.String(length=50), server_default='ACTIVE', nullable=False),
        sa.Column('trust_status', sa.Enum('IGNORE', 'WATCH', 'CONFIRMED', name='truststatusenum'), nullable=False, server_default='WATCH'),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('affected_line', sa.String(length=100), nullable=True),
        sa.Column('affected_stop', sa.String(length=100), nullable=True),
        sa.Column('affected_route', sa.String(length=100), nullable=True),
        sa.Column('severity', sa.String(length=50), server_default='MEDIUM', nullable=False),
        sa.Column('latitude', sa.Float(), nullable=True),
        sa.Column('longitude', sa.Float(), nullable=True),
        sa.Column('geometry', Geometry(geometry_type='POINT', srid=4326), nullable=True),
        sa.Column('valid_from', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('valid_to', sa.DateTime(timezone=True), nullable=True),
        sa.Column('confidence_score', sa.Float(), server_default='0.5', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False)
    )

    # Reports table
    op.create_table(
        'reports',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('source_type', sa.String(length=50), nullable=False),
        sa.Column('source_name', sa.String(length=100), nullable=False),
        sa.Column('source_url', sa.String(length=500), nullable=True),
        sa.Column('raw_text', sa.Text(), nullable=False),
        sa.Column('published_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('retrieved_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('latitude', sa.Float(), nullable=True),
        sa.Column('longitude', sa.Float(), nullable=True),
        sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), server_default='{}', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False)
    )

    # Evidence table
    op.create_table(
        'evidence',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('event_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('events.id', ondelete='CASCADE'), nullable=False),
        sa.Column('report_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('reports.id', ondelete='CASCADE'), nullable=False),
        sa.Column('source_type', sa.String(length=50), nullable=False),
        sa.Column('source_name', sa.String(length=100), nullable=False),
        sa.Column('location_match', sa.Float(), server_default='1.0', nullable=False),
        sa.Column('time_match', sa.Float(), server_default='1.0', nullable=False),
        sa.Column('evidence_weight', sa.Float(), server_default='1.0', nullable=False),
        sa.Column('freshness_score', sa.Float(), server_default='1.0', nullable=False),
        sa.Column('independence_group', sa.String(length=100), server_default='default', nullable=False),
        sa.Column('validation_status', sa.Enum('VALID', 'INVALID', 'UNGROUNDABLE', 'PENDING', name='validationstatusenum'), server_default='VALID', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False)
    )

    # Route Impacts table
    op.create_table(
        'route_impacts',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('event_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('events.id', ondelete='CASCADE'), nullable=False),
        sa.Column('journey_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('journeys.id', ondelete='CASCADE'), nullable=False),
        sa.Column('affects_route', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('affected_leg', postgresql.JSONB(astext_type=sa.Text()), server_default='{}', nullable=False),
        sa.Column('estimated_delay', sa.Integer(), server_default='0', nullable=False),
        sa.Column('route_feasible', sa.Boolean(), server_default='true', nullable=False),
        sa.Column('route_protected', sa.Boolean(), server_default='true', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False)
    )

    # Replan Proposals table
    op.create_table(
        'replan_proposals',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('journey_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('journeys.id', ondelete='CASCADE'), nullable=False),
        sa.Column('event_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('events.id', ondelete='CASCADE'), nullable=False),
        sa.Column('old_itinerary_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('itineraries.id', ondelete='CASCADE'), nullable=False),
        sa.Column('new_itinerary_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('itineraries.id', ondelete='CASCADE'), nullable=False),
        sa.Column('reason', sa.String(length=500), nullable=False),
        sa.Column('time_saved', sa.Integer(), server_default='0', nullable=False),
        sa.Column('status', sa.Enum('PENDING', 'ACCEPTED', 'REJECTED', 'EXPIRED', name='replanstatusenum'), server_default='PENDING', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True)
    )

    # Confirmations table
    op.create_table(
        'confirmations',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('proposal_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('replan_proposals.id', ondelete='CASCADE'), nullable=False),
        sa.Column('journey_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('journeys.id', ondelete='CASCADE'), nullable=False),
        sa.Column('decision', sa.Enum('ACCEPT', 'REJECT', name='decisionenum'), nullable=False),
        sa.Column('confirmed_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False)
    )

    # Data Sources table
    op.create_table(
        'data_sources',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('source_type', sa.String(length=50), nullable=False),
        sa.Column('source_name', sa.String(length=100), nullable=False),
        sa.Column('source_url', sa.String(length=500), nullable=True),
        sa.Column('version', sa.String(length=50), nullable=True),
        sa.Column('checksum', sa.String(length=100), nullable=True),
        sa.Column('retrieved_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('validation_status', sa.String(length=50), server_default='VALID', nullable=False),
        sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), server_default='{}', nullable=False)
    )


def downgrade() -> None:
    op.drop_table('data_sources')
    op.drop_table('confirmations')
    op.drop_table('replan_proposals')
    op.drop_table('route_impacts')
    op.drop_table('evidence')
    op.drop_table('reports')
    op.drop_table('events')
    op.drop_constraint('fk_journey_current_itinerary', 'journeys', type_='foreignkey')
    op.drop_table('itineraries')
    op.drop_table('journeys')
    op.drop_table('travellers')

    op.execute("DROP TYPE IF EXISTS decisionenum;")
    op.execute("DROP TYPE IF EXISTS replanstatusenum;")
    op.execute("DROP TYPE IF EXISTS validationstatusenum;")
    op.execute("DROP TYPE IF EXISTS truststatusenum;")
