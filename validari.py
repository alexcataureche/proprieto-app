"""
Modul de validări pentru date ANAF
Validări pentru CNP, CUI, și alte date necesare pentru declarația D212
"""

import re


def valideaza_cnp(cnp: str) -> tuple[bool, str]:
    """
    Validează CNP-ul românesc

    Args:
        cnp: String cu CNP-ul de validat

    Returns:
        Tuple (is_valid, error_message)
    """
    if not cnp:
        return False, "CNP-ul este obligatoriu"

    # Elimină spații
    cnp = cnp.strip().replace(" ", "").replace("-", "")

    # Verifică lungimea
    if len(cnp) != 13:
        return False, "CNP-ul trebuie să aibă 13 cifre"

    # Verifică dacă sunt doar cifre
    if not cnp.isdigit():
        return False, "CNP-ul trebuie să conțină doar cifre"

    # Verifică cifra de sex (prima cifră)
    if cnp[0] not in '123456789':
        return False, "Prima cifră (sex) nu este validă"

    # Verifică luna (caracterele 4-5)
    luna = int(cnp[3:5])
    if luna < 1 or luna > 12:
        return False, "Luna din CNP nu este validă (01-12)"

    # Verifică ziua (caracterele 6-7)
    zi = int(cnp[5:7])
    if zi < 1 or zi > 31:
        return False, "Ziua din CNP nu este validă (01-31)"

    # Verifică cifra de control (ultima cifră)
    greutati = [2, 7, 9, 1, 4, 6, 3, 5, 8, 2, 7, 9]
    suma_control = sum(int(cnp[i]) * greutati[i] for i in range(12))
    cifra_control = suma_control % 11
    if cifra_control == 10:
        cifra_control = 1

    if int(cnp[12]) != cifra_control:
        return False, "Cifra de control a CNP-ului nu este validă"

    return True, ""


def valideaza_cui(cui: str) -> tuple[bool, str]:
    """
    Validează CUI-ul românesc (pentru persoane juridice)

    Args:
        cui: String cu CUI-ul de validat

    Returns:
        Tuple (is_valid, error_message)
    """
    if not cui:
        return False, "CUI-ul este obligatoriu"

    # Elimină spații și prefix RO
    cui_curatat = cui.strip().upper().replace(" ", "").replace("-", "")
    cui_curatat = cui_curatat.replace("RO", "")

    # Verifică dacă sunt doar cifre
    if not cui_curatat.isdigit():
        return False, "CUI-ul trebuie să conțină doar cifre (sau RO + cifre)"

    # Verifică lungimea (2-10 cifre)
    if len(cui_curatat) < 2 or len(cui_curatat) > 10:
        return False, "CUI-ul trebuie să aibă între 2 și 10 cifre"

    return True, ""


def valideaza_telefon(telefon: str) -> tuple[bool, str]:
    """
    Validează numărul de telefon românesc

    Args:
        telefon: String cu numărul de telefon

    Returns:
        Tuple (is_valid, error_message)
    """
    if not telefon:
        return False, "Numărul de telefon este obligatoriu"

    # Elimină spații, paranteze, cratimă
    telefon_curatat = re.sub(r'[\s\-\(\)]', '', telefon)

    # Verifică dacă începe cu +40, 0040, sau 0
    if telefon_curatat.startswith('+40'):
        telefon_curatat = telefon_curatat[3:]
    elif telefon_curatat.startswith('0040'):
        telefon_curatat = telefon_curatat[4:]
    elif telefon_curatat.startswith('0'):
        telefon_curatat = telefon_curatat[1:]

    # Verifică dacă are 9 cifre (format românesc)
    if not telefon_curatat.isdigit():
        return False, "Numărul de telefon trebuie să conțină doar cifre"

    if len(telefon_curatat) != 9:
        return False, "Numărul de telefon trebuie să aibă 9 cifre (fără prefix)"

    # Verifică dacă începe cu 7 (mobil) sau 2, 3 (fix)
    if telefon_curatat[0] not in '723':
        return False, "Numărul de telefon trebuie să înceapă cu 7 (mobil) sau 2/3 (fix)"

    return True, ""


def valideaza_email(email: str) -> tuple[bool, str]:
    """
    Validează adresa de email

    Args:
        email: String cu adresa de email

    Returns:
        Tuple (is_valid, error_message)
    """
    if not email:
        return False, "Adresa de email este obligatorie"

    # Pattern regex pentru email
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

    if not re.match(pattern, email):
        return False, "Adresa de email nu este validă"

    return True, ""


