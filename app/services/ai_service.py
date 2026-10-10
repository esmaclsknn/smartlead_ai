import requests


class AIServiceError(Exception):
    """Yapay zekâ bağlantısında oluşan kontrollü hatalar."""
    pass


class AIService:
    def __init__(self):
        self.ayarlar = None

    def yapilandir(self, ayarlar):
        """Uygulamanın ayarlarını alır; Flask'a doğrudan bağlanmaz."""
        self.ayarlar = dict(ayarlar)

    def _mesajlari_hazirla(self, mesaj):
        """Yalnızca marka bilgisi ve mevcut soruyu gönderir."""
        return [
            {
                "role": "system",
                "content": self.ayarlar["BUSINESS_CONTEXT"],
            },
            {
                "role": "user",
                "content": mesaj,
            },
        ]

    def yanit_uret(self, mesaj, gecmis=None):
        # Yönergedeki parametre korunur ancak geçmiş kullanılmaz.
        if self.ayarlar is None:
            raise AIServiceError("Asistan ayarları henüz yüklenmedi.")

        if not isinstance(mesaj, str) or not mesaj.strip():
            raise ValueError("Lütfen bir mesaj yazın.")

        mesaj = mesaj.strip()

        if len(mesaj) > self.ayarlar["MAX_MESSAGE_LENGTH"]:
            raise ValueError("Mesajınız çok uzun. Lütfen kısaltın.")

        if self.ayarlar["AI_PROVIDER"] != "groq":
            raise AIServiceError("Yapay zekâ sağlayıcısı desteklenmiyor.")

        api_anahtari = self.ayarlar.get("GROQ_API_KEY", "").strip()

        if not api_anahtari:
            return (
                "Deneme modu: Yapay zekâ bağlantısı henüz kurulmadı. "
                "Bu, otomatik oluşturulmuş bir AI yanıtı değildir. "
                "Ilmeva, şirketlerin bütçe ve insan kaynağı "
                "kısıtları altında projelerini önceliklendirmesine "
                "yardımcı olan bir karar destek ürünüdür."
            )

        try:
            response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_anahtari}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": self.ayarlar["AI_MODEL"],
                    "messages": self._mesajlari_hazirla(mesaj),
                    "max_completion_tokens": self.ayarlar["AI_MAX_TOKENS"],
                    "temperature": 0.3,
                    "stream": False,
                },
                timeout=self.ayarlar["AI_TIMEOUT_SECONDS"],
            )

            response.raise_for_status()

        except requests.exceptions.Timeout:
            raise AIServiceError(
                "Asistan zamanında yanıt veremedi. Lütfen tekrar deneyin."
            ) from None

        except requests.exceptions.HTTPError as hata:
            durum = hata.response.status_code

            if durum == 429:
                aciklama = (
                    "Asistanın kullanım sınırına ulaşıldı. "
                    "Lütfen daha sonra tekrar deneyin."
                )
            elif durum in (401, 403):
                aciklama = "Asistanın bağlantı yetkisi doğrulanamadı."
            else:
                aciklama = "Yapay zekâ hizmetinden yanıt alınamadı."

            raise AIServiceError(aciklama) from None

        except requests.exceptions.RequestException:
            raise AIServiceError(
                "Yapay zekâ hizmetine bağlanılamadı."
            ) from None

        try:
            veri = response.json()
            cevap = veri["choices"][0]["message"]["content"]

            if not isinstance(cevap, str) or not cevap.strip():
                raise ValueError("Boş yanıt.")

            return cevap.strip()

        except (ValueError, KeyError, IndexError, TypeError):
            raise AIServiceError(
                "Asistandan geçerli bir yanıt alınamadı."
            ) from None


ai_service = AIService()