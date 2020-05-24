"""empty message

Revision ID: 8ecd1812124f
Revises: 3ce4dac0c27d
Create Date: 2020-05-23 17:24:57.946444

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '8ecd1812124f'
down_revision = '3ce4dac0c27d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('teachers')
    op.drop_table('bookings')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('bookings',
    sa.Column('booking_id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('week_day', sa.VARCHAR(length=15), autoincrement=False, nullable=True),
    sa.Column('lesson_time', sa.VARCHAR(length=10), autoincrement=False, nullable=True),
    sa.Column('client_name', sa.VARCHAR(length=50), autoincrement=False, nullable=True),
    sa.Column('client_phone', sa.VARCHAR(length=20), autoincrement=False, nullable=True),
    sa.Column('booking_ditails', sa.VARCHAR(length=230), autoincrement=False, nullable=False),
    sa.PrimaryKeyConstraint('booking_id', name='bookings_pkey')
    )
    op.create_table('teachers',
    sa.Column('teacher_id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('teacher_name', sa.VARCHAR(length=150), autoincrement=False, nullable=False),
    sa.Column('rating', postgresql.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=False),
    sa.Column('price', postgresql.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=False),
    sa.Column('picture', sa.VARCHAR(length=200), autoincrement=False, nullable=True),
    sa.Column('schedule', postgresql.JSON(astext_type=sa.Text()), autoincrement=False, nullable=True),
    sa.Column('about', sa.TEXT(), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('teacher_id', name='teachers_pkey')
    )
    # ### end Alembic commands ###