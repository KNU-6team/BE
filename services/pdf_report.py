import os

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


def _register_korean_fonts():
    """
    ReportLab TTFont는 TrueType(TTF) 계열이 가장 안정적이다.
    TTC/일부 OTF(CFF outline)는 'postscript outlines not supported'로 실패할 수 있어
    TTF 위주로만 등록한다.
    """
    if "KOR" in pdfmetrics.getRegisteredFontNames():
        return

    # ✅ TTF 우선 후보 (가장 안정)
    candidates = [
        # Nanum (TTF) - Ubuntu에서 매우 안정적
        ("/usr/share/fonts/truetype/nanum/NanumGothic.ttf",
         "/usr/share/fonts/truetype/nanum/NanumGothicBold.ttf"),
        ("/usr/share/fonts/truetype/nanum/NanumBarunGothic.ttf",
         "/usr/share/fonts/truetype/nanum/NanumBarunGothicBold.ttf"),

        # NotoSansKR (TTF) - 설치돼 있으면 사용
        ("/usr/share/fonts/truetype/noto/NotoSansKR-Regular.ttf",
         "/usr/share/fonts/truetype/noto/NotoSansKR-Bold.ttf"),
    ]

    reg_path = None
    bold_path = None

    for r, b in candidates:
        if os.path.exists(r):
            reg_path = r
            bold_path = b if os.path.exists(b) else None
            break

    if not reg_path:
        raise RuntimeError(
            "Korean TTF font not found.\n"
            "추천 해결:\n"
            "  sudo apt install fonts-nanum\n"
            "그리고 경로를 확인:\n"
            "  fc-list | grep -i NanumGothic | head\n"
        )

    pdfmetrics.registerFont(TTFont("KOR", reg_path))
    pdfmetrics.registerFont(TTFont("KOR-B", bold_path or reg_path))

def build_pdf(path: str, team_name: str, report: dict):
    # ✅ 한글 폰트 등록
    _register_korean_fonts()

    styles = getSampleStyleSheet()

    # ✅ fontName을 KOR / KOR-B로 지정해서 한글 출력 보장
    styles.add(ParagraphStyle(
        name="T",
        fontName="KOR-B",
        fontSize=18,
        leading=22,
        alignment=1,
        spaceAfter=10
    ))
    styles.add(ParagraphStyle(
        name="H",
        fontName="KOR-B",
        fontSize=13,
        leading=16,
        textColor=colors.HexColor("#2A6F97"),
        spaceBefore=10
    ))
    styles.add(ParagraphStyle(
        name="B",
        fontName="KOR",
        fontSize=10.5,
        leading=15
    ))

    doc = SimpleDocTemplate(
        path,
        pagesize=A4,
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=36
    )
    el = []

    el.append(Paragraph("AI Bone Age & Growth Report", styles["T"]))
    # Paragraph에서 <b> 태그 대신 Bold 폰트 스타일 쓰는 게 더 안정적
    el.append(Paragraph(team_name, styles["B"]))
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
        ("FONTNAME", (0, 0), (-1, -1), "KOR"),  # ✅ 테이블도 한글 가능하게
        ("BOX", (0, 0), (-1, -1), 0.6, colors.grey),
        ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.lightgrey),
        ("BACKGROUND", (0, 0), (-1, 0), colors.whitesmoke),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
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
