"""change_role_to_enum

Revision ID: 2c3b8338be77
Revises: b383cf84434f
Create Date: 2025-12-08 21:52:11.162675

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '2c3b8338be77'
down_revision = 'b383cf84434f'
branch_labels = None
depends_on = None

def upgrade():
    userrole_enum = postgresql.ENUM('USER', 'ADMIN', name='userrole')
    userrole_enum.create(op.get_bind(), checkfirst=True)
    
    op.execute("ALTER TABLE users ALTER COLUMN role TYPE userrole USING role::userrole")

def downgrade():
    op.alter_column('users', 'role',
                    existing_type=sa.Enum('USER', 'ADMIN', name='userrole'),
                    type_=sa.String(),
                    nullable=True)
    op.execute("DROP TYPE IF EXISTS userrole")
