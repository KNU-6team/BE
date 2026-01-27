from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

def build_pdf(path: str, team_name: str, report: dict):
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="T", fontSize=18, leading=22, alignment=1, spaceAfter=10))
    styles.add(ParagraphStyle(name="H", fontSize=13, leading=16, textColor=colors.HexColor("#2A6F97"), spaceBefore=10))
    styles.add(ParagraphStyle(name="B", fontSize=10.5, leading=15))

    doc = SimpleDocTemplate(path, pagesize=A4, leftMargin=36, rightMargin=36, topMargin=36, bottomMargin=36)
    el = []

    el.append(Paragraph("AI Bone Age & Growth Report", styles["T"]))
    el.append(Paragraph(f"<b>{team_name}</b>", styles["B"]))
    el.append(Spacer(1, 10))

    summary = [
        ["Patient ID", report["patient_id"]],
        ["Sex", report["sex"]],
        ["Birth Date", report["birth_date"]],
        ["Study Date", report["study_date"]],
        ["Bone Age (AI)", f'{report["bone_age_years"]} years'],
        ["Chronological Age", f'{report["chronological_age_years"]} years'],
        ["Delta (BA-CA)", f'{report["delta_years"]} years'],
        ["Status", report["status_label"]],
    ]
    t = Table(summary, colWidths=[150, 340])
    t.setStyle(TableStyle([
        ("BOX",(0,0),(-1,-1),0.6,colors.grey),
        ("INNERGRID",(0,0),(-1,-1),0.25,colors.lightgrey),
        ("BACKGROUND",(0,0),(-1,0),colors.whitesmoke),
        ("VALIGN",(0,0),(-1,-1),"MIDDLE"),
    ]))
    el.append(t)
    el.append(Spacer(1, 12))

    el.append(Paragraph("Guardian-friendly Interpretation", styles["H"]))
    el.append(Paragraph(report["message"], styles["B"]))
    el.append(Spacer(1, 10))

    el.append(Paragraph("Important Notes", styles["H"]))
    el.append(Paragraph(
        "This report is a supportive reference based on AI analysis and does not replace medical diagnosis. "
        "Final clinical decisions should be made by healthcare professionals.",
        styles["B"]
    ))

    doc.build(el)
