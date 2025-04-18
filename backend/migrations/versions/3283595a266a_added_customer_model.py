"""Added Customer model

Revision ID: 3283595a266a
Revises: af1378969e52
Create Date: 2025-03-28 19:59:19.969703

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3283595a266a'
down_revision = 'af1378969e52'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('customer',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('full_name', sa.String(length=100), nullable=False),
    sa.Column('email', sa.String(length=100), nullable=False),
    sa.Column('contact', sa.String(length=15), nullable=False),
    sa.Column('address', sa.Text(), nullable=False),
    sa.Column('pincode', sa.String(length=10), nullable=False),
    sa.ForeignKeyConstraint(['id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('customer')
    # ### end Alembic commands ###
