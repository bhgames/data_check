"""empty message

Revision ID: 7e1a254f7dd3
Revises: 32b1afcf724d
Create Date: 2017-01-05 11:56:50.112495

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7e1a254f7dd3'
down_revision = '32b1afcf724d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('job_template', sa.Column('ignore_system_failures', sa.Boolean()))
    op.execute('update "job_template" set ignore_system_failures = false')
    op.alter_column('job_template', 'ignore_system_failures', nullable=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('job_template', 'ignore_system_failures')
    # ### end Alembic commands ###
