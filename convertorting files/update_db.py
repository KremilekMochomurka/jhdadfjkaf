from app import app
import os
import sqlite3

# Přidání sloupce content_type do tabulky user_document
with app.app_context():
    # Získání cesty k databázi
    db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')

    # Připojení k databázi
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Přidání sloupce content_type
    try:
        cursor.execute('ALTER TABLE user_document ADD COLUMN content_type VARCHAR(50) DEFAULT "unknown"')
        print("Sloupec content_type byl přidán.")
    except sqlite3.OperationalError as e:
        print(f"Sloupec content_type již existuje nebo nastala chyba: {e}")

    # Přidání sloupce folder_id
    try:
        cursor.execute('ALTER TABLE user_document ADD COLUMN folder_id INTEGER')
        print("Sloupec folder_id byl přidán.")
    except sqlite3.OperationalError as e:
        print(f"Sloupec folder_id již existuje nebo nastala chyba: {e}")

    # Přidání sloupce tags
    try:
        cursor.execute('ALTER TABLE user_document ADD COLUMN tags VARCHAR(500)')
        print("Sloupec tags byl přidán.")
    except sqlite3.OperationalError as e:
        print(f"Sloupec tags již existuje nebo nastala chyba: {e}")

    # Uložení změn
    conn.commit()
    conn.close()

    print("Aktualizace databáze dokončena.")
