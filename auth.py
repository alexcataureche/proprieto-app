"""
Modul de autentificare pentru Proprieto ANAF 2026
Gestionează login, logout și verificarea sesiunii utilizatorilor
"""

import streamlit as st
from supabase import Client
import hashlib
import secrets
from datetime import datetime, timedelta

def hash_password(password: str, salt: str = None) -> tuple:
    """Hash password cu salt pentru securitate"""
    if salt is None:
        salt = secrets.token_hex(16)

    pwd_hash = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt.encode('utf-8'),
        100000
    )
    return pwd_hash.hex(), salt

def verify_password(password: str, pwd_hash: str, salt: str) -> bool:
    """Verifică dacă parola este corectă"""
    new_hash, _ = hash_password(password, salt)
    return new_hash == pwd_hash

def init_session_state():
    """Inițializează session state pentru autentificare"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'user_id' not in st.session_state:
        st.session_state.user_id = None
    if 'user_email' not in st.session_state:
        st.session_state.user_email = None
    if 'user_name' not in st.session_state:
        st.session_state.user_name = None
    if 'user_role' not in st.session_state:
        st.session_state.user_role = None
    if 'login_attempts' not in st.session_state:
        st.session_state.login_attempts = 0
    if 'last_login_attempt' not in st.session_state:
        st.session_state.last_login_attempt = None

def check_rate_limit() -> bool:
    """Verifică rate limiting pentru login (max 5 încercări / 15 min)"""
    if st.session_state.login_attempts >= 5:
        if st.session_state.last_login_attempt:
            time_diff = datetime.now() - st.session_state.last_login_attempt
            if time_diff < timedelta(minutes=15):
                return False
            else:
                # Reset după 15 minute
                st.session_state.login_attempts = 0
    return True

def login_user(supabase: Client, email: str, password: str) -> tuple:
    """
    Autentifică utilizatorul
    Returns: (success: bool, message: str, user_data: dict)
    """
    try:
        # Rate limiting
        if not check_rate_limit():
            return False, "Prea multe încercări de login. Așteaptă 15 minute.", None

        # Caută utilizatorul în baza de date
        result = supabase.table("users").select("*").eq("email", email.lower()).execute()

        if not result.data:
            st.session_state.login_attempts += 1
            st.session_state.last_login_attempt = datetime.now()
            return False, "Email sau parolă incorectă.", None

        user = result.data[0]

        # Verifică dacă contul este activ
        if not user.get('active', True):
            return False, "Contul este dezactivat. Contactează administratorul.", None

        # Verifică parola
        if verify_password(password, user['password_hash'], user['salt']):
            # Reset login attempts
            st.session_state.login_attempts = 0

            # Actualizează last_login
            supabase.table("users").update({
                "last_login": datetime.now().isoformat()
            }).eq("id", user['id']).execute()

            # Setează session state
            st.session_state.authenticated = True
            st.session_state.user_id = user['id']
            st.session_state.user_email = user['email']
            st.session_state.user_name = user.get('nume', user['email'])
            st.session_state.user_role = user.get('role', 'user')

            return True, "Autentificare reușită!", user
        else:
            st.session_state.login_attempts += 1
            st.session_state.last_login_attempt = datetime.now()
            return False, "Email sau parolă incorectă.", None

    except Exception as e:
        return False, f"Eroare la autentificare: {str(e)}", None

def logout_user():
    """Deconectează utilizatorul"""
    st.session_state.authenticated = False
    st.session_state.user_id = None
    st.session_state.user_email = None
    st.session_state.user_name = None
    st.session_state.user_role = None
    st.session_state.login_attempts = 0

def register_user(supabase: Client, email: str, password: str, nume: str, role: str = 'user') -> tuple:
    """
    Înregistrează un utilizator nou
    Returns: (success: bool, message: str)
    """
    try:
        # Validare email
        if '@' not in email or '.' not in email:
            return False, "Email invalid."

        # Validare parolă (min 8 caractere)
        if len(password) < 8:
            return False, "Parola trebuie să aibă minim 8 caractere."

        # Verifică dacă emailul există deja
        result = supabase.table("users").select("id").eq("email", email.lower()).execute()
        if result.data:
            return False, "Acest email este deja înregistrat."

        # Hash parolă
        pwd_hash, salt = hash_password(password)

        # Creează utilizator
        user_data = {
            "email": email.lower(),
            "password_hash": pwd_hash,
            "salt": salt,
            "nume": nume,
            "role": role,
            "active": True,
            "created_at": datetime.now().isoformat()
        }

        supabase.table("users").insert(user_data).execute()

        return True, "Cont creat cu succes! Poți să te autentifici acum."

    except Exception as e:
        return False, f"Eroare la înregistrare: {str(e)}"

def change_password(supabase: Client, user_id: str, old_password: str, new_password: str) -> tuple:
    """
    Schimbă parola utilizatorului
    Returns: (success: bool, message: str)
    """
    try:
        # Validare parolă nouă
        if len(new_password) < 8:
            return False, "Parola nouă trebuie să aibă minim 8 caractere."

        # Preia datele utilizatorului
        result = supabase.table("users").select("*").eq("id", user_id).execute()
        if not result.data:
            return False, "Utilizator negăsit."

        user = result.data[0]

        # Verifică parola veche
        if not verify_password(old_password, user['password_hash'], user['salt']):
            return False, "Parola curentă este incorectă."

        # Hash parola nouă
        pwd_hash, salt = hash_password(new_password)

        # Actualizează în baza de date
        supabase.table("users").update({
            "password_hash": pwd_hash,
            "salt": salt
        }).eq("id", user_id).execute()

        return True, "Parolă schimbată cu succes!"

    except Exception as e:
        return False, f"Eroare la schimbarea parolei: {str(e)}"

def is_admin() -> bool:
    """Verifică dacă utilizatorul curent este administrator"""
    return st.session_state.get('user_role') == 'admin'

def require_auth(func):
    """Decorator pentru a proteja funcții care necesită autentificare"""
    def wrapper(*args, **kwargs):
        if not st.session_state.get('authenticated', False):
            st.warning("Trebuie să fii autentificat pentru a accesa această pagină.")
            st.stop()
        return func(*args, **kwargs)
    return wrapper

def require_admin(func):
    """Decorator pentru a proteja funcții care necesită rol de admin"""
    def wrapper(*args, **kwargs):
        if not st.session_state.get('authenticated', False):
            st.warning("Trebuie să fii autentificat pentru a accesa această pagină.")
            st.stop()
        if not is_admin():
            st.error("Nu ai permisiuni de administrator pentru această acțiune.")
            st.stop()
        return func(*args, **kwargs)
    return wrapper
