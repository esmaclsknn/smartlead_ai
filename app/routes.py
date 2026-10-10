import re
import sqlite3
from functools import wraps
from hmac import compare_digest

from flask import (
    Blueprint,
    current_app,
    jsonify,
    render_template,
    request,
)
from werkzeug.security import check_password_hash

from app.database import lead_ekle, tum_leadler
from app.services.ai_service import ai_service, AIServiceError


pages = Blueprint("pages", __name__)
api = Blueprint("api", __name__, url_prefix="/api")


def hata_yaniti(mesaj, durum):
    """Hataları tutarlı bir JSON biçiminde döndürür."""
    return jsonify(basari=False, hata=mesaj), durum


def yonetici_gerekli(fonksiyon):
    """Dashboard ve müşteri listesini yönetici girişiyle korur."""
    @wraps(fonksiyon)
    def kontrol(*args, **kwargs):
        kullanici = current_app.config.get("ADMIN_USERNAME", "")
        parola_ozeti = current_app.config.get("ADMIN_PASSWORD_HASH", "")

        # Ayarlar eksikse müşteri kayıtlarını erişime açmaz.
        if not kullanici or not parola_ozeti:
            return hata_yaniti("Yönetici erişimi henüz hazırlanmadı.", 503)

        kimlik = request.authorization

        gecerli = (
            kimlik is not None
            and kimlik.type.lower() == "basic"
            and compare_digest(
                (kimlik.username or "").encode("utf-8"),
                kullanici.encode("utf-8"),
            )
            and check_password_hash(
                parola_ozeti,
                kimlik.password or "",
            )
        )

        if not gecerli:
            yanit = jsonify(
                basari=False,
                hata="Bu alan için yönetici girişi gerekiyor.",
            )
            yanit.status_code = 401
            yanit.headers["WWW-Authenticate"] = 'Basic realm="Ilmeva"'
            yanit.headers["Cache-Control"] = "no-store"
            return yanit

        return fonksiyon(*args, **kwargs)

    return kontrol


@pages.route("/", methods=["GET"])
def ana_sayfa():
    return render_template("index.html")


@pages.route("/dashboard", methods=["GET"])
@yonetici_gerekli
def dashboard():
    return render_template("dashboard.html")


@pages.route("/health", methods=["GET"])
def health():
    return jsonify(basari=True, durum="calisiyor")


@api.route("/sohbet", methods=["POST"])
def sohbet():
    veri = request.get_json(silent=True)

    if not isinstance(veri, dict):
        return hata_yaniti("Geçerli bir JSON mesajı gönderin.", 400)

    mesaj = veri.get("mesaj")

    try:
        # Önceki mesajlar alınmaz veya AI servisine aktarılmaz.
        cevap = ai_service.yanit_uret(mesaj)
        return jsonify(basari=True, cevap=cevap)

    except ValueError as hata:
        return hata_yaniti(str(hata), 400)

    except AIServiceError as hata:
        return hata_yaniti(str(hata), 503)


@api.route("/leads", methods=["POST"])
def lead_kaydet():
    veri = request.get_json(silent=True)

    if not isinstance(veri, dict):
        return hata_yaniti("Geçerli bir JSON formu gönderin.", 400)

    alanlar = {}
    sinirlar = {
        "isim": 100,
        "telefon": 30,
        "email": 254,
        "mesaj": 1500,
    }

    for alan, sinir in sinirlar.items():
        deger = veri.get(alan, "")

        if not isinstance(deger, str):
            return hata_yaniti(
                f"{alan} alanı metin olmalıdır.", 400
            )

        deger = deger.strip()

        if len(deger) > sinir:
            return hata_yaniti(
                f"{alan} alanı en fazla {sinir} karakter olabilir.", 400
            )

        alanlar[alan] = deger

    if not alanlar["isim"] or not alanlar["telefon"]:
        return hata_yaniti("İsim ve telefon alanlarını doldurun.", 400)

    telefon = alanlar["telefon"]
    rakamlar = re.sub(r"[^0-9]", "", telefon)

    if (
        not re.fullmatch(r"\+?[0-9 ()-]+", telefon)
        or not 7 <= len(rakamlar) <= 15
    ):
        return hata_yaniti("Geçerli bir telefon numarası yazın.", 400)

    email = alanlar["email"]

    if email and not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
        return hata_yaniti("E-posta adresini kontrol edin.", 400)

    try:
        kayit_id = lead_ekle(
            isim=alanlar["isim"],
            telefon=telefon,
            mesaj=alanlar["mesaj"],
            email=email,
        )

        return jsonify(
            basari=True,
            id=kayit_id,
            mesaj="İletişim talebiniz kaydedildi.",
        ), 201

    except sqlite3.Error:
        return hata_yaniti(
            "Talebiniz kaydedilemedi. Lütfen tekrar deneyin.", 503
        )


@api.route("/leads", methods=["GET"])
@yonetici_gerekli
def lead_listesi():
    try:
        return jsonify(basari=True, leadler=tum_leadler())

    except sqlite3.Error:
        return hata_yaniti("Kayıtlar şu anda getirilemiyor.", 503)


@pages.after_request
@api.after_request
def onbellegi_kapat(yanit):
    """İletişim verilerinin tarayıcı önbelleğinde tutulmasını önler."""
    yanit.headers["Cache-Control"] = "no-store"
    return yanit