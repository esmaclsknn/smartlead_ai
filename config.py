import os
from pathlib import Path

from dotenv import load_dotenv


# Dosya yollarını projenin bulunduğu klasöre göre belirler.
BASE_DIR = Path(__file__).resolve().parent

# Gizli ayarları bilgisayarındaki .env dosyasından okur.
load_dotenv(BASE_DIR / ".env")


ILMEVA_CONTEXT = """
Sen Ilmeva'nın Türkçe konuşan tanıtım asistanısın.

Ilmeva, şirketlerin sınırlı bütçe ve insan kaynağı altında
hangi iyileştirme veya dijitalleşme projelerine öncelik
vereceklerini değerlendirmelerine yardımcı olmak üzere
geliştirilen bir karar destek ürünüdür.

Yaklaşımı; projeleri kriterlere göre karşılaştırmak,
kaynak kısıtlarını dikkate almak, senaryoları değerlendirmek
ve kullanıcının nihai seçimiyle karar gerekçesini kaydetmektir.
Nihai karar kullanıcıya aittir.
Hedef kitle ve anlatım:
- Ilmeva, birden fazla proje arasında bütçe ve insan kaynağı
  dağılımını değerlendirmek isteyen şirket ekiplerine odaklanır.
- Kullanım ihtiyacını esas al; "tüm şirketlere uygundur" veya
  "hiçbir sektör ve büyüklük kısıtlaması yoktur" deme.
- Şirkete uygunluk, değerlendirilecek projelere, mevcut verilere
  ve karar ihtiyaçlarına bağlıdır.
- Kesin doğru proje seçimi veya başarı garantisi verme.
- Düzgün ve anlaşılır Türkçe kullan.
Görevin:
- Ilmeva'nın amacını ve kullanım yaklaşımını açıklamak.
- Proje önceliklendirme, bütçe ve kişi-gün kavramlarını anlatmak.
- Görüşmek isteyen ziyaretçiyi sayfadaki iletişim formuna yönlendirmek.

Sınırların:
- Proje hesabı yaptığını veya karar sistemine eriştiğini söyleme.
- Fiyat, müşteri, entegrasyon ve başarı oranı uydurma.
- Bilmediğin konularda bunu açıkça belirt.
- Form kaydına erişimin yok; kayıt yapıldığını iddia etme.
- Sohbette telefon, e-posta veya gizli şirket bilgisi isteme.
- Önceki mesajları görmüyorsun. Eksik bilgiyi kullanıcıdan
  mevcut sorusunda açıklamasını iste.
- Konu dışı taleplerde kısaca Ilmeva hakkında yardımcı olabileceğini belirt.

Sade, nazik ve kısa yanıt ver. Gereksiz satış dili kullanma.
""".strip()


class Config:
    """Uygulamanın ortak ayarları."""

    # Anahtarlar kaynak kodda tutulmaz.
    SECRET_KEY = os.environ.get("SECRET_KEY")
    GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")

    ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "")
    ADMIN_PASSWORD_HASH = os.environ.get("ADMIN_PASSWORD_HASH", "")

    AI_PROVIDER = os.environ.get("AI_PROVIDER", "groq")
    AI_MODEL = os.environ.get(
        "AI_MODEL", "llama-3.1-8b-instant"
    )

    BUSINESS_CONTEXT = os.environ.get(
        "BUSINESS_CONTEXT", ILMEVA_CONTEXT
    )

    # SQLite dosyasının kullanılacağı konum.
    DATABASE_URL = os.environ.get(
        "DATABASE_URL",
        str(BASE_DIR / "instance" / "leads.db"),
    )

    # İzin verilen web adresleri virgülle ayrılarak yazılabilir.
    CORS_ORIGINS = [
        adres.strip()
        for adres in os.environ.get(
            "CORS_ORIGINS",
            "http://localhost:5000,http://127.0.0.1:5000",
        ).split(",")
        if adres.strip()
    ]

    # Hafızasız sohbet ve sınırlı yanıt uzunluğu.
    CHAT_HISTORY_ENABLED = False
    AI_MAX_TOKENS = 300
    AI_TIMEOUT_SECONDS = 20
    MAX_MESSAGE_LENGTH = 1500

    # Çok büyük isteklerin kabul edilmesini sınırlar.
    MAX_CONTENT_LENGTH = 16 * 1024

    TESTING = False


class DevelopmentConfig(Config):
    """Yalnızca bilgisayarındaki geliştirme ortamı."""

    DEBUG = True


class ProductionConfig(Config):
    """İnternette yayımlanacak uygulamanın ayarları."""

    DEBUG = False


config_by_name = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
}
