"""
Migrační skript pro aktualizaci databáze.

Tento skript přidá nové sloupce do tabulky user_document pro podporu rozdělených souborů.
"""

import os
import sqlite3
import logging

# Konfigurace loggeru
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Cesta k databázi
DB_PATH = os.path.join('instance', 'app.db')

def migrate_database():
    """
    Provede migraci databáze - přidá nové sloupce pro podporu rozdělených souborů.
    """
    if not os.path.exists(DB_PATH):
        logger.error(f"Databáze nenalezena na cestě: {DB_PATH}")
        return False

    try:
        # Připojení k databázi
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Zjištění, zda sloupce již existují
        cursor.execute("PRAGMA table_info(user_document)")
        columns = [column[1] for column in cursor.fetchall()]
        
        # Seznam sloupců, které chceme přidat
        new_columns = [
            ("is_split", "BOOLEAN DEFAULT 0"),
            ("split_folder", "VARCHAR(255)"),
            ("parent_id", "INTEGER"),
            ("part_number", "INTEGER"),
            ("total_parts", "INTEGER")
        ]
        
        # Přidání chybějících sloupců
        for column_name, column_type in new_columns:
            if column_name not in columns:
                logger.info(f"Přidávám sloupec {column_name} do tabulky user_document")
                cursor.execute(f"ALTER TABLE user_document ADD COLUMN {column_name} {column_type}")
            else:
                logger.info(f"Sloupec {column_name} již existuje v tabulce user_document")
        
        # Přidání cizího klíče pro parent_id (pokud je to možné)
        try:
            if "parent_id" not in columns:
                logger.info("Přidávám cizí klíč pro parent_id")
                cursor.execute("""
                    CREATE TRIGGER fk_user_document_parent_id
                    BEFORE INSERT ON user_document
                    FOR EACH ROW BEGIN
                        SELECT CASE
                            WHEN NEW.parent_id IS NOT NULL AND
                                (SELECT id FROM user_document WHERE id = NEW.parent_id) IS NULL
                            THEN RAISE(ABORT, 'Foreign key constraint failed on parent_id')
                        END;
                    END;
                """)
        except sqlite3.Error as e:
            logger.warning(f"Nepodařilo se přidat cizí klíč pro parent_id: {e}")
        
        # Uložení změn
        conn.commit()
        logger.info("Migrace databáze byla úspěšně dokončena")
        
        # Zavření spojení
        conn.close()
        return True
    
    except sqlite3.Error as e:
        logger.error(f"Chyba při migraci databáze: {e}")
        return False

if __name__ == "__main__":
    logger.info("Spouštím migraci databáze...")
    success = migrate_database()
    
    if success:
        logger.info("Migrace databáze byla úspěšně dokončena")
    else:
        logger.error("Migrace databáze selhala")
