"""Create users, expenses and budgets."""
from alembic import op
import sqlalchemy as sa
revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.create_table('users', sa.Column('id',sa.Integer(),primary_key=True),sa.Column('name',sa.String(100),nullable=False),sa.Column('email',sa.String(255),nullable=False),sa.Column('hashed_password',sa.String(255),nullable=False),sa.Column('created_at',sa.DateTime(),nullable=False),sa.UniqueConstraint('email'))
    op.create_index('ix_users_id','users',['id']); op.create_index('ix_users_email','users',['email'],unique=True)
    op.create_table('expenses',sa.Column('id',sa.Integer(),primary_key=True),sa.Column('title',sa.String(140),nullable=False),sa.Column('amount',sa.Float(),nullable=False),sa.Column('category',sa.String(60),nullable=False),sa.Column('transaction_type',sa.String(20),nullable=False),sa.Column('spent_on',sa.Date(),nullable=False),sa.Column('description',sa.Text()),sa.Column('user_id',sa.Integer(),sa.ForeignKey('users.id',ondelete='CASCADE'),nullable=False),sa.Column('created_at',sa.DateTime(),nullable=False))
    op.create_index('ix_expenses_id','expenses',['id']); op.create_index('ix_expenses_user_id','expenses',['user_id'])
    op.create_table('budgets',sa.Column('id',sa.Integer(),primary_key=True),sa.Column('month',sa.String(7),nullable=False),sa.Column('category',sa.String(60),nullable=False),sa.Column('limit_amount',sa.Float(),nullable=False),sa.Column('user_id',sa.Integer(),sa.ForeignKey('users.id',ondelete='CASCADE'),nullable=False),sa.UniqueConstraint('user_id','month','category',name='uq_user_budget_month_category'))
    op.create_index('ix_budgets_month','budgets',['month']); op.create_index('ix_budgets_user_id','budgets',['user_id'])
def downgrade():
    op.drop_table('budgets'); op.drop_table('expenses'); op.drop_table('users')
