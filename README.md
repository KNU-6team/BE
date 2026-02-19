설치

python -m venv .venv && source .venv/bin/activate

pip install -r requirements.txt

pip install cryptography (또는 requirements에 추가)

DB 준비

CREATE DATABASE boneage...

CREATE USER boneage_user...

마이그레이션

flask db upgrade

실행

python app.py 또는 flask run
