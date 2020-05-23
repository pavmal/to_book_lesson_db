"""empty message

Revision ID: 686d5bfdd54a
Revises: 
Create Date: 2020-05-23 10:06:31.851726

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '686d5bfdd54a'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('goals',
    sa.Column('goal_id', sa.Integer(), nullable=False),
    sa.Column('goal_name', sa.String(length=35), nullable=False),
    sa.PrimaryKeyConstraint('goal_id'),
    sa.UniqueConstraint('goal_name')
    )
    op.create_table('teachers',
    sa.Column('teacher_id', sa.Integer(), nullable=False),
    sa.Column('teacher_name', sa.String(length=150), nullable=False),
    sa.Column('rating', sa.Float(), nullable=False),
    sa.Column('price', sa.Float(), nullable=False),
    sa.Column('picture', sa.String(length=200), nullable=True),
    sa.Column('schedule', postgresql.JSON(astext_type=sa.Text()), nullable=True),
    sa.Column('about', sa.Text(), nullable=True),
    sa.PrimaryKeyConstraint('teacher_id')
    )
    op.create_table('bookings',
    sa.Column('booking_id', sa.Integer(), nullable=False),
    sa.Column('teacher_id', sa.Integer(), nullable=True),
    sa.Column('week_day', sa.String(length=15), nullable=True),
    sa.Column('lesson_time', sa.String(length=10), nullable=True),
    sa.Column('client_name', sa.String(length=50), nullable=True),
    sa.Column('client_phone', sa.String(length=20), nullable=True),
    sa.ForeignKeyConstraint(['teacher_id'], ['teachers.teacher_id'], ),
    sa.PrimaryKeyConstraint('booking_id')
    )
    op.create_table('reqforms',
    sa.Column('reqform_id', sa.Integer(), nullable=False),
    sa.Column('goal_id', sa.Integer(), nullable=True),
    sa.Column('learning_time', sa.String(length=25), nullable=True),
    sa.Column('client_name', sa.String(length=50), nullable=True),
    sa.Column('client_phone', sa.String(length=20), nullable=True),
    sa.ForeignKeyConstraint(['goal_id'], ['goals.goal_id'], ),
    sa.PrimaryKeyConstraint('reqform_id')
    )
    op.create_table('teachers_goals',
    sa.Column('teacher_id', sa.Integer(), nullable=True),
    sa.Column('goal_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['goal_id'], ['goals.goal_id'], ),
    sa.ForeignKeyConstraint(['teacher_id'], ['teachers.teacher_id'], )
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('teachers_goals')
    op.drop_table('reqforms')
    op.drop_table('bookings')
    op.drop_table('teachers')
    op.drop_table('goals')
    # ### end Alembic commands ###
