"""init

Revision ID: 96c0db5808e5
Revises: 
Create Date: 2020-02-17 17:47:11.297847

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '96c0db5808e5'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('customer_import_file',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=True),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_customer_import_file_name'), 'customer_import_file', ['name'], unique=False)
    op.create_index(op.f('ix_customer_import_file_timestamp'), 'customer_import_file', ['timestamp'], unique=False)
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=64), nullable=True),
    sa.Column('email', sa.String(length=120), nullable=True),
    sa.Column('password_hash', sa.String(length=128), nullable=True),
    sa.Column('token', sa.String(length=32), nullable=True),
    sa.Column('token_expiration', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_email'), 'user', ['email'], unique=True)
    op.create_index(op.f('ix_user_token'), 'user', ['token'], unique=True)
    op.create_index(op.f('ix_user_username'), 'user', ['username'], unique=True)
    op.create_table('customer',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('income', sa.Integer(), nullable=True),
    sa.Column('education', sa.Integer(), nullable=True),
    sa.Column('cc_avg', sa.Numeric(precision=10, scale=2), nullable=True),
    sa.Column('family', sa.Integer(), nullable=True),
    sa.Column('cd_account', sa.Boolean(), nullable=True),
    sa.Column('age', sa.Integer(), nullable=True),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.Column('import_file_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['import_file_id'], ['customer_import_file.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_customer_timestamp'), 'customer', ['timestamp'], unique=False)
    op.create_table('personal_loan_offer',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('customer_id', sa.Integer(), nullable=True),
    sa.Column('predicted_response', sa.String(length=15), nullable=True),
    sa.Column('prediction_probability', sa.Numeric(precision=10, scale=2), nullable=True),
    sa.Column('actual_response', sa.String(length=15), nullable=True),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['customer_id'], ['customer.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_personal_loan_offer_timestamp'), 'personal_loan_offer', ['timestamp'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_personal_loan_offer_timestamp'), table_name='personal_loan_offer')
    op.drop_table('personal_loan_offer')
    op.drop_index(op.f('ix_customer_timestamp'), table_name='customer')
    op.drop_table('customer')
    op.drop_index(op.f('ix_user_username'), table_name='user')
    op.drop_index(op.f('ix_user_token'), table_name='user')
    op.drop_index(op.f('ix_user_email'), table_name='user')
    op.drop_table('user')
    op.drop_index(op.f('ix_customer_import_file_timestamp'), table_name='customer_import_file')
    op.drop_index(op.f('ix_customer_import_file_name'), table_name='customer_import_file')
    op.drop_table('customer_import_file')
    # ### end Alembic commands ###