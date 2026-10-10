import sqlite3
from pathlib import Path

from flask import current_app, g


def get_db():
    """Bir istek boyunca aynı veritabanı bağlantısını kullanır."""
    if "db" not in g:
        g.db = sqlite3.connect(
            current_app.config["DATABASE_URL"],
            timeout=10,
        )
        g.db.row_factory = sqlite3.Row

    return g.db


def close_db(error=None):
    """İstek tamamlandığında veritabanı bağlantısını kapatır."""
    db = g.pop("db", None)

    if db is not None:
        db.close()


def init_db(app):
    """Veritabanı klasörünü ve müşteri adayları tablosunu hazırlar."""
    database_path = Path(app.config["DATABASE_URL"])
    database_path.parent.mkdir(parents=True, exist_ok=True)

    app.teardown_appcontext(close_db)

    with app.app_context():
        db = get_db()

        try:
            db.execute(
                """
                CREATE TABLE IF NOT EXISTS leads (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    isim TEXT NOT NULL,
                    telefon TEXT NOT NULL,
                    email TEXT,
                    mesaj TEXT,
                    tarih TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            db.commit()

        except sqlite3.Error:
            db.rollback()
            raise


def lead_ekle(isim, telefon, mesaj="", email=""):
    """İletişim talebini kaydeder ve yeni kaydın numarasını döndürür."""
    db = get_db()

    try:
        # Değerler SQL metnine eklenmez; ? yer tutucularıyla gönderilir.
        cursor = db.execute(
            """
            INSERT INTO leads (isim, telefon, email, mesaj)
            VALUES (?, ?, ?, ?)
            """,
            (isim, telefon, email, mesaj),
        )
        db.commit()
        return cursor.lastrowid

    except sqlite3.Error:
        db.rollback()
        raise


def tum_leadler():
    """Müşteri adaylarını en yeni kayıt önce olacak şekilde getirir."""
    db = get_db()

    rows = db.execute(
        """
        SELECT id, isim, telefon, email, mesaj, tarih
        FROM leads
        ORDER BY tarih DESC, id DESC
        """
    ).fetchall()

    return [dict(row) for row in rows]