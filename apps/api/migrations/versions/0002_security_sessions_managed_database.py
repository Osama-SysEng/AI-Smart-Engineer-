"""Add revocable sessions, tenant-aware roles, and operational indexes.

Revision ID: 0002
Revises: 0001
"""
from alembic import op
import sqlalchemy as sa


revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    role_constraints = inspector.get_unique_constraints("roles")
    for constraint in role_constraints:
        if constraint.get("column_names") == ["name"] and constraint.get("name"):
            op.drop_constraint(constraint["name"], "roles", type_="unique")

    op.add_column("roles", sa.Column("tenant_id", sa.String(length=36), nullable=True))
    op.add_column("roles", sa.Column("is_system", sa.Boolean(), nullable=False, server_default=sa.text("false")))
    op.create_index("ix_roles_tenant_id", "roles", ["tenant_id"])
    op.create_unique_constraint("uq_roles_tenant_name", "roles", ["tenant_id", "name"])

    op.create_table(
        "auth_sessions",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("user_id", sa.String(length=36), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("tenant_id", sa.String(length=36), nullable=False),
        sa.Column("refresh_jti", sa.String(length=64), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("revoke_reason", sa.String(length=100), nullable=True),
        sa.Column("ip_address", sa.String(length=64), nullable=True),
        sa.Column("user_agent", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("refresh_jti", name="uq_auth_sessions_refresh_jti"),
    )
    op.create_index("ix_auth_sessions_user_id", "auth_sessions", ["user_id"])
    op.create_index("ix_auth_sessions_tenant_id", "auth_sessions", ["tenant_id"])
    op.create_index("ix_auth_sessions_expires_at", "auth_sessions", ["expires_at"])
    op.create_index("ix_auth_sessions_active", "auth_sessions", ["user_id", "revoked_at", "expires_at"])
    op.create_index("ix_audit_logs_security_timeline", "audit_logs", ["resource_type", "action", "created_at"])


def downgrade() -> None:
    op.drop_index("ix_audit_logs_security_timeline", table_name="audit_logs")
    op.drop_index("ix_auth_sessions_active", table_name="auth_sessions")
    op.drop_index("ix_auth_sessions_expires_at", table_name="auth_sessions")
    op.drop_index("ix_auth_sessions_tenant_id", table_name="auth_sessions")
    op.drop_index("ix_auth_sessions_user_id", table_name="auth_sessions")
    op.drop_table("auth_sessions")
    op.drop_constraint("uq_roles_tenant_name", "roles", type_="unique")
    op.drop_index("ix_roles_tenant_id", table_name="roles")
    op.drop_column("roles", "is_system")
    op.drop_column("roles", "tenant_id")
