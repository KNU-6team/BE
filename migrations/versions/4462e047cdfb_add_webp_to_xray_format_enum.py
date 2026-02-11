"""add WEBP to xray_format enum

Revision ID: 4462e047cdfb
Revises: 3f13c53a0bba
Create Date: 2026-02-11 11:20:12.117183

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4462e047cdfb'
down_revision = '3f13c53a0bba'
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        "ALTER TABLE analyses "
        "MODIFY xray_format ENUM('DICOM','JPG','PNG','WEBP') NOT NULL"
    )


def downgrade():
    op.execute(
        "ALTER TABLE analyses "
        "MODIFY xray_format ENUM('DICOM','JPG','PNG') NOT NULL"
    )