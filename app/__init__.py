
import os

from flask import Flask, jsonify
from flask_cors import CORS
from werkzeug.exceptions import HTTPException

from config import config_by_name
from app.database import init_db
from app.services.ai_service import ai_service


def create_app(config_name=None):
    """
    Ilmeva Flask uygulamasını oluşturur.
    Veritabanını, chatbotu ve API bağlantılarını başlatır.
    """

    ortam = config_name or os.environ.get(
        "APP_ENV",
        "development"
    )

    if ortam not in config_by_name:
        raise ValueError("Geçersiz uygulama ortamı.")

    app = Flask(__name__)

    app.config.from_object(
        config_by_name[ortam]
    )

    app.json.ensure_ascii = False

    # CORS AYARLARI
    # Wix ve diğer izin verilen frontend bağlantıları

    CORS(app)

    # VERİTABANI

    init_db(app)

    # YAPAY ZEKA SERVİSİ

    ai_service.yapilandir(app.config)

    # SAYFA VE API BAĞLANTILARI

    from app.routes import api, pages

    app.register_blueprint(pages)
    app.register_blueprint(api)

    # BAĞLANTI TESTİ
    # Müşteri verisi döndürmez.

    @app.route("/api/baglanti-test", methods=["GET"])
    def baglanti_test():

        return jsonify(
            basari=True,
            uygulama="Ilmeva",
            durum="aktif",
            api="calisiyor"
        ), 200

    # HTTP HATALARI

    @app.errorhandler(HTTPException)
    def http_hatasi(hata):

        mesajlar = {
            400: "İstek okunamadı.",
            401: "Yetkisiz erişim.",
            403: "Erişim reddedildi.",
            404: "Sayfa veya işlem bulunamadı.",
            405: "Bu istek yöntemi desteklenmiyor.",
            413: "Gönderilen içerik çok büyük."
        }

        yanit = hata.get_response()

        yanit.data = app.json.dumps({
            "basari": False,
            "hata": mesajlar.get(
                hata.code,
                "İstek tamamlanamadı."
            )
        })

        yanit.content_type = "application/json"

        yanit.headers["Cache-Control"] = "no-store"

        return yanit

    # SUNUCU HATALARI

    @app.errorhandler(500)
    def sunucu_hatasi(hata):

        app.logger.error(
            "Ilmeva sunucu hatası: %s",
            hata
        )

        yanit = jsonify(
            basari=False,
            hata="Beklenmeyen bir sunucu hatası oluştu."
        )

        yanit.status_code = 500

        yanit.headers["Cache-Control"] = "no-store"

        return yanit

    return app
