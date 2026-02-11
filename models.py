from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import Enum

db = SQLAlchemy()

class Patient(db.Model):
    __tablename__ = "patients"
    id = db.Column(db.String(64), primary_key=True)
    name = db.Column(db.String(64), nullable=True)
    sex = db.Column(Enum("M", "F", name="sex_enum"), nullable=False)
    birth_date = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

class Analysis(db.Model):
    __tablename__ = "analyses"
    id = db.Column(db.String(64), primary_key=True)
    patient_id = db.Column(db.String(64), db.ForeignKey("patients.id"), nullable=False)
    study_date = db.Column(db.Date, nullable=False)

    xray_path = db.Column(db.String(255), nullable=False)
    # ✅ WEBP 추가
    xray_format = db.Column(
        Enum("DICOM", "JPG", "PNG", "WEBP", name="xray_format_enum"),
        nullable=False
    )

    status = db.Column(
        Enum("QUEUED", "RUNNING", "DONE", "FAILED", name="status_enum"),
        nullable=False,
        default="QUEUED"
    )
    bone_age_years = db.Column(db.Numeric(4, 1), nullable=True)

    ai_raw_path = db.Column(db.String(255), nullable=True)
    error_message = db.Column(db.Text, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