def valideaza_cod_postal(cod_postal: str) -> tuple[bool, str]:
    """
    Validează codul poștal românesc

    Args:
        cod_postal: String cu codul poștal

    Returns:
        Tuple (is_valid, error_message)
    """
    if not cod_postal:
        return True, ""  # Codul poștal este opțional

    # Elimină spații
    cod_postal = cod_postal.strip().replace(" ", "")

    # Verifică dacă are 6 cifre
    if not cod_postal.isdigit() or len(cod_postal) != 6:
        return False, "Codul poștal trebuie să aibă 6 cifre"

    return True, ""


def formateaza_cnp(cnp: str) -> str:
    """
    Formatează CNP-ul pentru afișare

    Args:
        cnp: String cu CNP-ul

    Returns:
        CNP formatat (ex: 1850203-123456)
    """
    if not cnp or len(cnp) != 13:
        return cnp

    return f"{cnp[:7]}-{cnp[7:]}"


def formateaza_cui(cui: str) -> str:
    """
    Formatează CUI-ul pentru afișare

    Args:
        cui: String cu CUI-ul

    Returns:
        CUI formatat (ex: RO12345678)
    """
    if not cui:
        return cui

    # Elimină prefix RO dacă există
    cui_curatat = cui.strip().upper().replace("RO", "")

    return f"RO{cui_curatat}"


def formateaza_telefon(telefon: str) -> str:
    """
    Formatează numărul de telefon pentru afișare

    Args:
        telefon: String cu numărul de telefon

    Returns:
        Telefon formatat (ex: +40 722 123 456)
    """
    if not telefon:
        return telefon

    # Elimină spații, paranteze, cratimă
    telefon_curatat = re.sub(r'[\s\-\(\)]', '', telefon)

    # Verifică dacă începe cu +40, 0040, sau 0
    if telefon_curatat.startswith('+40'):
        telefon_curatat = telefon_curatat[3:]
    elif telefon_curatat.startswith('0040'):
        telefon_curatat = telefon_curatat[4:]
    elif telefon_curatat.startswith('0'):
        telefon_curatat = telefon_curatat[1:]

    # Verifică dacă are 9 cifre
    if len(telefon_curatat) == 9:
        return f"+40 {telefon_curatat[:3]} {telefon_curatat[3:6]} {telefon_curatat[6:]}"

    return telefon


def formateaza_adresa_completa(
    judet: str = None,
    localitate: str = None,
    strada: str = None,
    numar: str = None,
    bloc: str = None,
    scara: str = None,
    etaj: str = None,
    apartament: str = None,
    cod_postal: str = None
) -> str:
    """
    Formatează o adresă completă pentru afișare

    Args:
        judet: Județul
        localitate: Localitatea
        strada: Strada
        numar: Numărul
        bloc: Blocul
        scara: Scara
        etaj: Etajul
        apartament: Apartamentul
        cod_postal: Codul poștal

    Returns:
        Adresa formatată complet
    """
    parti_adresa = []

    # Strada și număr
    if strada:
        if numar:
            parti_adresa.append(f"Str. {strada} nr. {numar}")
        else:
            parti_adresa.append(f"Str. {strada}")
    elif numar:
        parti_adresa.append(f"nr. {numar}")

    # Bloc
    if bloc:
        parti_adresa.append(f"bl. {bloc}")

    # Scara
    if scara:
        parti_adresa.append(f"sc. {scara}")

    # Etaj
    if etaj:
        parti_adresa.append(f"et. {etaj}")

    # Apartament
    if apartament:
        parti_adresa.append(f"ap. {apartament}")

    # Localitate și județ
    if localitate:
        parti_adresa.append(localitate)

    if judet:
        parti_adresa.append(f"jud. {judet}")

    # Cod poștal
    if cod_postal:
        parti_adresa.append(cod_postal)

    return ", ".join(parti_adresa)


# Lista județelor din România pentru dropdown
JUDETE_ROMANIA = [
    "Alba", "Arad", "Argeș", "Bacău", "Bihor", "Bistrița-Năsăud",
    "Botoșani", "Brașov", "Brăila", "București", "Buzău", "Caraș-Severin",
    "Călărași", "Cluj", "Constanța", "Covasna", "Dâmbovița", "Dolj",
    "Galați", "Giurgiu", "Gorj", "Harghita", "Hunedoara", "Ialomița",
    "Iași", "Ilfov", "Maramureș", "Mehedinți", "Mureș", "Neamț",
    "Olt", "Prahova", "Satu Mare", "Sălaj", "Sibiu", "Suceava",
    "Teleorman", "Timiș", "Tulcea", "Vaslui", "Vâlcea", "Vrancea"
]

# Frecvențe de plată disponibile
FRECVENTE_PLATA = [
    "lunar",
    "trimestrial",
    "semestrial",
    "anual"
]

# Monede disponibile
MONEDE = ["RON", "EUR", "USD"]
