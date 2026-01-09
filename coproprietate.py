"""
Modul pentru gestionarea co-proprietății în Proprieto
Permite mai multor utilizatori să dețină același imobil/contract
"""

import streamlit as st
from supabase import Client
from typing import List, Dict, Optional, Tuple

def get_imobile_user(supabase: Client, user_id: str, include_shared: bool = True) -> List[Dict]:
    """
    Obține toate imobilele la care un user are acces
    (atât cele personale cât și co-proprietățile)
    """
    try:
        if include_shared:
            # Folosește tabelul de legătură pentru co-proprietăți
            result = supabase.table("imobile_proprietari")\
                .select("*, imobile(*), users(nume, email)")\
                .eq("user_id", user_id)\
                .execute()

            return result.data if result.data else []
        else:
            # Doar imobilele unde e proprietar unic
            result = supabase.table("imobile")\
                .select("*")\
                .eq("user_id", user_id)\
                .execute()

            return result.data if result.data else []
    except Exception as e:
        st.error(f"Eroare la preluarea imobilelor: {str(e)}")
        return []

def get_contracte_user(supabase: Client, user_id: str, include_shared: bool = True) -> List[Dict]:
    """
    Obține toate contractele la care un user are acces
    """
    try:
        if include_shared:
            result = supabase.table("contracte_proprietari")\
                .select("*, contracte(*, imobile(nume))")\
                .eq("user_id", user_id)\
                .execute()

            return result.data if result.data else []
        else:
            result = supabase.table("contracte")\
                .select("*, imobile(nume)")\
                .eq("user_id", user_id)\
                .execute()

            return result.data if result.data else []
    except Exception as e:
        st.error(f"Eroare la preluarea contractelor: {str(e)}")
        return []

def get_coproprietari_imobil(supabase: Client, imobil_id: str) -> List[Dict]:
    """
    Obține toți co-proprietarii unui imobil
    """
    try:
        result = supabase.table("imobile_proprietari")\
            .select("*, users(id, nume, email)")\
            .eq("imobil_id", imobil_id)\
            .execute()

        return result.data if result.data else []
    except Exception as e:
        st.error(f"Eroare la preluarea co-proprietarilor: {str(e)}")
        return []

def adauga_coproprietar_imobil(
    supabase: Client,
    imobil_id: str,
    user_id: str,
    procent: float
) -> Tuple[bool, str]:
    """
    Adaugă un co-proprietar la un imobil
    """
    try:
        # Verifică că procentul e valid
        if procent <= 0 or procent > 100:
            return False, "Procentul trebuie să fie între 1 și 100"

        # Verifică că nu există deja
        existing = supabase.table("imobile_proprietari")\
            .select("id")\
            .eq("imobil_id", imobil_id)\
            .eq("user_id", user_id)\
            .execute()

        if existing.data:
            return False, "Utilizatorul este deja co-proprietar la acest imobil"

        # Adaugă co-proprietarul
        supabase.table("imobile_proprietari").insert({
            "imobil_id": imobil_id,
            "user_id": user_id,
            "procent_proprietate": procent
        }).execute()

        # Adaugă automat la toate contractele imobilului
        contracte = supabase.table("contracte")\
            .select("id")\
            .eq("imobil_id", imobil_id)\
            .execute()

        if contracte.data:
            for contract in contracte.data:
                try:
                    supabase.table("contracte_proprietari").insert({
                        "contract_id": contract['id'],
                        "user_id": user_id
                    }).execute()
                except:
                    pass  # Poate exista deja

        return True, "Co-proprietar adăugat cu succes!"

    except Exception as e:
        return False, f"Eroare: {str(e)}"

