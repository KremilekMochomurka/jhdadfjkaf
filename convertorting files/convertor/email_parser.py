"""
Modul pro detekci a zpracování emailové korespondence.
"""

import re
import json
import logging
import datetime
from typing import List, Dict, Any, Tuple, Optional

# Nastavení loggeru
logger = logging.getLogger(__name__)

# Regulární výrazy pro detekci emailů
EMAIL_HEADER_PATTERNS = [
    r'Od:\s*([^\n]+)',
    r'Odesílatel:\s*([^\n]+)',
    r'From:\s*([^\n]+)',
    r'Sender:\s*([^\n]+)',
    r'Komu:\s*([^\n]+)',
    r'Pro:\s*([^\n]+)',
    r'To:\s*([^\n]+)',
    r'Předmět:\s*([^\n]+)',
    r'Subject:\s*([^\n]+)',
    r'Datum:\s*([^\n]+)',
    r'Date:\s*([^\n]+)',
    r'Kopie:\s*([^\n]+)',
    r'CC:\s*([^\n]+)',
    r'Skrytá kopie:\s*([^\n]+)',
    r'BCC:\s*([^\n]+)',
]

# Regulární výrazy pro detekci začátku nového emailu
NEW_EMAIL_PATTERNS = [
    r'[-]{3,}Původní zpráva[-]{3,}',
    r'[-]{3,}Original Message[-]{3,}',
    r'[-]{3,}Forwarded message[-]{3,}',
    r'[-]{3,}Přeposlaná zpráva[-]{3,}',
    r'Dne\s+[\d\.]+\s+v\s+[\d:]+\s+(?:[\w\s]+)\s+napsal',
    r'On\s+[\w\s,]+\s+wrote:',
    r'From:[\s\w@\.<>]+Sent:[\s\w,]+To:',
    r'Od:[\s\w@\.<>]+Odesláno:[\s\w,]+Komu:',
]

# Regulární výraz pro detekci emailové adresy
EMAIL_REGEX = r'[\w\.-]+@[\w\.-]+'

def is_email_correspondence(text: str) -> bool:
    """
    Detekuje, zda se jedná o emailovou korespondenci.

    Args:
        text: Text k analýze

    Returns:
        bool: True pokud se jedná o emailovou korespondenci, jinak False
    """
    # Kontrola, zda text obsahuje typické emailové hlavičky
    header_count = 0
    for pattern in EMAIL_HEADER_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            header_count += 1

    # Kontrola, zda text obsahuje emailové adresy
    email_addresses = re.findall(EMAIL_REGEX, text)

    # Kontrola, zda text obsahuje typické značky pro přeposlané emaily
    forwarded_markers = 0
    for pattern in NEW_EMAIL_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            forwarded_markers += 1

    # Rozhodnutí na základě kombinace faktorů
    if (header_count >= 3 and len(email_addresses) >= 1) or forwarded_markers >= 1:
        return True

    return False

