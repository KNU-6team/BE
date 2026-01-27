from datetime import date

def calc_chronological_age_years(birth_date: date, study_date: date) -> float:
    days = (study_date - birth_date).days
    return round(days / 365.25, 2)

def label_from_delta(delta_years: float) -> str:
    # 팀 기준(예시): ±1.0년 이내 정상
    if delta_years > 1.0:
        return "Slightly Advanced"
    if delta_years < -1.0:
        return "Slightly Delayed"
    return "Within Normal Range"

def message_for_guardian(label: str) -> str:
    if label == "Within Normal Range":
        return "현재 골연령은 생활연령과 비슷한 범위로 관찰됩니다. 정기적인 추적 관찰을 권장합니다."
    if label == "Slightly Delayed":
        return "현재 골연령이 생활연령보다 낮게 관찰됩니다. 단일 결과만으로 단정하기 어렵기 때문에 추적 관찰을 권장합니다."
    return "현재 골연령이 생활연령보다 높게 관찰됩니다. 성장 속도 변화가 있을 수 있어 정기 확인을 권장합니다."
