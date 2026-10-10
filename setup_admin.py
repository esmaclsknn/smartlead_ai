from getpass import getpass
from pathlib import Path
import secrets

from dotenv import dotenv_values, set_key
from werkzeug.security import generate_password_hash


def main():
    env_dosyasi = Path(__file__).resolve().parent / ".env"

    if not env_dosyasi.is_file():
        print(".env bulunamadı. Dosyayı proje klasörüne kaydedin.")
        return

    print("Yönetici kullanıcı adınız: esma")
    print("Parola yazarken ekranda karakter görünmemesi normaldir.")

    parola = getpass("Yeni yönetici parolası (en az 12 karakter): ")

    if len(parola) < 12:
        print("Parola kısa. İşlem yapılmadı; tekrar çalıştırın.")
        return

    tekrar = getpass("Aynı parolayı tekrar yazın: ")

    if parola != tekrar:
        print("Parolalar eşleşmedi. İşlem yapılmadı.")
        return

    ayarlar = dotenv_values(env_dosyasi)

    set_key(str(env_dosyasi), "ADMIN_USERNAME", "esma")
    set_key(
        str(env_dosyasi),
        "ADMIN_PASSWORD_HASH",
        generate_password_hash(parola),
    )

    if not ayarlar.get("SECRET_KEY"):
        set_key(
            str(env_dosyasi),
            "SECRET_KEY",
            secrets.token_hex(32),
        )

    # Dosyayı yalnızca Mac kullanıcı hesabın okuyup yazabilsin.
    env_dosyasi.chmod(0o600)

    print("YÖNETİCİ AYARLARI KAYDEDİLDİ.")
    print("Kullanıcı adı: esma")
    print("Groq anahtarı ve model ayarı korundu.")


if __name__ == "__main__":
    main()