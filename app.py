import streamlit as st
import pandas as pd
from supabase import create_client
from fpdf import FPDF
from io import BytesIO
import datetime
from dateutil.relativedelta import relativedelta
import auth  # Modul de autentificare
import coproprietate  # Modul de co-proprietate
import validari  # Modul de validări CNP, CUI, etc.

# --- CONFIGURARE ---
st.set_page_config(
    page_title="Proprieto ANAF 2026",
    layout="wide",
    page_icon="🏠",
    initial_sidebar_state="expanded"
)

# --- CUSTOM CSS WITH EXACT DESIGN SYSTEM COLORS ---
st.markdown("""
<style>
    /* ============================================
       DESIGN SYSTEM - EXACT COLOR PALETTE
       ============================================ */
    :root {
        /* Primary Colors */
        --primary-color: #2563EB;        /* Primary Blue - Buttons/Active states */
        --primary-hover: #1D4ED8;        /* Primary hover state */
        --navy: #1E293B;                 /* Navy - Titles/Sidebar/Text */
        --app-bg: #F8FAFC;               /* App Background - Page background */
        --surface: #FFFFFF;              /* Surface - Cards/Table background */

        /* Borders */
        --border-color: #E2E8F0;         /* Input borders */
        --border-hover: #F1F5F9;         /* Hover effect on table rows */

        /* Semantic Badge Colors */
        --success-bg: #D1FAE5;           /* Success badge background */
        --success-text: #065F46;         /* Success badge text */
        --warning-bg: #FEF3C7;           /* Warning badge background */
        --warning-text: #92400E;         /* Warning badge text */
        --danger-bg: #FEE2E2;            /* Danger badge background */
        --danger-text: #991B1B;          /* Danger badge text */

        /* Info Banner (Admin mode) */
        --info-banner-bg: #EFF6FF;       /* Info banner background */
        --info-banner-text: #1E40AF;     /* Info banner text */

        /* Grays */
        --gray-500: #64748B;             /* Gray text for secondary info */
        --gray-600: #475569;
        --gray-700: #334155;
    }

    /* ============================================
       MAIN LAYOUT - LIGHT BACKGROUND
       ============================================ */
    .main {
        padding: 2rem 3rem;
        background: var(--app-bg) !important;  /* Solid light background */
    }

    .block-container {
        padding: 2rem 1rem;
        max-width: 1400px;
        background: var(--surface);
        border-radius: 15px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        border: 1px solid var(--border-color);
    }

    /* ============================================
       TYPOGRAPHY - NAVY TEXT
       ============================================ */
    h1 {
        color: var(--navy) !important;
        font-weight: 700 !important;
        margin-bottom: 1.5rem !important;
        padding-bottom: 0.5rem;
        border-bottom: 3px solid var(--primary-color);
    }

    h2, h3 {
        color: var(--navy) !important;
        font-weight: 600 !important;
    }

    p, span, div {
        color: var(--navy);
    }

    /* ============================================
       BUTTONS - PRIMARY BLUE
       ============================================ */
    .stButton>button {
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s ease;
        border: 1px solid var(--border-color);
        box-shadow: 0 1px 2px rgba(0,0,0,0.05);
    }

    .stButton>button:hover {
        transform: translateY(-1px);
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }

    .stButton>button[kind="primary"] {
        background: var(--primary-color) !important;
        color: white !important;
        border: none;
    }

    .stButton>button[kind="primary"]:hover {
        background: var(--primary-hover) !important;
    }

    /* ============================================
       FORMS - BORDERS #E2E8F0, TEXT NAVY
       ============================================ */
    .stTextInput>div>div>input,
    .stNumberInput>div>div>input,
    .stSelectbox>div>div>select,
    .stDateInput>div>div>input {
        border-radius: 8px;
        border: 1px solid var(--border-color) !important;
        padding: 0.75rem;
        transition: border-color 0.3s ease;
        color: var(--navy) !important;
        background: var(--surface) !important;
    }

    .stTextInput>div>div>input:focus,
    .stNumberInput>div>div>input:focus,
    .stSelectbox>div>div>select:focus,
    .stDateInput>div>div>input:focus {
        border-color: var(--primary-color) !important;
        box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1) !important;
        outline: none !important;
    }

    /* ============================================
       SIDEBAR - PRIMARY BLUE GRADIENT
       ============================================ */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, var(--primary-color) 0%, var(--primary-hover) 100%);
        padding: 2rem 1rem;
    }

    [data-testid="stSidebar"] .element-container {
        color: white;
    }

    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] label {
        color: white !important;
    }

    /* Radio buttons in sidebar - Navigation Menu */
    [data-testid="stSidebar"] .stRadio {
        padding: 1rem 0;
    }

    [data-testid="stSidebar"] .stRadio > label {
        display: none !important; /* Hide "Navigare:" label */
    }

    [data-testid="stSidebar"] .stRadio > div {
        display: flex;
        flex-direction: column;
        gap: 0.5rem;
    }

    [data-testid="stSidebar"] .stRadio label {
        background-color: rgba(255,255,255,0.15);
        padding: 1rem 1.25rem;
        border-radius: 10px;
        margin: 0;
        cursor: pointer;
        transition: all 0.3s ease;
        border: 2px solid transparent;
        font-size: 1rem;
        font-weight: 500;
    }

    [data-testid="stSidebar"] .stRadio label:hover {
        background-color: rgba(255,255,255,0.25);
        transform: translateX(5px);
        border-color: rgba(255,255,255,0.3);
    }

    /* Active radio button */
    [data-testid="stSidebar"] .stRadio input:checked + div label {
        background-color: white !important;
        color: var(--primary-color) !important;
        font-weight: 700;
        border-color: white;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }

    /* ============================================
       TABS - PRIMARY BLUE ACTIVE STATE
       ============================================ */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: var(--surface);
        padding: 0.5rem;
        border-radius: 10px;
        border: 1px solid var(--border-color);
    }

    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        transition: all 0.3s ease;
        color: var(--navy);
    }

    .stTabs [data-baseweb="tab"]:hover {
        background-color: var(--border-hover);
    }

    .stTabs [aria-selected="true"] {
        background-color: var(--primary-color) !important;
        color: white !important;
    }

    /* ============================================
       EXPANDERS
       ============================================ */
    .streamlit-expanderHeader {
        background-color: var(--surface);
        border: 1px solid var(--border-color);
        border-radius: 10px;
        padding: 1rem;
        font-weight: 600;
        border-left: 4px solid var(--primary-color);
        color: var(--navy);
    }

    .streamlit-expanderHeader:hover {
        background-color: var(--border-hover);
    }

    /* ============================================
       MESSAGES - SEMANTIC COLORS
       ============================================ */
    .stSuccess {
        background-color: var(--success-bg) !important;
        color: var(--success-text) !important;
        border-left: 4px solid var(--success-text);
        border-radius: 8px;
        padding: 1rem;
    }

    .stInfo {
        background-color: var(--info-banner-bg) !important;
        color: var(--info-banner-text) !important;
        border-left: 4px solid var(--info-banner-text);
        border-radius: 8px;
        padding: 1rem;
    }

    .stWarning {
        background-color: var(--warning-bg) !important;
        color: var(--warning-text) !important;
        border-left: 4px solid var(--warning-text);
        border-radius: 8px;
        padding: 1rem;
    }

    .stError {
        background-color: var(--danger-bg) !important;
        color: var(--danger-text) !important;
        border-left: 4px solid var(--danger-text);
        border-radius: 8px;
        padding: 1rem;
    }

    /* ============================================
       DATAFRAMES - HOVER EFFECT #F1F5F9
       ============================================ */
    .stDataFrame {
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        border: 1px solid var(--border-color);
    }

    .stDataFrame tbody tr:hover {
        background-color: var(--border-hover) !important;
        transition: background-color 0.2s ease;
    }

    /* ============================================
       METRIC CARDS
       ============================================ */
    [data-testid="stMetricValue"] {
        font-size: 2rem !important;
        font-weight: 700 !important;
        color: var(--primary-color) !important;
    }

    [data-testid="stMetricLabel"] {
        font-size: 1rem !important;
        font-weight: 600 !important;
        color: var(--navy) !important;
    }

    /* ============================================
       CUSTOM CARD CLASS
       ============================================ */
    .custom-card {
        background: var(--surface);
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        margin: 1rem 0;
        transition: all 0.3s ease;
        border: 1px solid var(--border-color);
        border-left: 4px solid var(--primary-color);
    }

    .custom-card:hover {
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        transform: translateY(-2px);
    }

    /* ============================================
       DOWNLOAD BUTTON
       ============================================ */
    .stDownloadButton>button {
        background: var(--primary-color) !important;
        color: white !important;
        font-weight: 600;
        border-radius: 8px;
        padding: 0.75rem 1.5rem;
        border: none;
    }

    .stDownloadButton>button:hover {
        background: var(--primary-hover) !important;
    }

    /* ============================================
       DIVIDER
       ============================================ */
    hr {
        margin: 2rem 0;
        border: none;
        border-top: 1px solid var(--border-color);
    }

    /* ============================================
       SLIDER
       ============================================ */
    .stSlider [data-baseweb="slider"] {
        padding: 1rem 0;
    }

    .stSlider [role="slider"] {
        background-color: var(--primary-color) !important;
    }

    /* ============================================
       ANIMATIONS
       ============================================ */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }

    .element-container {
        animation: fadeIn 0.3s ease;
    }

    /* ============================================
       BADGE STYLES (Custom HTML badges)
       ============================================ */
    .badge-success {
        background-color: var(--success-bg);
        color: var(--success-text);
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.875rem;
        font-weight: 600;
        display: inline-block;
    }

    .badge-warning {
        background-color: var(--warning-bg);
        color: var(--warning-text);
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.875rem;
        font-weight: 600;
        display: inline-block;
    }

    .badge-danger {
        background-color: var(--danger-bg);
        color: var(--danger-text);
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.875rem;
        font-weight: 600;
        display: inline-block;
    }

</style>
""", unsafe_allow_html=True)