def extract_email_parts(text: str) -> List[Dict[str, Any]]:
    """
    Extrahuje jednotlivé emaily z textu emailové korespondence.

    Args:
        text: Text emailové korespondence

    Returns:
        List[Dict]: Seznam emailů s jejich částmi (odesílatel, příjemce, předmět, datum, obsah)
    """
    # Rozdělení textu na jednotlivé emaily
    email_parts = []

    # Nejprve zkusíme rozdělit podle typických značek pro přeposlané emaily
    email_blocks = []

    # Spojíme všechny vzory pro detekci nového emailu do jednoho
    combined_pattern = '|'.join(f'({pattern})' for pattern in NEW_EMAIL_PATTERNS)

    # Přidáme další vzory pro detekci emailových hlaviček, které mohou označovat začátek nového emailu
    header_patterns = [
        r'(?:Od:|Odesílatel:|From:|Sender:)\s*([^\n]+)[\n\r]+(?:Komu:|Pro:|To:)',
        r'(?:Od:|Odesílatel:|From:|Sender:)\s*([^\n]+)[\n\r]+(?:Odesláno:|Sent:|Datum:|Date:)',
        r'(?:Od:|Odesílatel:|From:|Sender:)\s*([^\n]+)[\n\r]+(?:Předmět:|Subject:)'
    ]

    # Přidáme vzory pro detekci emailových hlaviček do kombinovaného vzoru
    header_combined = '|'.join(f'({pattern})' for pattern in header_patterns)

    # Rozšířený kombinovaný vzor pro detekci začátku nového emailu
    extended_pattern = f"{combined_pattern}|{header_combined}"

    # Pokud najdeme alespoň jeden vzor, rozdělíme text
    if re.search(extended_pattern, text, re.IGNORECASE | re.MULTILINE):
        # Nejprve zkusíme najít všechny výskyty vzorů v textu
        matches = []

        # Hledáme všechny výskyty vzorů pro přeposlané emaily
        for pattern in NEW_EMAIL_PATTERNS:
            for match in re.finditer(pattern, text, re.IGNORECASE | re.MULTILINE):
                matches.append((match.start(), match.group()))

        # Hledáme všechny výskyty vzorů pro emailové hlavičky
        for pattern in header_patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE | re.MULTILINE):
                # Ujistíme se, že je to začátek řádku nebo předchozí řádek je prázdný
                if match.start() == 0 or text[match.start()-1] == '\n' or text[match.start()-2:match.start()] == '\r\n':
                    matches.append((match.start(), match.group()))

        # Seřadíme výskyty podle pozice v textu
        matches.sort(key=lambda x: x[0])

        # Pokud nemáme žádné výskyty, považujeme celý text za jeden email
        if not matches:
            email_blocks = [text]
        else:
            # Rozdělíme text podle nalezených výskytů
            last_pos = 0
            for pos, match_text in matches:
                # Přidáme text před aktuálním výskytem jako samostatný blok
                if pos > last_pos and text[last_pos:pos].strip():
                    email_blocks.append(text[last_pos:pos].strip())

                # Najdeme konec aktuálního emailu (začátek dalšího nebo konec textu)
                next_pos = len(text)
                for next_match_pos, _ in matches:
                    if next_match_pos > pos:
                        next_pos = next_match_pos
                        break

                # Přidáme aktuální email jako samostatný blok
                if next_pos > pos and text[pos:next_pos].strip():
                    email_blocks.append(text[pos:next_pos].strip())

                last_pos = next_pos

            # Přidáme poslední část textu, pokud existuje
            if last_pos < len(text) and text[last_pos:].strip():
                email_blocks.append(text[last_pos:].strip())
    else:
        # Pokud nenajdeme typické značky, zkusíme rozdělit podle emailových hlaviček
        # Hledáme všechny výskyty vzorů pro emailové hlavičky
        header_matches = []

        for header_pattern in [
            r'(?:Od:|Odesílatel:|From:|Sender:)\s*([^\n]+)',
            r'(?:Komu:|Pro:|To:)\s*([^\n]+)',
            r'(?:Předmět:|Subject:)\s*([^\n]+)',
            r'(?:Datum:|Date:|Odesláno:|Sent:)\s*([^\n]+)'
        ]:
            for match in re.finditer(header_pattern, text, re.IGNORECASE | re.MULTILINE):
                header_matches.append((match.start(), match.group()))

        # Seřadíme výskyty podle pozice v textu
        header_matches.sort(key=lambda x: x[0])

        # Pokud máme alespoň 3 hlavičky blízko sebe, považujeme to za začátek emailu
        email_starts = []

        for i in range(len(header_matches) - 2):
            pos1, _ = header_matches[i]
            pos2, _ = header_matches[i+1]
            pos3, _ = header_matches[i+2]

            # Pokud jsou hlavičky blízko sebe (méně než 200 znaků mezi nimi), považujeme to za začátek emailu
            if pos2 - pos1 < 200 and pos3 - pos2 < 200:
                email_starts.append(pos1)

        # Pokud jsme našli začátky emailů, rozdělíme text podle nich
        if email_starts:
            for i in range(len(email_starts)):
                start_pos = email_starts[i]
                end_pos = email_starts[i+1] if i+1 < len(email_starts) else len(text)

                if text[start_pos:end_pos].strip():
                    email_blocks.append(text[start_pos:end_pos].strip())
        else:
            # Pokud nenajdeme žádné začátky emailů, považujeme celý text za jeden email
            email_blocks = [text]

    # Zpracování každého bloku emailu
    for block in email_blocks:
        email_data = {}

        # Extrakce hlaviček
        for header_name, pattern in [
            ('from', r'(?:Od:|Odesílatel:|From:|Sender:)\s*([^\n]+)'),
            ('to', r'(?:Komu:|Pro:|To:)\s*([^\n]+)'),
            ('subject', r'(?:Předmět:|Subject:)\s*([^\n]+)'),
            ('date', r'(?:Datum:|Date:|Odesláno:|Sent:)\s*([^\n]+)'),
            ('cc', r'(?:Kopie:|CC:)\s*([^\n]+)'),
            ('bcc', r'(?:Skrytá kopie:|BCC:)\s*([^\n]+)')
        ]:
            match = re.search(pattern, block, re.IGNORECASE)
            if match:
                email_data[header_name] = match.group(1).strip()

        # Extrakce emailových adres
        if 'from' in email_data:
            from_emails = re.findall(EMAIL_REGEX, email_data['from'])
            if from_emails:
                email_data['from_email'] = from_emails[0]

        if 'to' in email_data:
            to_emails = re.findall(EMAIL_REGEX, email_data['to'])
            if to_emails:
                email_data['to_emails'] = to_emails

        # Extrakce obsahu - odstraníme hlavičky a ponecháme jen tělo emailu
        content = block
        for pattern in EMAIL_HEADER_PATTERNS:
            content = re.sub(pattern, '', content, flags=re.IGNORECASE)

        # Odstranění prázdných řádků na začátku
        content = re.sub(r'^\s*\n', '', content, flags=re.MULTILINE)

        email_data['content'] = content.strip()

        # Přidání časové značky pro řazení
        if 'date' in email_data:
            try:
                # Pokus o extrakci data a času
                date_str = email_data['date']
                # Zde by bylo ideální použít pokročilejší parsování data,
                # ale pro jednoduchost použijeme aktuální čas a relativní pořadí
                email_data['timestamp'] = datetime.datetime.now().isoformat()
            except:
                email_data['timestamp'] = datetime.datetime.now().isoformat()
        else:
            email_data['timestamp'] = datetime.datetime.now().isoformat()

        email_parts.append(email_data)

    # Seřazení emailů podle časové značky (nejnovější první)
    email_parts.reverse()

    return email_parts

def emails_to_json(emails: List[Dict[str, Any]]) -> str:
    """
    Převede seznam emailů do JSON formátu.

    Args:
        emails: Seznam emailů

    Returns:
        str: JSON reprezentace emailů
    """
    email_data = {
        "type": "email_correspondence",
        "emails": emails,
        "total_emails": len(emails),
        "extracted_at": datetime.datetime.now().isoformat()
    }

    return json.dumps(email_data, ensure_ascii=False, indent=2)

def process_email_correspondence(text: str) -> Tuple[bool, Optional[str]]:
    """
    Zpracuje text a pokud se jedná o emailovou korespondenci, převede ji do strukturovaného JSON.

    Args:
        text: Text k analýze

    Returns:
        Tuple[bool, Optional[str]]: (Je to email?, JSON struktura nebo None)
    """
    if is_email_correspondence(text):
        emails = extract_email_parts(text)
        if emails:
            return True, emails_to_json(emails)

    return False, None