def sterge_coproprietar_imobil(
    supabase: Client,
    imobil_id: str,
    user_id: str
) -> Tuple[bool, str]:
    """
    Șterge un co-proprietar de la un imobil
    """
    try:
        # Verifică că nu e ultimul proprietar
        proprietari = get_coproprietari_imobil(supabase, imobil_id)
        if len(proprietari) <= 1:
            return False, "Nu poți șterge ultimul proprietar al imobilului"

        # Șterge din imobile_proprietari
        supabase.table("imobile_proprietari")\
            .delete()\
            .eq("imobil_id", imobil_id)\
            .eq("user_id", user_id)\
            .execute()

        # Șterge și din contracte_proprietari pentru contractele acestui imobil
        contracte = supabase.table("contracte")\
            .select("id")\
            .eq("imobil_id", imobil_id)\
            .execute()

        if contracte.data:
            for contract in contracte.data:
                try:
                    supabase.table("contracte_proprietari")\
                        .delete()\
                        .eq("contract_id", contract['id'])\
                        .eq("user_id", user_id)\
                        .execute()
                except:
                    pass

        return True, "Co-proprietar șters cu succes!"

    except Exception as e:
        return False, f"Eroare: {str(e)}"

def actualizeaza_procent_coproprietar(
    supabase: Client,
    imobil_id: str,
    user_id: str,
    procent_nou: float
) -> Tuple[bool, str]:
    """
    Actualizează procentul de proprietate al unui co-proprietar
    """
    try:
        if procent_nou <= 0 or procent_nou > 100:
            return False, "Procentul trebuie să fie între 1 și 100"

        supabase.table("imobile_proprietari")\
            .update({"procent_proprietate": procent_nou})\
            .eq("imobil_id", imobil_id)\
            .eq("user_id", user_id)\
            .execute()

        return True, "Procent actualizat cu succes!"

    except Exception as e:
        return False, f"Eroare: {str(e)}"

def get_procent_total_imobil(supabase: Client, imobil_id: str) -> float:
    """
    Calculează suma procentelor pentru un imobil
    """
    try:
        proprietari = get_coproprietari_imobil(supabase, imobil_id)
        return sum(p.get('procent_proprietate', 0) for p in proprietari)
    except:
        return 0

def user_poate_edita_imobil(supabase: Client, user_id: str, imobil_id: str, is_admin: bool = False) -> bool:
    """
    Verifică dacă un user poate edita un imobil
    Admini pot edita orice, userii doar imobilele lor (inclusiv co-proprietăți)
    """
    if is_admin:
        return True

    try:
        result = supabase.table("imobile_proprietari")\
            .select("id")\
            .eq("imobil_id", imobil_id)\
            .eq("user_id", user_id)\
            .execute()

        return bool(result.data)
    except:
        return False

def user_poate_edita_contract(supabase: Client, user_id: str, contract_id: str, is_admin: bool = False) -> bool:
    """
    Verifică dacă un user poate edita un contract
    """
    if is_admin:
        return True

    try:
        result = supabase.table("contracte_proprietari")\
            .select("id")\
            .eq("contract_id", contract_id)\
            .eq("user_id", user_id)\
            .execute()

        return bool(result.data)
    except:
        return False

def creaza_imobil_cu_proprietari(
    supabase: Client,
    nume: str,
    adresa: Optional[str],
    proprietari: List[Dict[str, any]]  # [{"user_id": "...", "procent": 50}, ...]
) -> Tuple[bool, str, Optional[str]]:
    """
    Creează un imobil nou cu multipli proprietari

    Args:
        proprietari: Listă cu dict-uri: {"user_id": "uuid", "procent": 50}

    Returns:
        (success, message, imobil_id)
    """
    try:
        # Verifică că suma procentelor = 100
        suma_procente = sum(p['procent'] for p in proprietari)
        if abs(suma_procente - 100) > 0.01:  # Toleranță pentru erori de rotunjire
            return False, f"Suma procentelor trebuie să fie 100% (acum: {suma_procente}%)", None

        # Creează imobilul (fără user_id pentru că e co-proprietate)
        result = supabase.table("imobile").insert({
            "nume": nume,
            "adresa": adresa,
            "procent_proprietate": 100,  # Total
            "user_id": proprietari[0]['user_id']  # Primul proprietar ca "principal"
        }).execute()

        if not result.data:
            return False, "Eroare la crearea imobilului", None

        imobil_id = result.data[0]['id']

        # Adaugă toți proprietarii
        for prop in proprietari:
            supabase.table("imobile_proprietari").insert({
                "imobil_id": imobil_id,
                "user_id": prop['user_id'],
                "procent_proprietate": prop['procent']
            }).execute()

        return True, "Imobil creat cu succes!", imobil_id

    except Exception as e:
        return False, f"Eroare: {str(e)}", None
