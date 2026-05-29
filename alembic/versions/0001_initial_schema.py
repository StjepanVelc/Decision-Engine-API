"""initial schema

Revision ID: 0001_initial_schema
Revises: 
Create Date: 2026-05-29 00:00:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "0001_initial_schema"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "rules",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("field", sa.String(length=100), nullable=True),
        sa.Column("operator", sa.String(length=20), nullable=True),
        sa.Column("value", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("expression", sa.Text(), nullable=True),
        sa.Column("weight", sa.Integer(), nullable=False, server_default="10"),
        sa.Column("hard_stop", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("action", sa.String(length=20), nullable=False, server_default="REJECT"),
        sa.Column("priority", sa.Float(), nullable=False, server_default="0"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("category", sa.String(length=50), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint(
            "operator IS NULL OR operator IN ('gt','lt','gte','lte','eq','neq','in','not_in','contains','not_contains')",
            name="ck_rules_operator",
        ),
        sa.CheckConstraint("action IN ('APPROVE','REVIEW','REJECT')", name="ck_rules_action"),
        sa.CheckConstraint("priority >= 0", name="ck_rules_priority_positive"),
        sa.CheckConstraint("weight >= 0", name="ck_rules_weight_positive"),
        sa.CheckConstraint(
            "expression IS NOT NULL OR (field IS NOT NULL AND operator IS NOT NULL AND value IS NOT NULL)",
            name="ck_rules_expression_or_legacy",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )

    op.create_table(
        "decisions",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("payload", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("outcome", sa.String(length=20), nullable=False),
        sa.Column("triggered_rules", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("reasons", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("rules_evaluated", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("risk_score", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("normalized_score", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("reference_id", sa.String(length=100), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_decisions_reference_id"), "decisions", ["reference_id"], unique=False)

    op.create_table(
        "audit_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("event_type", sa.String(length=50), nullable=False),
        sa.Column("entity_type", sa.String(length=50), nullable=False),
        sa.Column("entity_id", sa.String(length=100), nullable=False),
        sa.Column("details", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_audit_logs_created_at"), "audit_logs", ["created_at"], unique=False)
    op.create_index(op.f("ix_audit_logs_entity_id"), "audit_logs", ["entity_id"], unique=False)
    op.create_index(op.f("ix_audit_logs_event_type"), "audit_logs", ["event_type"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_audit_logs_event_type"), table_name="audit_logs")
    op.drop_index(op.f("ix_audit_logs_entity_id"), table_name="audit_logs")
    op.drop_index(op.f("ix_audit_logs_created_at"), table_name="audit_logs")
    op.drop_table("audit_logs")

    op.drop_index(op.f("ix_decisions_reference_id"), table_name="decisions")
    op.drop_table("decisions")

    op.drop_table("rules")
