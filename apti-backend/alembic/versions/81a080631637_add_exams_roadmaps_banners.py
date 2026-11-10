"""add_exams_roadmaps_banners

Revision ID: 81a080631637
Revises: 97e6537dbc62
Create Date: 2026-11-10 10:26:35.211975

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


revision: str = '81a080631637'
down_revision: Union[str, Sequence[str], None] = '97e6537dbc62'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Exams table
    op.create_table(
        'exams',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('category_id', sa.String(length=50), nullable=True),
        sa.Column('time_limit_minutes', sa.Integer(), nullable=False, server_default='30'),
        sa.Column('passing_score', sa.Float(), nullable=False, server_default='70.0'),
        sa.Column('is_premium', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('question_ids', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_exams_id'), 'exams', ['id'], unique=False)

    # 2. Roadmaps table
    op.create_table(
        'roadmaps',
        sa.Column('id', sa.String(length=50), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('subtitle', sa.String(length=255), nullable=False),
        sa.Column('target_role', sa.String(length=100), nullable=False, server_default='Management Trainee'),
        sa.Column('duration_weeks', sa.Integer(), nullable=False, server_default='4'),
        sa.Column('phases', sa.JSON(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('display_order', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    # 3. Banners table
    op.create_table(
        'banners',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('badge_text', sa.String(length=50), nullable=False, server_default='HOT'),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('cta_text', sa.String(length=50), nullable=False, server_default='Khám phá ngay'),
        sa.Column('link_url', sa.String(length=255), nullable=False, server_default='#'),
        sa.Column('image_url', sa.String(length=500), nullable=True),
        sa.Column('bg_gradient', sa.String(length=255), nullable=False, server_default='linear-gradient(135deg, #5348CD, #F54899)'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('display_order', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_banners_id'), 'banners', ['id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_banners_id'), table_name='banners')
    op.drop_table('banners')
    op.drop_table('roadmaps')
    op.drop_index(op.f('ix_exams_id'), table_name='exams')
    op.drop_table('exams')