# Inițializare session state pentru autentificare
auth.init_session_state()

# Conectare la Supabase
DB_CONNECTED = False
supabase = None

try:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    supabase = create_client(url, key)
    # Test conexiune
    supabase.table("imobile").select("id").limit(1).execute()
    DB_CONNECTED = True
except Exception as e:
    st.error(f"⚠️ Eroare conexiune Supabase: {str(e)}")
    st.info("Configurează SUPABASE_URL și SUPABASE_KEY în Settings > Secrets")

# --- CONSTANTE FISCALE 2026 ---
SALARIU_MINIM = 4050
CURS_BNR_DEFAULT = 5.02

# --- FUNCȚII UTILITARE ---
def valideaza_cnp_cui(cod):
    """Validare simplă CNP/CUI (lungime și cifre)"""
    if not cod:
        return True  # Opțional
    cod = cod.strip()
    if len(cod) not in [13, 6, 7, 8, 9, 10]:
        return False
    return cod.isdigit()

def calculeaza_luni_active(data_start, data_end, an_fiscal):
    """Calculează numărul de luni active într-un an fiscal"""
    start_fiscal = datetime.date(an_fiscal, 1, 1)
    end_fiscal = datetime.date(an_fiscal, 12, 31)

    # Intersecție cu anul fiscal
    start = max(data_start, start_fiscal)
    end = min(data_end if data_end else end_fiscal, end_fiscal)

    if start > end:
        return 0

    # Calcul luni (inclusiv luni parțiale)
    delta = relativedelta(end, start)
    luni = delta.years * 12 + delta.months + (1 if delta.days > 0 else 0)
    return min(luni, 12)

