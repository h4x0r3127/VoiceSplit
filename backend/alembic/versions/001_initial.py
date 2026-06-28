"""Initial database schema — creates all Phase 1-3 tables.

Revision ID: 001_initial
Revises: —
Create Date: 2026-06-28
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ── ENUMS ──────────────────────────────────────────────────────────────
    auth_provider = postgresql.ENUM(
        "email", "google", name="auth_provider", create_type=False
    )
    auth_provider.create(op.get_bind(), checkfirst=True)

    job_status = postgresql.ENUM(
        "UPLOADED", "PREPROCESSING", "VAD", "DIARIZING", "EMBEDDING",
        "CLUSTERING", "SEPARATING", "TRANSCRIBING", "ANALYZING",
        "RECONSTRUCTING", "COMPLETED", "FAILED",
        name="job_status", create_type=False,
    )
    job_status.create(op.get_bind(), checkfirst=True)

    export_status = postgresql.ENUM(
        "PENDING", "PROCESSING", "COMPLETED", "FAILED",
        name="export_status", create_type=False,
    )
    export_status.create(op.get_bind(), checkfirst=True)

    export_format = postgresql.ENUM(
        "mp3", "wav", "flac", "txt", "json", "csv",
        name="export_format", create_type=False,
    )
    export_format.create(op.get_bind(), checkfirst=True)

    # ── USERS ──────────────────────────────────────────────────────────────
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("created_at", sa.DateTime(timezone=True),
                  server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True),
                  server_default=sa.text("now()"), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("email", sa.String(320), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("avatar_url", sa.String(2048), nullable=True),
        sa.Column("password_hash", sa.String(255), nullable=True),
        sa.Column("provider", sa.Enum("email", "google", name="auth_provider"),
                  nullable=False, server_default="email"),
        sa.Column("provider_id", sa.String(255), nullable=True),
        sa.Column("credits", sa.Integer(), nullable=False, server_default="300"),
        sa.Column("storage_used_bytes", sa.BigInteger(), nullable=False, server_default="0"),
        sa.Column("is_verified", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)
    op.create_index("ix_users_provider_id", "users", ["provider_id"])

    # ── JOBS ───────────────────────────────────────────────────────────────
    op.create_table(
        "jobs",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("created_at", sa.DateTime(timezone=True),
                  server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True),
                  server_default=sa.text("now()"), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("original_filename", sa.String(512), nullable=False),
        sa.Column("original_s3_key", sa.String(1024), nullable=False),
        sa.Column("processed_s3_key", sa.String(1024), nullable=True),
        sa.Column("status",
                  sa.Enum("UPLOADED", "PREPROCESSING", "VAD", "DIARIZING", "EMBEDDING",
                          "CLUSTERING", "SEPARATING", "TRANSCRIBING", "ANALYZING",
                          "RECONSTRUCTING", "COMPLETED", "FAILED", name="job_status"),
                  nullable=False, server_default="UPLOADED"),
        sa.Column("pipeline_stage", sa.String(64), nullable=True),
        sa.Column("progress", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("duration_seconds", sa.Float(), nullable=True),
        sa.Column("file_size_bytes", sa.BigInteger(), nullable=False, server_default="0"),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("audio_metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_jobs_user_id", "jobs", ["user_id"])
    op.create_index("ix_jobs_status", "jobs", ["status"])

    # ── SPEAKERS ───────────────────────────────────────────────────────────
    op.create_table(
        "speakers",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("created_at", sa.DateTime(timezone=True),
                  server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True),
                  server_default=sa.text("now()"), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("job_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("label", sa.String(128), nullable=False),
        sa.Column("color", sa.String(16), nullable=False, server_default="#06D6CF"),
        sa.Column("gender", sa.String(32), nullable=True),
        sa.Column("age_range", sa.String(32), nullable=True),
        sa.Column("language", sa.String(16), nullable=True),
        sa.Column("speaking_duration", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("confidence", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("emotion", sa.String(64), nullable=True),
        sa.Column("accent", sa.String(64), nullable=True),
        sa.Column("preview_s3_key", sa.String(1024), nullable=True),
        sa.Column("embedding", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("segments", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.ForeignKeyConstraint(["job_id"], ["jobs.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_speakers_job_id", "speakers", ["job_id"])

    # ── EXPORTS ────────────────────────────────────────────────────────────
    op.create_table(
        "exports",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("created_at", sa.DateTime(timezone=True),
                  server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True),
                  server_default=sa.text("now()"), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("job_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("selected_speaker_ids",
                  postgresql.JSONB(astext_type=sa.Text()), nullable=False,
                  server_default="[]"),
        sa.Column("output_format",
                  sa.Enum("mp3", "wav", "flac", "txt", "json", "csv",
                          name="export_format"),
                  nullable=False),
        sa.Column("output_s3_key", sa.String(1024), nullable=True),
        sa.Column("status",
                  sa.Enum("PENDING", "PROCESSING", "COMPLETED", "FAILED",
                          name="export_status"),
                  nullable=False, server_default="PENDING"),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["job_id"], ["jobs.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_exports_job_id", "exports", ["job_id"])
    op.create_index("ix_exports_user_id", "exports", ["user_id"])


def downgrade() -> None:
    op.drop_table("exports")
    op.drop_table("speakers")
    op.drop_table("jobs")
    op.drop_table("users")

    # Drop enums
    for enum_name in ("export_format", "export_status", "job_status", "auth_provider"):
        op.execute(f"DROP TYPE IF EXISTS {enum_name}")
