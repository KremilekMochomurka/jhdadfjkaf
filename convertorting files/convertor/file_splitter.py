"""
File Splitter Module

Tento modul poskytuje funkce pro rozdělení velkých souborů na menší části,
které lze zpracovat postupně. Podporuje různé typy souborů včetně PDF, DOCX, TXT a dalších.
"""

import os
import logging
import uuid
import shutil
import PyPDF2
from pathlib import Path

# Konfigurace loggeru
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Konstanty
DEFAULT_CHUNK_SIZE = 5  # Počet stránek na jeden chunk pro PDF
DEFAULT_TEXT_CHUNK_SIZE = 50000  # Počet znaků na jeden chunk pro textové soubory
MAX_FILE_SIZE_MB = 10  # Maximální velikost souboru v MB, nad kterou se soubor rozdělí

def should_split_file(file_path, max_size_mb=MAX_FILE_SIZE_MB):
    """
    Určí, zda by měl být soubor rozdělen na základě jeho velikosti nebo typu.
    
    Args:
        file_path (str): Cesta k souboru
        max_size_mb (int): Maximální velikost souboru v MB, nad kterou se soubor rozdělí
        
    Returns:
        tuple: (bool, str) - (zda rozdělit soubor, důvod rozdělení)
    """
    file_path_obj = Path(file_path)
    file_extension = file_path_obj.suffix.lower()
    file_size_mb = file_path_obj.stat().st_size / (1024 * 1024)  # Převod na MB
    
    # Kontrola velikosti souboru
    if file_size_mb > max_size_mb:
        return True, f"Soubor je příliš velký ({file_size_mb:.2f} MB > {max_size_mb} MB)"
    
    # Kontrola typu souboru a počtu stránek pro PDF
    if file_extension == '.pdf':
        try:
            with open(file_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                total_pages = len(reader.pages)
                if total_pages > DEFAULT_CHUNK_SIZE:
                    return True, f"PDF má příliš mnoho stránek ({total_pages} > {DEFAULT_CHUNK_SIZE})"
        except Exception as e:
            logger.error(f"Chyba při čtení PDF {file_path}: {e}")
    
    # Pro textové soubory kontrolujeme velikost obsahu
    if file_extension in ['.txt', '.html', '.htm', '.json', '.csv']:
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                if len(content) > DEFAULT_TEXT_CHUNK_SIZE:
                    return True, f"Textový soubor je příliš velký ({len(content)} znaků > {DEFAULT_TEXT_CHUNK_SIZE})"
        except Exception as e:
            logger.error(f"Chyba při čtení textového souboru {file_path}: {e}")
    
    return False, "Soubor není potřeba rozdělit"

def create_split_folder(original_file_path, upload_folder):
    """
    Vytvoří složku pro uložení rozdělených částí souboru.
    
    Args:
        original_file_path (str): Cesta k původnímu souboru
        upload_folder (str): Základní složka pro nahrané soubory
        
    Returns:
        str: Cesta k nově vytvořené složce
    """
    original_filename = os.path.basename(original_file_path)
    folder_name = f"split_{uuid.uuid4()}"
    split_folder_path = os.path.join(upload_folder, folder_name)
    
    # Vytvoření složky
    os.makedirs(split_folder_path, exist_ok=True)
    logger.info(f"Vytvořena složka pro rozdělené části: {split_folder_path}")
    
    return split_folder_path

def split_pdf_file(file_path, split_folder, chunk_size=DEFAULT_CHUNK_SIZE):
    """
    Rozdělí PDF soubor na menší části.
    
    Args:
        file_path (str): Cesta k PDF souboru
        split_folder (str): Složka pro uložení rozdělených částí
        chunk_size (int): Počet stránek na jeden chunk
        
    Returns:
        list: Seznam cest k rozděleným částem
    """
    original_filename = os.path.basename(file_path)
    base_name = os.path.splitext(original_filename)[0]
    
    try:
        with open(file_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            total_pages = len(reader.pages)
            
            # Výpočet počtu částí
            num_chunks = (total_pages + chunk_size - 1) // chunk_size  # Zaokrouhlení nahoru
            
            # Vytvoření částí
            part_files = []
            for i in range(num_chunks):
                start_page = i * chunk_size
                end_page = min((i + 1) * chunk_size, total_pages)
                
                # Vytvoření nového PDF pro tuto část
                writer = PyPDF2.PdfWriter()
                
                # Přidání stránek do nového PDF
                for page_num in range(start_page, end_page):
                    writer.add_page(reader.pages[page_num])
                
                # Uložení části
                part_filename = f"{base_name}_part{i+1}of{num_chunks}.pdf"
                part_path = os.path.join(split_folder, part_filename)
                
                with open(part_path, 'wb') as part_file:
                    writer.write(part_file)
                
                part_files.append(part_path)
                logger.info(f"Vytvořena část {i+1}/{num_chunks}: {part_path} (stránky {start_page+1}-{end_page})")
            
            return part_files, num_chunks
    
    except Exception as e:
        logger.error(f"Chyba při rozdělování PDF {file_path}: {e}")
        raise

def split_text_file(file_path, split_folder, chunk_size=DEFAULT_TEXT_CHUNK_SIZE):
    """
    Rozdělí textový soubor na menší části.
    
    Args:
        file_path (str): Cesta k textovému souboru
        split_folder (str): Složka pro uložení rozdělených částí
        chunk_size (int): Počet znaků na jeden chunk
        
    Returns:
        list: Seznam cest k rozděleným částem
    """
    original_filename = os.path.basename(file_path)
    base_name = os.path.splitext(original_filename)[0]
    extension = os.path.splitext(original_filename)[1]
    
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            
            # Výpočet počtu částí
            total_length = len(content)
            num_chunks = (total_length + chunk_size - 1) // chunk_size  # Zaokrouhlení nahoru
            
            # Vytvoření částí
            part_files = []
            for i in range(num_chunks):
                start_pos = i * chunk_size
                end_pos = min((i + 1) * chunk_size, total_length)
                
                # Extrakce části obsahu
                chunk_content = content[start_pos:end_pos]
                
                # Uložení části
                part_filename = f"{base_name}_part{i+1}of{num_chunks}{extension}"
                part_path = os.path.join(split_folder, part_filename)
                
                with open(part_path, 'w', encoding='utf-8') as part_file:
                    part_file.write(chunk_content)
                
                part_files.append(part_path)
                logger.info(f"Vytvořena část {i+1}/{num_chunks}: {part_path} (znaky {start_pos+1}-{end_pos})")
            
            return part_files, num_chunks
    
    except Exception as e:
        logger.error(f"Chyba při rozdělování textového souboru {file_path}: {e}")
        raise

def split_binary_file(file_path, split_folder, chunk_size_mb=5):
    """
    Rozdělí binární soubor na menší části.
    
    Args:
        file_path (str): Cesta k binárnímu souboru
        split_folder (str): Složka pro uložení rozdělených částí
        chunk_size_mb (int): Velikost jedné části v MB
        
    Returns:
        list: Seznam cest k rozděleným částem
    """
    original_filename = os.path.basename(file_path)
    base_name = os.path.splitext(original_filename)[0]
    extension = os.path.splitext(original_filename)[1]
    
    try:
        # Velikost souboru v bajtech
        file_size = os.path.getsize(file_path)
        chunk_size_bytes = chunk_size_mb * 1024 * 1024
        
        # Výpočet počtu částí
        num_chunks = (file_size + chunk_size_bytes - 1) // chunk_size_bytes  # Zaokrouhlení nahoru
        
        # Vytvoření částí
        part_files = []
        with open(file_path, 'rb') as f:
            for i in range(num_chunks):
                # Uložení části
                part_filename = f"{base_name}_part{i+1}of{num_chunks}{extension}"
                part_path = os.path.join(split_folder, part_filename)
                
                # Čtení části obsahu
                chunk_data = f.read(chunk_size_bytes)
                
                with open(part_path, 'wb') as part_file:
                    part_file.write(chunk_data)
                
                part_files.append(part_path)
                logger.info(f"Vytvořena část {i+1}/{num_chunks}: {part_path}")
        
        return part_files, num_chunks
    
    except Exception as e:
        logger.error(f"Chyba při rozdělování binárního souboru {file_path}: {e}")
        raise

def split_file(file_path, upload_folder):
    """
    Rozdělí soubor na menší části podle jeho typu.
    
    Args:
        file_path (str): Cesta k souboru
        upload_folder (str): Základní složka pro nahrané soubory
        
    Returns:
        tuple: (split_folder, part_files, num_chunks) nebo (None, None, None) pokud soubor není potřeba rozdělit
    """
    should_split, reason = should_split_file(file_path)
    
    if not should_split:
        logger.info(f"Soubor {file_path} není potřeba rozdělit: {reason}")
        return None, None, None
    
    logger.info(f"Rozdělování souboru {file_path}: {reason}")
    
    # Vytvoření složky pro rozdělené části
    split_folder = create_split_folder(file_path, upload_folder)
    
    # Rozdělení souboru podle typu
    file_extension = os.path.splitext(file_path)[1].lower()
    
    if file_extension == '.pdf':
        part_files, num_chunks = split_pdf_file(file_path, split_folder)
    elif file_extension in ['.txt', '.html', '.htm', '.json', '.csv']:
        part_files, num_chunks = split_text_file(file_path, split_folder)
    else:
        # Pro ostatní typy souborů použijeme obecné binární rozdělení
        part_files, num_chunks = split_binary_file(file_path, split_folder)
    
    return split_folder, part_files, num_chunks

def cleanup_split_folder(split_folder):
    """
    Vyčistí složku s rozdělenými částmi.
    
    Args:
        split_folder (str): Cesta ke složce s rozdělenými částmi
    """
    if split_folder and os.path.exists(split_folder):
        try:
            shutil.rmtree(split_folder)
            logger.info(f"Složka s rozdělenými částmi byla vyčištěna: {split_folder}")
        except Exception as e:
            logger.error(f"Chyba při čištění složky {split_folder}: {e}")