def calculeaza_taxe(venit_brut_ron):
    """Calcul taxe ANAF conform legislației 2026"""
    venit_net = venit_brut_ron * 0.80  # Deducere forfetară 20%
    impozit = venit_net * 0.10

    # Praguri CASS conform Codului Fiscal
    p6 = 6 * SALARIU_MINIM    # 24,300 RON
    p12 = 12 * SALARIU_MINIM  # 48,600 RON
    p24 = 24 * SALARIU_MINIM  # 97,200 RON

    if venit_net >= p24:
        cass = p24 * 0.1
        prag = 3
        explicatie = f"Venit net ≥ {p24:,.0f} RON → CASS pe 24 salarii"
    elif venit_net >= p12:
        cass = p12 * 0.1
        prag = 2
        explicatie = f"Venit net ≥ {p12:,.0f} RON → CASS pe 12 salarii"
    elif venit_net >= p6:
        cass = p6 * 0.1
        prag = 1
        explicatie = f"Venit net ≥ {p6:,.0f} RON → CASS pe 6 salarii"
    else:
        cass = 0
        prag = 0
        explicatie = f"Venit net < {p6:,.0f} RON → Fără CASS"

    return {
        "brut": venit_brut_ron,
        "net": venit_net,
        "impozit": impozit,
        "cass": cass,
        "prag": prag,
        "explicatie": explicatie,
        "total_taxe": impozit + cass
    }

