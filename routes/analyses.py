# routes/analyses.py
import os
import uuid
import json
from datetime import datetime

from flask import Blueprint, request, jsonify, send_file, current_app
from models import db, Patient, Analysis
from services.ai_client import analyze_bone_age
from services.derived import calc_chronological_age_years, label_from_delta, message_for_guardian
from services.pdf_report import build_pdf

bp = Blueprint("analyses", __name__)

def _detect_format(filename: str) -> str:
    ext = (filename or "").lower().rsplit(".", 1)[-1]
    if ext == "dcm":
        return "DICOM"
    if ext in ("jpg", "jpeg"):
        return "JPG"
    if ext == "png":
        return "PNG"
    if ext == "webp":
        return "WEBP"   # ✅ webp 업로드 대비 (models enum도 WEBP 허용 필요)
    return "JPG"

def _safe_ext(filename: str) -> str:
    """저장용 확장자. 확장자가 없거나 이상하면 jpg로."""
    if not filename or "." not in filename:
        return "jpg"
    ext = filename.rsplit(".", 1)[-1].lower()
    # 너무 이상한 확장자 방지
    if ext not in ("jpg", "jpeg", "png", "webp", "dcm"):
        return "jpg"
    return ext

@bp.post("/api/v1/analyses")
def create_analysis():
    # 0) 입력 받기 (가장 먼저 정의)
    xray = request.files.get("xray")
    patient_json = request.form.get("patient")

    if not xray or not patient_json:
        return jsonify({"error": "xray(file) and patient(text json) are required"}), 400

    try:
        patient = json.loads(patient_json)
    except Exception:
        return jsonify({"error": "patient must be valid JSON string"}), 400

    # 필수 필드 체크
    for k in ("patient_id", "sex", "birth_date"):
        if k not in patient:
            return jsonify({"error": f"patient.{k} is required"}), 400

    patient_id = str(patient["patient_id"])
    sex = str(patient["sex"]).upper()  # "M" / "F"
    if sex not in ("M", "F"):
        return jsonify({"error": "patient.sex must be 'M' or 'F'"}), 400

    try:
        birth_date = datetime.strptime(patient["birth_date"], "%Y-%m-%d").date()
    except ValueError:
        return jsonify({"error": "patient.birth_date must be YYYY-MM-DD"}), 400

    # study_date는 없으면 오늘로
    study_date_str = patient.get("study_date", datetime.now().strftime("%Y-%m-%d"))
    try:
        study_date = datetime.strptime(study_date_str, "%Y-%m-%d").date()
    except ValueError:
        return jsonify({"error": "patient.study_date must be YYYY-MM-DD"}), 400

    # 1) analysis_id 생성
    analysis_id = "A-" + uuid.uuid4().hex[:12]

    # 2) 파일 저장 경로 생성 + 저장
    os.makedirs(current_app.config["UPLOAD_DIR"], exist_ok=True)
    ext = _safe_ext(xray.filename)
    save_path = os.path.join(current_app.config["UPLOAD_DIR"], f"{analysis_id}.{ext}")
    xray.save(save_path)

    # 3) patient upsert (FK 만족 위해 flush)
    p = Patient.query.get(patient_id)
    if not p:
        p = Patient(id=patient_id, sex=sex, birth_date=birth_date)
        db.session.add(p)
        db.session.flush()  # ✅ analyses FK 오류 방지

    # 4) Analysis row 생성 (save_path 확정 후)
    fmt = _detect_format(xray.filename)

    a = Analysis(
        id=analysis_id,
        patient_id=patient_id,
        study_date=study_date,
        xray_path=save_path,
        xray_format=fmt,
        status="RUNNING",
        bone_age_years=None,
        ai_raw_path=None,
        error_message=None,
    )
    db.session.add(a)
    db.session.commit()

    # 5) AI analyze (Mock/Real 스위치)
    try:
        with open(save_path, "rb") as f:
            img_bytes = f.read()

        bone_age, raw_path = analyze_bone_age(
            mock=current_app.config["MOCK_AI"],
            analysis_id=analysis_id,
            image_bytes=img_bytes,
            meta={
                "patient_id": patient_id,
                "sex": sex,
                "birth_date": str(birth_date),
                "study_date": str(study_date),
                "xray_format": fmt,
            },
            ai_raw_dir=current_app.config["AI_RAW_DIR"],
        )

        a.status = "DONE"
        a.bone_age_years = bone_age
        a.ai_raw_path = raw_path
        a.error_message = None
        db.session.commit()

        return jsonify({"analysis_id": analysis_id, "status": a.status, "bone_age_years": float(bone_age)})

    except Exception as e:
        # AI 실패해도 row는 남겨서 조회 가능하게
        a.status = "FAILED"
        a.error_message = str(e)
        db.session.commit()
        return jsonify({"analysis_id": analysis_id, "status": a.status, "error": a.error_message}), 500


@bp.get("/api/v1/analyses/<analysis_id>")
def get_analysis(analysis_id):
    a = Analysis.query.get_or_404(analysis_id)
    p = Patient.query.get(a.patient_id)

    if a.status != "DONE" or a.bone_age_years is None:
        return jsonify({"analysis_id": a.id, "status": a.status, "error": a.error_message})

    ca = calc_chronological_age_years(p.birth_date, a.study_date)
    delta = round(float(a.bone_age_years) - ca, 2)
    label = label_from_delta(delta)
    msg = message_for_guardian(label)

    return jsonify({
        "analysis_id": a.id,
        "status": a.status,
        "ai_result": {"bone_age_years": float(a.bone_age_years)},
        "derived": {
            "chronological_age_years": ca,
            "delta_years": delta,
            "status_label": label,
            "message": msg
        },
        "input": {
            "patient_id": p.id,
            "sex": p.sex,
            "birth_date": str(p.birth_date),
            "study_date": str(a.study_date),
            "xray_format": a.xray_format,
            "xray_path": a.xray_path
        }
    })


@bp.get("/api/v1/analyses/<analysis_id>/report.pdf")
def download_pdf(analysis_id):
    a = Analysis.query.get_or_404(analysis_id)
    p = Patient.query.get(a.patient_id)

    if a.status != "DONE" or a.bone_age_years is None:
        return jsonify({"error": "analysis not completed", "status": a.status, "detail": a.error_message}), 409

    ca = calc_chronological_age_years(p.birth_date, a.study_date)
    delta = round(float(a.bone_age_years) - ca, 2)
    label = label_from_delta(delta)
    msg = message_for_guardian(label)

    report = {
        "patient_id": p.id,
        "sex": p.sex,
        "birth_date": str(p.birth_date),
        "study_date": str(a.study_date),
        "bone_age_years": float(a.bone_age_years),
        "chronological_age_years": ca,
        "delta_years": delta,
        "status_label": label,
        "message": msg
    }

    os.makedirs("storage", exist_ok=True)
    out_path = os.path.join("storage", f"{analysis_id}_report.pdf")
    build_pdf(out_path, team_name="Silla System - 6Team", report=report)
    return send_file(out_path, as_attachment=True, download_name=f"{analysis_id}_report.pdf")
