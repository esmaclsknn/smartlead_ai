import os

from flask import Flask, jsonify
from flask_cors import CORS
from werkzeug.exceptions import HTTPException

from config import config_by_name
from app.database import init_db
from app.services.ai_service import ai_service


def create_app(config_name=None):
    """Ayarları, veritabanını ve sayfaları bir araya getirir."""
    ortam = config_name or os.environ.get("APP_ENV", "development")

    if ortam not in config_by_name:
        raise ValueError("Geçersiz uygulama ortamı.")

    app = Flask(__name__)
    app.config.from_object(config_by_name[ortam])
    app.json.ensure_ascii = False

    # Yayında gerekli yönetici ayarları eksikse başlamaz.
    #if ortam == "production":
    #    gerekli_ayarlar = (
    #        "SECRET_KEY",
    #        "ADMIN_USERNAME",
    #        "ADMIN_PASSWORD_HASH",
    #    )

    #    for ayar in gerekli_ayarlar:
    #        if not app.config.get(ayar):
    #            raise RuntimeError(f"Eksik uygulama ayarı: {ayar}")

    CORS(
        app,
        resources={
            r"/api/*": {
                "origins": app.config["CORS_ORIGINS"],
            }
        },
    )

    init_db(app)
    ai_service.yapilandir(app.config)

    from app.routes import api, pages

    app.register_blueprint(pages)
    app.register_blueprint(api)

    @app.errorhandler(HTTPException)
    def http_hatasi(hata):
        mesajlar = {
            400: "İstek okunamadı.",
            404: "Sayfa veya işlem bulunamadı.",
            405: "Bu istek yöntemi desteklenmiyor.",
            413: "Gönderilen içerik çok büyük.",
        }

        yanit = hata.get_response()
        yanit.data = app.json.dumps({
            "basari": False,
            "hata": mesajlar.get(hata.code, "İstek tamamlanamadı."),
        })
        yanit.content_type = "application/json"
        yanit.headers["Cache-Control"] = "no-store"
        return yanit

    @app.errorhandler(500)
    def sunucu_hatasi(hata):
        yanit = jsonify(
            basari=False,
            hata="Beklenmeyen bir hata oluştu. Lütfen tekrar deneyin.",
        )
        yanit.status_code = 500
        yanit.headers["Cache-Control"] = "no-store"
        return yanit

    return app