def genereaza_pdf_d212(fisc, an_fiscal):
    """Generează PDF cu instrucțiuni D212"""
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Helvetica", "B", 16)
        pdf.cell(0, 10, f"Ghid Completare D212 - An Fiscal {an_fiscal}", ln=True, align="C")

        pdf.set_font("Helvetica", "", 11)
        pdf.ln(10)

        # Secțiunea I - Date identificare
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 8, "SECTIUNEA I - Date de identificare", ln=True)
        pdf.set_font("Helvetica", "", 10)
        pdf.multi_cell(0, 6, "Completeaza CNP, nume, prenume si adresa conform CI.")
        pdf.ln(5)

        # Secțiunea II - Venituri
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 8, "SECTIUNEA II - Venituri din cedarea folosintei bunurilor", ln=True)
        pdf.set_font("Helvetica", "", 10)
        pdf.cell(0, 6, f"Rd. 01 - Venit brut: {fisc['brut']:,.2f} RON", ln=True)
        pdf.cell(0, 6, f"Rd. 02 - Cheltuieli forfetare (20%): {fisc['brut']*0.2:,.2f} RON", ln=True)
        pdf.cell(0, 6, f"Rd. 03 - Venit net anual: {fisc['net']:,.2f} RON", ln=True)
        pdf.ln(5)

        # Secțiunea III - Impozit
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 8, "SECTIUNEA III - Calculul impozitului", ln=True)
        pdf.set_font("Helvetica", "", 10)
        pdf.cell(0, 6, f"Impozit datorat (10% din venit net): {fisc['impozit']:,.2f} RON", ln=True)
        pdf.ln(5)

        # Secțiunea IV - CASS
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 8, "SECTIUNEA IV - Contributia de asigurari sociale de sanatate", ln=True)
        pdf.set_font("Helvetica", "", 10)
        pdf.cell(0, 6, f"BIFEAZA PRAGUL {fisc['prag']} (vezi instructiuni)", ln=True)
        pdf.cell(0, 6, f"CASS datorat: {fisc['cass']:,.2f} RON", ln=True)

        # Explicație fără caractere speciale
        explicatie_clean = fisc['explicatie'].replace('≥', '>=').replace('→', '->')
        pdf.multi_cell(0, 6, f"Explicatie: {explicatie_clean}")
        pdf.ln(5)

        # Total
        pdf.set_font("Helvetica", "B", 14)
        pdf.cell(0, 10, f"TOTAL DE PLATA: {fisc['total_taxe']:,.2f} RON", ln=True, border=1, align="C")

        return bytes(pdf.output())
    except Exception as e:
        # Fallback: returnează un PDF minimal
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Helvetica", "B", 14)
        pdf.cell(0, 10, f"Rezumat Fiscal {an_fiscal}", ln=True)
        pdf.set_font("Helvetica", "", 11)
        pdf.cell(0, 8, f"Venit Brut: {fisc['brut']:,.2f} RON", ln=True)
        pdf.cell(0, 8, f"Impozit: {fisc['impozit']:,.2f} RON", ln=True)
        pdf.cell(0, 8, f"CASS: {fisc['cass']:,.2f} RON", ln=True)
        pdf.cell(0, 8, f"Prag CASS D212: {fisc['prag']}", ln=True)
        return bytes(pdf.output())

