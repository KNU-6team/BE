import os

def mysql_uri():
    host = os.getenv("DB_HOST","127.0.0.1")
    port = os.getenv("DB_PORT","3306")
    name = os.getenv("DB_NAME","boneage")
    user = os.getenv("DB_USER","boneage_user")
    pw = os.getenv("DB_PASSWORD","1234")

    return f"mysql+pymysql://{user}:{pw}@{host}:{port}/{name}?charset=utf8mb4"

class config:
    MOCK_AI = os.getenv("MOCK_AI","True").lower() == "true"
    SQLALCHEMY_DATABASE_URI = mysql_uri()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_DIR = os.path.join("storage","uploads")
    AI_RAW_DIR = os.path.join("storage","ai_raw")
