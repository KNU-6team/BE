import os, json, re
from datetime import datetime

BONE_KEYS = ["bone_age", "boneAge", "boneAgeYears", "bone_age_years", "boneage", "ba"]

def _extract_bone_age(text: str):
    # JSON 키 후보 탐색
    try:
        obj = json.loads(text)
        if isinstance(obj, dict):
            for k in BONE_KEYS:
                if k in obj:
                    return float(obj[k])
    except Exception:
        pass
    # 숫자 하나만 와도 임시 처리
    m = re.search(r"(-?\d+(\.\d+)?)", text)
    return float(m.group(1)) if m else None

def analyze_bone_age(mock: bool, analysis_id: str, image_bytes: bytes, meta: dict, ai_raw_dir: str):
    """
    반환: (bone_age_years: float, raw_path: str|None)
    """
    if mock:
        # 파일명/환자ID에 따라 재현 가능하게 만들고 싶으면 여기에서 규칙 추가
        return 10.0, None

    # ---- Real 모드(내부망에서만 테스트) ----
    # 아래는 "자리"만 만들어 둔 것. 실제 ws URL/프로토콜은 멘토/회사 규격 확인 후 채움.
    # 응답 포맷 모르면 raw 저장 후 _extract_bone_age()로 파싱.
    raise NotImplementedError("Real AI WebSocket integration is disabled in local dev. Use MOCK_AI=true.")
