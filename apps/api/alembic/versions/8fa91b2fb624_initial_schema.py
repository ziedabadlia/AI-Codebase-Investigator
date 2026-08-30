"""initial_schema

Revision ID: 8fa91b2fb624
Revises: 
Create Date: 2026-08-30 22:02:19.715207

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8fa91b2fb624'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

import pgvector.sqlalchemy

def upgrade() -> None:
    # Ensure vector extension is installed
    op.execute('CREATE EXTENSION IF NOT EXISTS vector')
    
    op.create_table('repositories',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('url', sa.String(), nullable=False),
        sa.Column('owner', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('default_branch', sa.String(), nullable=False),
        sa.Column('commit_sha', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_repositories_url'), 'repositories', ['url'], unique=True)
    
    op.create_table('repository_files',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('repository_id', sa.UUID(), nullable=False),
        sa.Column('file_path', sa.String(), nullable=False),
        sa.Column('language', sa.String(), nullable=True),
        sa.Column('content', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['repository_id'], ['repositories.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('repository_id', 'file_path', name='uix_repository_file_path')
    )
    op.create_index(op.f('ix_repository_files_file_path'), 'repository_files', ['file_path'], unique=False)
    
    op.create_table('code_chunks',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('file_id', sa.UUID(), nullable=False),
        sa.Column('start_line', sa.Integer(), nullable=False),
        sa.Column('end_line', sa.Integer(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('embedding', pgvector.sqlalchemy.Vector(dim=384), nullable=True),
        sa.ForeignKeyConstraint(['file_id'], ['repository_files.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

def downgrade() -> None:
    op.drop_table('code_chunks')
    op.drop_index(op.f('ix_repository_files_file_path'), table_name='repository_files')
    op.drop_table('repository_files')
    op.drop_index(op.f('ix_repositories_url'), table_name='repositories')
    op.drop_table('repositories')

