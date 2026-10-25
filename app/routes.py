
import re
import sqlite3

from flask import (
    Blueprint,
    jsonify,
    render_template,
    request,
)

from app.database import lead_ekle, tum_leadler
from app.services.ai_service import ai_service, AIServiceError


pages = Blueprint("pages", __name__)
api = Blueprint("api", __name__, url_prefix="/api")


def hata_yaniti(mesaj, durum):
    """Hataları tutarlı bir JSON biçiminde döndürür."""
    return jsonify(basari=False, hata=mesaj), durum


# ANA SAYFA

@pages.route("/", methods=["GET"])
def ana_sayfa():
    return render_template("index.html")


# YÖNETİM PANELİ

@pages.route("/dashboard", methods=["GET"])
def dashboard():
    return render_template("dashboard.html")


# SUNUCU DURUMU

@pages.route("/health", methods=["GET"])
def health():
    return jsonify(
        basari=True,
        durum="calisiyor"
    )


# CHATBOT

@api.route("/sohbet", methods=["POST"])
def sohbet():
    veri = request.get_json(silent=True)

    if not isinstance(veri, dict):
        return hata_yaniti(
            "Geçerli bir JSON mesajı gönderin.",
            400
        )

    mesaj = veri.get("mesaj")

    try:
        cevap = ai_service.yanit_uret(mesaj)

        return jsonify(
            basari=True,
            cevap=cevap
        )

    except ValueError as hata:
        return hata_yaniti(str(hata), 400)

    except AIServiceError as hata:
        return hata_yaniti(str(hata), 503)


# İLETİŞİM FORMU - KAYIT EKLEME

@api.route("/leads", methods=["POST"])
def lead_kaydet():

    veri = request.get_json(silent=True)

    if not isinstance(veri, dict):
        return hata_yaniti(
            "Geçerli bir JSON formu gönderin.",
            400
        )

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
                f"{alan} alanı metin olmalıdır.",
                400
            )

        deger = deger.strip()

        if len(deger) > sinir:
            return hata_yaniti(
                f"{alan} alanı en fazla {sinir} karakter olabilir.",
                400
            )

        alanlar[alan] = deger

    if not alanlar["isim"] or not alanlar["telefon"]:
        return hata_yaniti(
            "İsim ve telefon alanlarını doldurun.",
            400
        )

    telefon = alanlar["telefon"]

    rakamlar = re.sub(
        r"[^0-9]",
        "",
        telefon
    )

    if (
        not re.fullmatch(r"\+?[0-9 ()-]+", telefon)
        or not 7 <= len(rakamlar) <= 15
    ):
        return hata_yaniti(
            "Geçerli bir telefon numarası yazın.",
            400
        )

    email = alanlar["email"]

    if email and not re.fullmatch(
        r"[^@\s]+@[^@\s]+\.[^@\s]+",
        email
    ):
        return hata_yaniti(
            "E-posta adresini kontrol edin.",
            400
        )

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
            mesaj="İletişim talebiniz kaydedildi."
        ), 201

    except sqlite3.Error:
        return hata_yaniti(
            "Talebiniz kaydedilemedi. Lütfen tekrar deneyin.",
            503
        )


# YÖNETİM PANELİ - KAYITLARI GETİRME

@api.route("/leads", methods=["GET"])
def lead_listesi():

    try:

        leadler = tum_leadler()

        return jsonify(
            basari=True,
            leadler=leadler
        ), 200

    except sqlite3.Error:
        return hata_yaniti(
            "Kayıtlar şu anda getirilemiyor.",
            503
        )


# ÖNBELLEK KONTROLÜ

@pages.after_request
@api.after_request
def onbellegi_kapat(yanit):

    yanit.headers["Cache-Control"] = "no-store"

    return yanit