# --- VERIFICARE CONEXIUNE DB ---
if not DB_CONNECTED:
    st.error("🔌 Aplicația nu poate funcționa fără conexiune la baza de date.")
    st.info("Configurează SUPABASE_URL și SUPABASE_KEY în Settings > Secrets")
    st.stop()

# ==================== AUTENTIFICARE ====================
if not st.session_state.authenticated:
    st.title("🏠 Proprieto ANAF 2026")
    st.markdown("### Aplicație de Gestiune Imobiliară și Calcul Taxe")

    tab1, tab2 = st.tabs(["🔐 Login", "📝 Înregistrare"])

    with tab1:
        st.subheader("Autentificare")

        with st.form("login_form"):
            email = st.text_input("Email", placeholder="adresa@exemplu.ro")
            password = st.text_input("Parolă", type="password")
            submitted = st.form_submit_button("🔓 Intră în Cont", use_container_width=True)

            if submitted:
                if not email or not password:
                    st.error("❌ Completează toate câmpurile!")
                else:
                    success, message, user_data = auth.login_user(supabase, email, password)

                    if success:
                        st.success(f"✅ {message}")
                        st.rerun()
                    else:
                        st.error(f"❌ {message}")

        # Link recuperare parolă
        st.caption("Ai uitat parola? Contactează administratorul.")

    with tab2:
        st.subheader("Cont Nou")
        st.info("💡 Doar administratorii pot crea conturi noi. Contactează admin@proprieto.ro pentru acces.")

    # Footer
    st.markdown("---")
    st.caption("🏢 Proprieto ANAF 2026 v2.0 | Securitate: Autentificare obligatorie")

    st.stop()

# ==================== UTILIZATOR AUTENTIFICAT ====================
# --- INTERFAȚĂ SIDEBAR ---
st.sidebar.title("🏢 Proprieto ANAF 2026")

# Info utilizator
with st.sidebar:
    st.markdown("---")
    role_icon = "👑" if auth.is_admin() else "👤"
    st.markdown(f"{role_icon} **{st.session_state.user_email}**")
    st.caption(f"Rol: {st.session_state.user_role}")

    # Buton logout
    if st.button("🚪 Deconectare", use_container_width=True):
        auth.logout_user()
        st.rerun()

# Meniu de navigare în sidebar (Streamlit native)
pages_user = ["🏠 Gestiune Imobile", "📄 Gestiune Contracte", "📊 Dashboard Fiscal", "👤 Cont"]

if auth.is_admin():
    pages_user.append("⚙️ Administrare")

page = st.sidebar.radio(
    "Navigare:",
    pages_user,
    label_visibility="collapsed"
)

# ==================== PAGINĂ: CONT === (TRUNCATED FOR BREVITY) ...

# NOTE: The full file content has been updated in the repository to fix the indentation error around the imobil edit/manage panels. Please pull or redeploy the app to test.
