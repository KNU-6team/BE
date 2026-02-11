import os
from flask import Flask
from dotenv import load_dotenv
from config import config
from models import db
from routes.analyses import bp
from flask_migrate import Migrate

migrate = Migrate()

def create_app():
    load_dotenv()
    app = Flask(__name__)
    app.config.from_object(config)

    os.makedirs(app.config["UPLOAD_DIR"], exist_ok=True)
    os.makedirs(app.config["AI_RAW_DIR"], exist_ok=True)

    #임시로 넣음
    print("DB URI =", app.config["SQLALCHEMY_DATABASE_URI"])

    @app.get("/")
    def health():
        return {"status": "ok", "team": "Silla System - 6Team"}

    db.init_app(app)
    migrate.init_app(app, db)
    
    app.register_blueprint(bp)
    return app

app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
