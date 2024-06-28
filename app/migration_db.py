from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "your_revision_id"
down_revision = "previous_revision_id"
branch_labels = None
depends_on = None


def upgrade():
    # Add the new column with a default value
    op.add_column(
        "cvs",
        sa.Column(
            "default_cv", sa.Boolean(), nullable=False, server_default=sa.false()
        ),
    )
    # Remove the server_default now that the column is populated
    op.alter_column("cvs", "default_cv", server_default=None)


def downgrade():
    op.drop_column("cvs", "default_cv")
