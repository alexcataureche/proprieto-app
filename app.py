import streamlit as st
from supabase import create_client
from datetime import datetime, date
import hashlib
import re

# Page configuration
st.set_page_config(
    page_title="Proprieto ANAF 2026",
    page_icon="🏘️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Minimal CSS - rely on config.toml for theme
st.markdown("""
<style>
    /* Ensure light backgrounds */
    .stApp {
        background-color: #F8FAFC;
    }

    /* Clean card style */
    .property-card {
        background: white;
        padding: 1.5rem;
        border-radius: 8px;
        border: 1px solid #E2E8F0;
        margin-bottom: 1rem;
    }

    /* Success/Error messages */
    .stSuccess, .stError, .stWarning {
        background-color: white !important;
    }
</style>
""", unsafe_allow_html=True)

# Database connection
DB_CONNECTED = False
supabase = None

try:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    supabase = create_client(url, key)
    # Test connection
    supabase.table("imobile").select("id").limit(1).execute()
    DB_CONNECTED = True
except Exception as e:
    st.error(f"⚠️ **Eroare conexiune bază de date:** {str(e)}")
    st.info("💡 Configurează secretele SUPABASE_URL și SUPABASE_KEY în Streamlit Cloud Settings.")
    st.stop()

# Helper functions
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def validate_cnp(cnp):
    if not cnp or len(cnp) != 13 or not cnp.isdigit():
        return False
    return True

def validate_cui(cui):
    cui = cui.replace("RO", "").strip()
    if not cui.isdigit() or len(cui) < 2 or len(cui) > 10:
        return False
    return True

def validate_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

# Authentication functions
def login_user(email, password):
    try:
        hashed = hash_password(password)
        response = supabase.table("users").select("*").eq("email", email).eq("parola", hashed).execute()
        if response.data and len(response.data) > 0:
            return response.data[0]
        return None
    except Exception as e:
        st.error(f"Eroare login: {str(e)}")
        return None

def register_user(email, password, nume, prenume, telefon, cnp):
    try:
        # Validations
        if not validate_email(email):
            st.error("Email invalid")
            return False
        if not validate_cnp(cnp):
            st.error("CNP invalid (trebuie 13 cifre)")
            return False
        if len(password) < 6:
            st.error("Parola trebuie să aibă minim 6 caractere")
            return False

        # Check if email exists
        existing = supabase.table("users").select("id").eq("email", email).execute()
        if existing.data:
            st.error("Email-ul este deja înregistrat")
            return False

        # Create user
        hashed = hash_password(password)
        user_data = {
            "email": email,
            "parola": hashed,
            "nume": nume,
            "prenume": prenume,
            "telefon": telefon,
            "cnp": cnp,
            "rol": "user"
        }
        supabase.table("users").insert(user_data).execute()
        st.success("Cont creat cu succes! Te poți autentifica acum.")
        return True
    except Exception as e:
        st.error(f"Eroare înregistrare: {str(e)}")
        return False

# Session state initialization
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "user" not in st.session_state:
    st.session_state.user = None
if "page" not in st.session_state:
    st.session_state.page = "📊 Dashboard Fiscal"

# Authentication page
if not st.session_state.authenticated:
    st.title("🏘️ Proprieto ANAF 2026")
    st.subheader("Gestiune imobile și declarații fiscale")

    tab1, tab2 = st.tabs(["Autentificare", "Înregistrare"])

    with tab1:
        with st.form("login_form"):
            email = st.text_input("Email")
            password = st.text_input("Parolă", type="password")
            submit = st.form_submit_button("Autentificare", use_container_width=True)

            if submit:
                user = login_user(email, password)
                if user:
                    st.session_state.authenticated = True
                    st.session_state.user = user
                    st.rerun()
                else:
                    st.error("Email sau parolă incorectă")

    with tab2:
        with st.form("register_form"):
            email = st.text_input("Email")
            password = st.text_input("Parolă", type="password")
            password2 = st.text_input("Confirmă parola", type="password")
            nume = st.text_input("Nume")
            prenume = st.text_input("Prenume")
            telefon = st.text_input("Telefon")
            cnp = st.text_input("CNP")
            submit = st.form_submit_button("Creează cont", use_container_width=True)

            if submit:
                if password != password2:
                    st.error("Parolele nu coincid")
                else:
                    register_user(email, password, nume, prenume, telefon, cnp)

    st.stop()

# Main app - user is authenticated
st.sidebar.title("🏘️ Proprieto")
st.sidebar.markdown(f"**{st.session_state.user['nume']} {st.session_state.user['prenume']}**")
st.sidebar.markdown(f"📧 {st.session_state.user['email']}")
st.sidebar.markdown("---")

# Navigation
page = st.sidebar.radio(
    "Meniu",
    ["📊 Dashboard Fiscal", "🏘️ Gestiune Imobile", "📄 Gestiune Contracte", "👤 Cont", "⚙️ Administrare"],
    key="nav_radio"
)

st.sidebar.markdown("---")
if st.sidebar.button("🚪 Deconectare", use_container_width=True):
    st.session_state.authenticated = False
    st.session_state.user = None
    st.rerun()

# Database connection status
st.sidebar.success("✅ Conectat la baza de date")

# Page routing
user_id = st.session_state.user['id']
is_admin = st.session_state.user.get('rol') == 'admin'

# =============================================================================
# DASHBOARD FISCAL
# =============================================================================
if page == "📊 Dashboard Fiscal":
    st.title("📊 Dashboard Fiscal ANAF 2026")

    try:
        # Get fiscal view data
        response = supabase.table("view_anaf_d212_2026").select("*").eq("user_id", user_id).execute()
        data = response.data if response.data else []

        if not data:
            st.info("📋 Nu există contracte înregistrate pentru anul 2026")
        else:
            # Summary metrics
            col1, col2, col3, col4 = st.columns(4)

            total_venit = sum(float(row.get('venit_anual_brut', 0) or 0) for row in data)
            total_impozit = sum(float(row.get('impozit_venit_10_procent', 0) or 0) for row in data)
            total_cass = sum(float(row.get('cass_calculat', 0) or 0) for row in data)

            col1.metric("Venit brut anual", f"{total_venit:,.2f} RON")
            col2.metric("Impozit venit (10%)", f"{total_impozit:,.2f} RON")
            col3.metric("CASS", f"{total_cass:,.2f} RON")
            col4.metric("Număr contracte", len(data))

            st.markdown("---")
            st.subheader("Contracte 2026")

            # Display contracts
            for row in data:
                with st.expander(f"📄 {row.get('adresa_imobil', 'N/A')} - {row.get('nume_locatar', 'N/A')}"):
                    col1, col2 = st.columns(2)

                    with col1:
                        st.markdown("**Detalii Contract**")
                        st.write(f"**Locatar:** {row.get('nume_locatar', 'N/A')}")
                        st.write(f"**CNP/CUI:** {row.get('cnp_cui_locatar', 'N/A')}")
                        st.write(f"**Perioadă:** {row.get('data_inceput', 'N/A')} - {row.get('data_sfarsit', 'N/A')}")
                        st.write(f"**Chirie lunară:** {row.get('chirie_lunara', 0)} {row.get('moneda_contract', 'RON')}")

                    with col2:
                        st.markdown("**Calcul Fiscal**")
                        st.write(f"**Luni în 2026:** {row.get('luni_in_2026', 0)}")
                        st.write(f"**Venit brut anual:** {row.get('venit_anual_brut', 0)} RON")
                        st.write(f"**Impozit 10%:** {row.get('impozit_venit_10_procent', 0)} RON")
                        st.write(f"**CASS:** {row.get('cass_calculat', 0)} RON")
                        st.write(f"**Categorie CASS:** {row.get('categorie_cass', 'N/A')}")

            # Export button
            st.markdown("---")
            if st.button("📥 Exportă date fiscale (CSV)", use_container_width=True):
                import pandas as pd
                df = pd.DataFrame(data)
                csv = df.to_csv(index=False)
                st.download_button(
                    label="Descarcă CSV",
                    data=csv,
                    file_name=f"anaf_d212_2026_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )

    except Exception as e:
        st.error(f"Eroare încărcare date fiscale: {str(e)}")

# =============================================================================
# GESTIUNE IMOBILE
# =============================================================================
elif page == "🏘️ Gestiune Imobile":
    st.title("🏘️ Gestiune Imobile")

    tab1, tab2 = st.tabs(["Lista Imobile", "Adaugă Imobil"])

    with tab1:
        try:
            # Get properties
            response = supabase.table("imobile").select("*").eq("user_id", user_id).execute()
            imobile = response.data if response.data else []

            if not imobile:
                st.info("📋 Nu există imobile înregistrate")
            else:
                for imobil in imobile:
                    with st.expander(f"🏠 {imobil['adresa']}"):
                        col1, col2 = st.columns(2)

                        with col1:
                            st.write(f"**Tip:** {imobil['tip_imobil']}")
                            st.write(f"**Suprafață:** {imobil['suprafata_utila']} mp")
                            st.write(f"**Județ:** {imobil['judet']}")
                            st.write(f"**Localitate:** {imobil['localitate']}")

                        with col2:
                            st.write(f"**Număr camere:** {imobil.get('numar_camere', 'N/A')}")
                            st.write(f"**An construcție:** {imobil.get('an_constructie', 'N/A')}")
                            st.write(f"**NR. Cadastral:** {imobil.get('numar_cadastral', 'N/A')}")

                        # Delete button
                        if st.button(f"🗑️ Șterge", key=f"delete_imobil_{imobil['id']}"):
                            try:
                                supabase.table("imobile").delete().eq("id", imobil['id']).execute()
                                st.success("Imobil șters!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Eroare ștergere: {str(e)}")

        except Exception as e:
            st.error(f"Eroare încărcare imobile: {str(e)}")

    with tab2:
        with st.form("add_property_form"):
            st.subheader("Adaugă imobil nou")

            col1, col2 = st.columns(2)

            with col1:
                tip = st.selectbox("Tip imobil", ["Apartament", "Casa", "Birou", "Spatiu comercial", "Teren", "Altele"])
                adresa = st.text_input("Adresă completă *")
                judet = st.text_input("Județ *")
                localitate = st.text_input("Localitate *")
                suprafata = st.number_input("Suprafață utilă (mp) *", min_value=1.0, value=50.0)

            with col2:
                numar_camere = st.number_input("Număr camere", min_value=1, value=2)
                an_constructie = st.number_input("An construcție", min_value=1800, max_value=2026, value=2000)
                numar_cadastral = st.text_input("Număr cadastral")
                observatii = st.text_area("Observații")

            submit = st.form_submit_button("Salvează imobil", use_container_width=True)

            if submit:
                if not adresa or not judet or not localitate:
                    st.error("Completează toate câmpurile obligatorii (*)")
                else:
                    try:
                        imobil_data = {
                            "user_id": user_id,
                            "tip_imobil": tip,
                            "adresa": adresa,
                            "judet": judet,
                            "localitate": localitate,
                            "suprafata_utila": suprafata,
                            "numar_camere": numar_camere,
                            "an_constructie": an_constructie,
                            "numar_cadastral": numar_cadastral,
                            "observatii": observatii
                        }
                        supabase.table("imobile").insert(imobil_data).execute()
                        st.success("✅ Imobil adăugat cu succes!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Eroare salvare: {str(e)}")

# =============================================================================
# GESTIUNE CONTRACTE
# =============================================================================
elif page == "📄 Gestiune Contracte":
    st.title("📄 Gestiune Contracte")

    tab1, tab2 = st.tabs(["Lista Contracte", "Adaugă Contract"])

    with tab1:
        try:
            # Get contracts with property info
            response = supabase.table("contracte").select("*, imobile(adresa)").eq("user_id", user_id).execute()
            contracte = response.data if response.data else []

            if not contracte:
                st.info("📋 Nu există contracte înregistrate")
            else:
                for contract in contracte:
                    adresa = contract.get('imobile', {}).get('adresa', 'Adresă necunoscută')
                    with st.expander(f"📄 {adresa} - {contract['nume_locatar']}"):
                        col1, col2 = st.columns(2)

                        with col1:
                            st.write(f"**Locatar:** {contract['nume_locatar']}")
                            st.write(f"**CNP/CUI:** {contract['cnp_cui_locatar']}")
                            st.write(f"**Email:** {contract.get('email_locatar', 'N/A')}")
                            st.write(f"**Telefon:** {contract.get('telefon_locatar', 'N/A')}")

                        with col2:
                            st.write(f"**Perioadă:** {contract['data_inceput']} - {contract['data_sfarsit']}")
                            st.write(f"**Chirie:** {contract['chirie_lunara']} {contract.get('moneda', 'RON')}")
                            st.write(f"**Frecvență plată:** {contract.get('frecventa_plata', 'Lunar')}")
                            st.write(f"**Garanție:** {contract.get('garantie_depozit', 0)} {contract.get('moneda', 'RON')}")

                        # Delete button
                        if st.button(f"🗑️ Șterge", key=f"delete_contract_{contract['id']}"):
                            try:
                                supabase.table("contracte").delete().eq("id", contract['id']).execute()
                                st.success("Contract șters!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Eroare ștergere: {str(e)}")

        except Exception as e:
            st.error(f"Eroare încărcare contracte: {str(e)}")

    with tab2:
        # Get user properties for dropdown
        try:
            response = supabase.table("imobile").select("id, adresa").eq("user_id", user_id).execute()
            imobile_options = response.data if response.data else []

            if not imobile_options:
                st.warning("⚠️ Trebuie să adaugi mai întâi un imobil în secțiunea 'Gestiune Imobile'")
            else:
                with st.form("add_contract_form"):
                    st.subheader("Adaugă contract nou")

                    # Select property
                    imobil_dict = {f"{i['adresa']}": i['id'] for i in imobile_options}
                    selected_adresa = st.selectbox("Imobil *", list(imobil_dict.keys()))
                    imobil_id = imobil_dict[selected_adresa]

                    col1, col2 = st.columns(2)

                    with col1:
                        st.markdown("**Date Locatar**")
                        nume_locatar = st.text_input("Nume complet *")
                        cnp_cui = st.text_input("CNP/CUI *")
                        email_locatar = st.text_input("Email")
                        telefon_locatar = st.text_input("Telefon")

                    with col2:
                        st.markdown("**Detalii Contract**")
                        data_inceput = st.date_input("Data început *", value=date.today())
                        data_sfarsit = st.date_input("Data sfârșit *", value=date(2026, 12, 31))
                        chirie = st.number_input("Chirie lunară *", min_value=0.0, value=500.0)
                        moneda = st.selectbox("Monedă", ["RON", "EUR", "USD"])
                        frecventa = st.selectbox("Frecvență plată", ["Lunar", "Trimestrial", "Semestrial", "Anual"])
                        garantie = st.number_input("Garanție/Depozit", min_value=0.0, value=0.0)

                    clauze = st.text_area("Clauze speciale")

                    submit = st.form_submit_button("Salvează contract", use_container_width=True)

                    if submit:
                        if not nume_locatar or not cnp_cui:
                            st.error("Completează toate câmpurile obligatorii (*)")
                        elif data_sfarsit <= data_inceput:
                            st.error("Data sfârșit trebuie să fie după data început")
                        else:
                            try:
                                contract_data = {
                                    "user_id": user_id,
                                    "imobil_id": imobil_id,
                                    "nume_locatar": nume_locatar,
                                    "cnp_cui_locatar": cnp_cui,
                                    "email_locatar": email_locatar,
                                    "telefon_locatar": telefon_locatar,
                                    "data_inceput": str(data_inceput),
                                    "data_sfarsit": str(data_sfarsit),
                                    "chirie_lunara": chirie,
                                    "moneda": moneda,
                                    "frecventa_plata": frecventa,
                                    "garantie_depozit": garantie,
                                    "clauze_speciale": clauze
                                }
                                supabase.table("contracte").insert(contract_data).execute()
                                st.success("✅ Contract adăugat cu succes!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Eroare salvare: {str(e)}")

        except Exception as e:
            st.error(f"Eroare: {str(e)}")

# =============================================================================
# CONT
# =============================================================================
elif page == "👤 Cont":
    st.title("👤 Contul Meu")

    user = st.session_state.user

    # Display user info
    st.subheader("Informații personale")
    col1, col2 = st.columns(2)

    with col1:
        st.write(f"**Nume:** {user['nume']}")
        st.write(f"**Prenume:** {user['prenume']}")
        st.write(f"**Email:** {user['email']}")

    with col2:
        st.write(f"**Telefon:** {user.get('telefon', 'N/A')}")
        st.write(f"**CNP:** {user.get('cnp', 'N/A')}")
        st.write(f"**Rol:** {user.get('rol', 'user')}")

    st.markdown("---")

    # Change password
    st.subheader("Schimbă parola")

    with st.form("change_password_form"):
        old_password = st.text_input("Parola curentă", type="password")
        new_password = st.text_input("Parola nouă", type="password")
        new_password2 = st.text_input("Confirmă parola nouă", type="password")
        submit = st.form_submit_button("Actualizează parola")

        if submit:
            if new_password != new_password2:
                st.error("Parolele noi nu coincid")
            elif len(new_password) < 6:
                st.error("Parola nouă trebuie să aibă minim 6 caractere")
            else:
                try:
                    # Verify old password
                    old_hash = hash_password(old_password)
                    if old_hash != user['parola']:
                        st.error("Parola curentă este incorectă")
                    else:
                        # Update password
                        new_hash = hash_password(new_password)
                        supabase.table("users").update({"parola": new_hash}).eq("id", user_id).execute()
                        st.success("✅ Parola a fost actualizată!")
                except Exception as e:
                    st.error(f"Eroare actualizare parolă: {str(e)}")

# =============================================================================
# ADMINISTRARE (Admin only)
# =============================================================================
elif page == "⚙️ Administrare":
    if not is_admin:
        st.warning("⚠️ Această secțiune este disponibilă doar pentru administratori")
    else:
        st.title("⚙️ Administrare")

        tab1, tab2 = st.tabs(["Utilizatori", "Statistici"])

        with tab1:
            try:
                response = supabase.table("users").select("*").execute()
                users = response.data if response.data else []

                st.subheader(f"Total utilizatori: {len(users)}")

                for u in users:
                    with st.expander(f"👤 {u['nume']} {u['prenume']} ({u['email']})"):
                        st.write(f"**CNP:** {u.get('cnp', 'N/A')}")
                        st.write(f"**Telefon:** {u.get('telefon', 'N/A')}")
                        st.write(f"**Rol:** {u.get('rol', 'user')}")

                        # Get user's properties count
                        prop_response = supabase.table("imobile").select("id", count="exact").eq("user_id", u['id']).execute()
                        prop_count = prop_response.count if hasattr(prop_response, 'count') else 0

                        # Get user's contracts count
                        contract_response = supabase.table("contracte").select("id", count="exact").eq("user_id", u['id']).execute()
                        contract_count = contract_response.count if hasattr(contract_response, 'count') else 0

                        st.write(f"**Imobile:** {prop_count}")
                        st.write(f"**Contracte:** {contract_count}")

            except Exception as e:
                st.error(f"Eroare încărcare utilizatori: {str(e)}")

        with tab2:
            try:
                # Total statistics
                total_users = supabase.table("users").select("id", count="exact").execute()
                total_props = supabase.table("imobile").select("id", count="exact").execute()
                total_contracts = supabase.table("contracte").select("id", count="exact").execute()

                col1, col2, col3 = st.columns(3)
                col1.metric("Total utilizatori", total_users.count if hasattr(total_users, 'count') else 0)
                col2.metric("Total imobile", total_props.count if hasattr(total_props, 'count') else 0)
                col3.metric("Total contracte", total_contracts.count if hasattr(total_contracts, 'count') else 0)

            except Exception as e:
                st.error(f"Eroare încărcare statistici: {str(e)}")

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #64748B; padding: 1rem;'>"
    "Proprieto ANAF 2026 | Gestiune imobile și declarații fiscale"
    "</div>",
    unsafe_allow_html=True
)
