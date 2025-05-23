"""Added ServiceRequest table

Revision ID: 8b6ff743230e
Revises: f4603b2a6905
Create Date: 2025-03-29 12:09:36.544320

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8b6ff743230e'
down_revision = 'f4603b2a6905'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('service_request',
    sa.Column('request_id', sa.Integer(), nullable=False),
    sa.Column('service_id', sa.Integer(), nullable=False),
    sa.Column('package_id', sa.Integer(), nullable=True),
    sa.Column('service_name', sa.String(length=100), nullable=False),
    sa.Column('package_name', sa.String(length=100), nullable=True),
    sa.Column('user_remark', sa.Text(), nullable=True),
    sa.Column('pincode', sa.String(length=10), nullable=False),
    sa.Column('request_time', sa.DateTime(), nullable=False),
    sa.Column('status', sa.String(length=20), nullable=False),
    sa.Column('professional_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['package_id'], ['package.id'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['professional_id'], ['professional.pid'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['service_id'], ['service.service_id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('request_id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('service_request')
    # ### end Alembic commands ###
