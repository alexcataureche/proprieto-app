import streamlit as st
import pandas as pd
from supabase import create_client
from fpdf import FPDF
from io import BytesIO
import datetime
from dateutil.relativedelta import relativedelta
import auth  # Modul de autentificare
import coproprietate  # Modul de co-proprietate

# --- CONFIGURARE ---
st.set_page_config(page_title="Proprieto 2026", layout="wide", page_icon="🏠")

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

# Meniu de navigare
pages_user = ["📊 Dashboard Fiscal", "🏠 Gestiune Imobile", "📄 Gestiune Contracte", "👤 Cont"]

if auth.is_admin():
    pages_user.append("⚙️ Administrare")

page = st.sidebar.radio("Navigare:", pages_user)

# ==================== PAGINĂ: CONT ====================
if page == "👤 Cont":
    st.title("👤 Contul Meu")

    tab1, tab2, tab3 = st.tabs(["📋 Informații", "✏️ Editează Profil", "🔒 Schimbă Parola"])

    with tab1:
        st.subheader("Informații Cont")

        col1, col2 = st.columns(2)
        with col1:
            st.text_input("Email", value=st.session_state.user_email, disabled=True)
            st.text_input("Nume", value=st.session_state.get('user_name', 'N/A'), disabled=True)
        with col2:
            st.text_input("Rol", value=st.session_state.user_role, disabled=True)

            # Afișare dată înregistrare și ultimul login
            try:
                user_info = supabase.table("users").select("created_at, last_login").eq("id", st.session_state.user_id).execute()
                if user_info.data:
                    created_at = pd.to_datetime(user_info.data[0]['created_at']).strftime('%d-%m-%Y')
                    last_login = pd.to_datetime(user_info.data[0]['last_login']).strftime('%d-%m-%Y %H:%M') if user_info.data[0].get('last_login') else 'N/A'
                    st.text_input("Înregistrat", value=created_at, disabled=True)
                    st.text_input("Ultimul login", value=last_login, disabled=True)
            except:
                pass

        st.markdown("---")
        st.info("💡 Pentru a edita numele sau parola, folosește tab-urile de mai sus.")

    with tab2:
        st.subheader("✏️ Editează Profil")

        st.markdown("#### Informații Personale")

        with st.form("edit_profile_form"):
            current_name = st.session_state.get('user_name', st.session_state.user_email)

            new_name = st.text_input(
                "Nume Complet",
                value=current_name,
                placeholder="ex: Popescu Ion",
                help="Numele afișat în aplicație"
            )

            st.caption("📧 Email-ul nu poate fi modificat pentru securitate")

            col_save, col_cancel = st.columns(2)

            with col_save:
                submitted_profile = st.form_submit_button("💾 Salvează", use_container_width=True, type="primary")

            if submitted_profile:
                if not new_name.strip():
                    st.error("❌ Numele nu poate fi gol!")
                elif len(new_name.strip()) < 3:
                    st.error("❌ Numele trebuie să aibă minim 3 caractere!")
                elif len(new_name.strip()) > 100:
                    st.error("❌ Numele este prea lung (max 100 caractere)")
                else:
                    try:
                        # Actualizează numele în baza de date
                        supabase.table("users").update({
                            "nume": new_name.strip()
                        }).eq("id", st.session_state.user_id).execute()

                        # Actualizează session state
                        st.session_state.user_name = new_name.strip()

                        st.success(f"✅ Profil actualizat cu succes!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Eroare la actualizare: {str(e)}")

    with tab3:
        st.subheader("🔒 Schimbă Parola")

        st.markdown("#### Requisites Parolă")
        st.info("""
        ✅ Minim 8 caractere
        ✅ Recomandat: combinație de litere, cifre și caractere speciale
        ✅ Nu folosi parole ușor de ghicit (ex: 123456, password, etc.)
        """)

        with st.form("change_password_form"):
            old_pwd = st.text_input("Parola Curentă*", type="password", placeholder="Introdu parola curentă")

            st.markdown("---")

            new_pwd = st.text_input("Parolă Nouă*", type="password", placeholder="Minim 8 caractere")

            # Indicator putere parolă
            if new_pwd:
                strength = 0
                feedback = []

                if len(new_pwd) >= 8:
                    strength += 1
                else:
                    feedback.append("❌ Prea scurtă (minim 8 caractere)")

                if len(new_pwd) >= 12:
                    strength += 1
                    feedback.append("✅ Lungime bună")

                if any(c.isupper() for c in new_pwd) and any(c.islower() for c in new_pwd):
                    strength += 1
                    feedback.append("✅ Conține litere mari și mici")
                else:
                    feedback.append("⚠️ Adaugă litere mari și mici")

                if any(c.isdigit() for c in new_pwd):
                    strength += 1
                    feedback.append("✅ Conține cifre")
                else:
                    feedback.append("⚠️ Adaugă cifre")

                if any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in new_pwd):
                    strength += 1
                    feedback.append("✅ Conține caractere speciale")
                else:
                    feedback.append("💡 Opțional: adaugă caractere speciale")

                # Afișare indicator putere
                if strength <= 2:
                    st.warning(f"🔴 **Parolă Slabă** ({strength}/5)")
                elif strength <= 3:
                    st.info(f"🟡 **Parolă Medie** ({strength}/5)")
                else:
                    st.success(f"🟢 **Parolă Puternică** ({strength}/5)")

                # Afișare feedback
                for fb in feedback:
                    st.caption(fb)

            confirm_pwd = st.text_input("Confirmă Parola Nouă*", type="password", placeholder="Re-introdu parola nouă")

            st.markdown("---")

            col_submit, col_info = st.columns([1, 2])

            with col_submit:
                submitted = st.form_submit_button("🔒 Schimbă Parola", use_container_width=True, type="primary")

            with col_info:
                st.caption("⚠️ Vei rămâne autentificat după schimbarea parolei")

            if submitted:
                erori = []

                if not old_pwd or not new_pwd or not confirm_pwd:
                    erori.append("Toate câmpurile sunt obligatorii")

                if len(new_pwd) < 8:
                    erori.append("Parola nouă trebuie să aibă minim 8 caractere")

                if new_pwd != confirm_pwd:
                    erori.append("Parolele noi nu se potrivesc")

                if old_pwd == new_pwd:
                    erori.append("Parola nouă trebuie să fie diferită de cea veche")

                if erori:
                    for err in erori:
                        st.error(f"❌ {err}")
                else:
                    success, message = auth.change_password(
                        supabase,
                        st.session_state.user_id,
                        old_pwd,
                        new_pwd
                    )

                    if success:
                        st.success(f"✅ {message}")
                        st.balloons()
                        st.info("💡 Parola a fost schimbată cu succes! Poți continua să folosești aplicația.")
                    else:
                        st.error(f"❌ {message}")


# ==================== PAGINĂ: ADMINISTRARE ====================
elif page == "⚙️ Administrare" and auth.is_admin():
    import admin_panel

    st.title("⚙️ Panou Administrare")

    admin_tab = st.tabs(["👥 Utilizatori", "📊 Date Generale", "⚙️ Setări Sistem"])

    with admin_tab[0]:
        admin_panel.show_users_management(supabase)

    with admin_tab[1]:
        admin_panel.show_data_overview(supabase, st.session_state.user_id, True)

    with admin_tab[2]:
        admin_panel.show_system_settings(supabase)

# ==================== PAGINA 1: DASHBOARD FISCAL ====================
if page == "📊 Dashboard Fiscal":
    st.title("📊 Monitorizare Venituri și Calculatoare Fiscale")

    # Filtrare pentru admini
    is_admin = auth.is_admin()
    selected_user_id = None

    if is_admin:
        # Admini pot filtra după utilizator
        try:
            users_result = supabase.table("users").select("id, email, nume").order("nume").execute()
            if users_result.data:
                user_options = {u['id']: f"{u['nume']} ({u['email']})" for u in users_result.data}
                user_options['all'] = "🌐 Toți utilizatorii (consolidat)"
                user_options[st.session_state.user_id] = f"👤 {user_options.get(st.session_state.user_id, 'Contul meu')}"

                col_filter, col_year, col_curs = st.columns([2, 1, 1])
                with col_filter:
                    selected_filter = st.selectbox(
                        "Vizualizare date pentru:",
                        options=['all', st.session_state.user_id] + [k for k in user_options.keys() if k not in ['all', st.session_state.user_id]],
                        format_func=lambda x: user_options.get(x, x),
                        index=0
                    )
                    selected_user_id = None if selected_filter == 'all' else selected_filter
                with col_year:
                    an_fiscal = st.selectbox("An Fiscal", [2025, 2026], index=1)
                with col_curs:
                    curs = st.number_input("Curs BNR", value=CURS_BNR_DEFAULT, min_value=1.0, max_value=10.0, step=0.01)
        except:
            st.warning("Eroare la încărcarea utilizatorilor")
            col_year, col_curs = st.columns(2)
            with col_year:
                an_fiscal = st.selectbox("An Fiscal", [2025, 2026], index=1)
            with col_curs:
                curs = st.number_input("Curs Mediu BNR (EUR→RON)", value=CURS_BNR_DEFAULT, min_value=1.0, max_value=10.0, step=0.01)
    else:
        # Useri văd doar propriile date
        selected_user_id = st.session_state.user_id
        col_settings = st.columns([2, 1])
        with col_settings[0]:
            an_fiscal = st.selectbox("An Fiscal", [2025, 2026], index=1)
        with col_settings[1]:
            curs = st.number_input("Curs Mediu BNR (EUR→RON)", value=CURS_BNR_DEFAULT, min_value=1.0, max_value=10.0, step=0.01)

    try:
        # Preluare date (cu sau fără filtrare după utilizator)
        if selected_user_id:
            # Filtrare pentru un singur utilizator
            res = supabase.table("contracte").select("*, imobile(procent_proprietate, nume), users(nume, email)").eq("user_id", selected_user_id).execute()
        else:
            # Toate datele (doar pentru admini)
            res = supabase.table("contracte").select("*, imobile(procent_proprietate, nume), users(nume, email)").execute()

        if not res.data:
            st.info("📭 Nu există contracte înregistrate. Mergi la **Gestiune Contracte** pentru a adăuga primul contract.")
        else:
            df = pd.DataFrame(res.data)

            # Calcul venituri cu perioadă activă
            venituri = []
            for _, contract in df.iterrows():
                try:
                    data_start = datetime.datetime.strptime(contract['data_inceput'], '%Y-%m-%d').date()
                    data_end = datetime.datetime.strptime(contract['data_sfarsit'], '%Y-%m-%d').date() if contract.get('data_sfarsit') else None

                    luni_active = calculeaza_luni_active(data_start, data_end, an_fiscal)
                    chirie_anuala = contract['chirie_lunara'] * luni_active
                    chirie_cota = chirie_anuala * (contract['imobile']['procent_proprietate'] / 100)

                    venit_ron = chirie_cota * (curs if contract['moneda'] == 'EUR' else 1)

                    venit_data = {
                        'Imobil': contract['imobile']['nume'],
                        'Locatar': contract['locatar'],
                        'Chirie/lună': f"{contract['chirie_lunara']:,.2f} {contract['moneda']}",
                        'Luni active': luni_active,
                        'Cotă proprietate': f"{contract['imobile']['procent_proprietate']}%",
                        'Venit RON': venit_ron
                    }

                    # Adaugă coloana Proprietar pentru admini când vizualizează toți userii
                    if is_admin and not selected_user_id and contract.get('users'):
                        venit_data = {
                            'Proprietar': contract['users']['nume'],
                            **venit_data
                        }

                    venituri.append(venit_data)
                except Exception as e:
                    st.warning(f"⚠️ Eroare la procesarea contractului {contract.get('nr_contract', 'N/A')}: {str(e)}")

            if venituri:
                df_venituri = pd.DataFrame(venituri)
                total_brut = df_venituri['Venit RON'].sum()

                # Calcul taxe
                fisc = calculeaza_taxe(total_brut)

                # METRICS
                st.markdown("### 💰 Situație Fiscală Anuală")
                m1, m2, m3, m4 = st.columns(4)
                m1.metric("Venit Brut", f"{fisc['brut']:,.2f} RON")
                m2.metric("Impozit (10%)", f"{fisc['impozit']:,.2f} RON", delta=None, delta_color="inverse")
                m3.metric("CASS", f"{fisc['cass']:,.2f} RON", delta=None, delta_color="inverse")
                m4.metric("TOTAL TAXE", f"{fisc['total_taxe']:,.2f} RON", delta=None, delta_color="inverse")

                # Explicație CASS
                st.info(f"💡 **Instrucțiune D212:** {fisc['explicatie']} → Bifează **Pragul {fisc['prag']}** la secțiunea CASS.")

                # Tabel detaliat
                st.markdown("### 📋 Detalii pe Contract")
                st.dataframe(df_venituri, use_container_width=True, hide_index=True)

                # EXPORT-URI
                st.markdown("### 📥 Export Rapoarte")
                col_exp1, col_exp2 = st.columns(2)

                with col_exp1:
                    # Export Excel
                    buffer_excel = BytesIO()
                    with pd.ExcelWriter(buffer_excel, engine='openpyxl') as writer:
                        df_venituri.to_excel(writer, sheet_name='Venituri', index=False)

                        # Sheet cu rezumat fiscal
                        df_fiscal = pd.DataFrame([{
                            'An Fiscal': an_fiscal,
                            'Venit Brut (RON)': fisc['brut'],
                            'Venit Net (RON)': fisc['net'],
                            'Impozit (RON)': fisc['impozit'],
                            'CASS (RON)': fisc['cass'],
                            'Total Taxe (RON)': fisc['total_taxe'],
                            'Prag CASS D212': fisc['prag']
                        }])
                        df_fiscal.to_excel(writer, sheet_name='Rezumat Fiscal', index=False)

                    st.download_button(
                        "📊 Descarcă Excel Complet",
                        buffer_excel.getvalue(),
                        f"Proprieto_Raport_{an_fiscal}.xlsx",
                        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )

                with col_exp2:
                    # Export PDF D212
                    pdf_bytes = genereaza_pdf_d212(fisc, an_fiscal)
                    st.download_button(
                        "📄 Ghid Completare D212 (PDF)",
                        pdf_bytes,
                        f"Ghid_D212_{an_fiscal}.pdf",
                        "application/pdf"
                    )

    except Exception as e:
        st.error(f"❌ Eroare la încărcarea datelor: {str(e)}")

# ==================== PAGINA 2: GESTIUNE IMOBILE ====================
elif page == "🏠 Gestiune Imobile":
    st.title("🏠 Gestiune Portofoliu Imobiliar")

    # Formular adăugare
    with st.expander("➕ Adaugă Imobil Nou", expanded=True):
        tab1, tab2 = st.tabs(["👤 Proprietate Singulară", "👥 Co-proprietate"])

        with tab1:
            # Formular clasic - un singur proprietar
            with st.form("imobil_form_single"):
                col1, col2 = st.columns(2)
                with col1:
                    nume = st.text_input("Nume Identificare*", placeholder="ex: Apartament Centru")
                with col2:
                    adr = st.text_input("Adresă Completă", placeholder="ex: Str. Victoriei nr. 10, București")

                proc = st.slider("Procent Proprietate (%)", 0, 100, 100, help="Cotă de proprietate deținută")

                submitted = st.form_submit_button("💾 Salvează Imobil", use_container_width=True)

                if submitted:
                    if not nume.strip():
                        st.error("❌ Numele imobilului este obligatoriu!")
                    elif len(nume) > 100:
                        st.error("❌ Numele este prea lung (max 100 caractere)")
                    else:
                        try:
                            # Creează imobilul
                            result = supabase.table("imobile").insert({
                                "nume": nume.strip(),
                                "adresa": adr.strip() if adr else None,
                                "procent_proprietate": proc,
                                "user_id": st.session_state.user_id
                            }).execute()

                            # Adaugă în tabelul de legătură
                            if result.data:
                                imobil_id = result.data[0]['id']
                                supabase.table("imobile_proprietari").insert({
                                    "imobil_id": imobil_id,
                                    "user_id": st.session_state.user_id,
                                    "procent_proprietate": proc
                                }).execute()

                            st.success(f"✅ Imobil '{nume}' a fost înregistrat!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ Eroare la salvare: {str(e)}")

        with tab2:
            # Formular co-proprietate - multipli proprietari
            st.info("💡 Creează un imobil cu multipli co-proprietari. Suma procentelor trebuie să fie 100%.")

            with st.form("imobil_form_copro"):
                col1, col2 = st.columns(2)
                with col1:
                    nume_copro = st.text_input("Nume Identificare*", placeholder="ex: Apartament Centru", key="nume_copro")
                with col2:
                    adr_copro = st.text_input("Adresă Completă", placeholder="ex: Str. Victoriei nr. 10, București", key="adr_copro")

                st.markdown("### 👥 Co-proprietari")

                # Preluare lista utilizatori pentru selecție
                try:
                    users_list = supabase.table("users").select("id, nume, email").eq("active", True).order("nume").execute()
                    users_dict = {u['id']: f"{u['nume']} ({u['email']})" for u in users_list.data}
                except:
                    users_dict = {}
                    st.error("Eroare la încărcarea utilizatorilor")

                # Proprietarul 1 (utilizatorul curent)
                user_display_name = st.session_state.get('user_name', st.session_state.get('user_email', 'Utilizator'))
                st.markdown(f"**Proprietar 1:** {user_display_name} (Tu)")
                procent1 = st.slider("Procent proprietate (%)", 0, 100, 50, key="proc1")

                # Proprietarul 2
                if users_dict:
                    other_users = {k: v for k, v in users_dict.items() if k != st.session_state.user_id}
                    if other_users:
                        st.markdown("**Proprietar 2:**")
                        user2_id = st.selectbox("Selectează co-proprietar", options=list(other_users.keys()),
                                               format_func=lambda x: other_users[x], key="user2")
                        procent2 = st.slider("Procent proprietate (%)", 0, 100, 50, key="proc2")

                        # Afișare sumă procentă
                        suma_procente = procent1 + procent2
                        if suma_procente == 100:
                            st.success(f"✅ Suma procentelor: {suma_procente}% (Corect!)")
                        else:
                            st.warning(f"⚠️ Suma procentelor: {suma_procente}% (Trebuie să fie 100%)")

                        submitted_copro = st.form_submit_button("💾 Creează Co-proprietate", use_container_width=True)

                        if submitted_copro:
                            if not nume_copro.strip():
                                st.error("❌ Numele imobilului este obligatoriu!")
                            elif suma_procente != 100:
                                st.error(f"❌ Suma procentelor trebuie să fie 100% (acum: {suma_procente}%)")
                            else:
                                proprietari_list = [
                                    {"user_id": st.session_state.user_id, "procent": procent1},
                                    {"user_id": user2_id, "procent": procent2}
                                ]

                                success, message, imobil_id = coproprietate.creaza_imobil_cu_proprietari(
                                    supabase,
                                    nume_copro.strip(),
                                    adr_copro.strip() if adr_copro else None,
                                    proprietari_list
                                )

                                if success:
                                    st.success(f"✅ {message}")
                                    st.rerun()
                                else:
                                    st.error(f"❌ {message}")
                    else:
                        st.warning("Nu există alți utilizatori activi în sistem pentru a crea co-proprietate.")
                        submitted_copro = st.form_submit_button("💾 Creează Co-proprietate", use_container_width=True, disabled=True)

    # Listare imobile existente
    st.markdown("### 📋 Imobile Înregistrate")

    # Filtrare pentru admini
    if auth.is_admin():
        st.info("👑 **Mod Administrator:** Vezi toate imobilele sau filtrează după utilizator")
        try:
            users_result = supabase.table("users").select("id, nume, email").order("nume").execute()
            if users_result.data:
                filter_options = {"all": "🌐 Toate imobilele"}
                filter_options.update({u['id']: f"{u['nume']} ({u['email']})" for u in users_result.data})

                selected_user_filter = st.selectbox(
                    "Filtrează imobile:",
                    options=list(filter_options.keys()),
                    format_func=lambda x: filter_options[x]
                )
        except:
            selected_user_filter = st.session_state.user_id
    else:
        selected_user_filter = st.session_state.user_id

    try:
        # Query cu sau fără filtrare - folosește tabelul de co-proprietate
        if selected_user_filter == "all":
            # Admini: toate imobilele
            res = supabase.table("imobile").select("*").order("created_at", desc=True).execute()
            imobile_lista = res.data if res.data else []
        else:
            # User specific: doar imobilele la care are acces (inclusiv co-proprietăți)
            imobile_data = coproprietate.get_imobile_user(supabase, selected_user_filter, include_shared=True)
            # Extrage doar datele imobilului din structura de co-proprietate
            imobile_lista = [item.get('imobile', item) if 'imobile' in item else item for item in imobile_data]

        if not imobile_lista:
            st.info("📭 Niciun imobil înregistrat încă.")
        else:
            for imobil in imobile_lista:
                # Preia toți co-proprietarii
                coproprietari = coproprietate.get_coproprietari_imobil(supabase, imobil['id'])

                with st.container():
                    col1, col2, col3 = st.columns([3, 2, 1])

                    with col1:
                        st.markdown(f"**{imobil['nume']}**")
                        if imobil.get('adresa'):
                            st.caption(f"📍 {imobil['adresa']}")

                        # Afișează toți co-proprietarii
                        if coproprietari:
                            if len(coproprietari) == 1:
                                prop = coproprietari[0]
                                if prop.get('users'):
                                    st.caption(f"👤 Proprietar: {prop['users']['nume']} ({prop['procent_proprietate']}%)")
                            else:
                                st.caption("👥 Co-proprietari:")
                                for prop in coproprietari:
                                    if prop.get('users'):
                                        icon = "👑" if prop['user_id'] == st.session_state.user_id else "👤"
                                        st.caption(f"  {icon} {prop['users']['nume']}: {prop['procent_proprietate']}%")

                    with col2:
                        # Afișare cotă totală
                        cota_totala = coproprietate.get_procent_total_imobil(supabase, imobil['id'])
                        color = "normal" if cota_totala == 100 else "off"
                        st.metric("Cotă totală", f"{cota_totala}%")

                        # Cotă utilizatorului curent
                        if not auth.is_admin() or selected_user_filter != "all":
                            cota_user = next((p['procent_proprietate'] for p in coproprietari
                                            if p['user_id'] == (selected_user_filter if selected_user_filter != "all" else st.session_state.user_id)), 0)
                            if cota_user > 0:
                                st.caption(f"Tu: {cota_user}%")

                    with col3:
                        # Verificare permisiune de editare/ștergere
                        can_edit = coproprietate.user_poate_edita_imobil(
                            supabase,
                            st.session_state.user_id,
                            imobil['id'],
                            auth.is_admin()
                        )

                        if can_edit:
                            # Buton editare imobil
                            if st.button("✏️", key=f"edit_{imobil['id']}", help="Editează imobil"):
                                st.session_state[f"editing_{imobil['id']}"] = True
                                st.rerun()

                            # Buton gestionare co-proprietari
                            if st.button("⚙️", key=f"manage_{imobil['id']}", help="Gestionează co-proprietari"):
                                st.session_state[f"managing_{imobil['id']}"] = True
                                st.rerun()

                            # Buton ștergere (doar dacă e ultimul proprietar sau admin)
                            if auth.is_admin() or len(coproprietari) == 1:
                                if st.button("🗑️", key=f"del_imobil_{imobil['id']}", help="Șterge imobil"):
                                    try:
                                        supabase.table("imobile").delete().eq("id", imobil['id']).execute()
                                        st.success("✅ Imobil șters!")
                                        st.rerun()
                                    except Exception as e:
                                        st.error(f"❌ Eroare: {str(e)}")

                    # Panel editare imobil
                    if st.session_state.get(f"editing_{imobil['id']}", False):
                        with st.expander("✏️ Editare Imobil", expanded=True):
                            st.markdown("#### Modifică Datele Imobilului")

                            with st.form(key=f"edit_form_{imobil['id']}"):
                                edit_nume = st.text_input(
                                    "Nume Imobil*",
                                    value=imobil['nume'],
                                    placeholder="ex: Apartament Centru",
                                    key=f"edit_nume_{imobil['id']}"
                                )

                                edit_adresa = st.text_input(
                                    "Adresă",
                                    value=imobil.get('adresa', ''),
                                    placeholder="ex: Str. Victoriei nr. 10, București",
                                    key=f"edit_adresa_{imobil['id']}"
                                )

                                # Procent proprietate - doar pentru proprietari singuri
                                if len(coproprietari) == 1:
                                    edit_procent = st.slider(
                                        "Procent proprietate (%)",
                                        0, 100,
                                        int(imobil.get('procent_proprietate', 100)),
                                        key=f"edit_procent_{imobil['id']}"
                                    )
                                else:
                                    st.info("💡 Pentru co-proprietăți, procentele se gestionează în tab-ul '⚙️ Gestionare Co-proprietari'")
                                    edit_procent = imobil.get('procent_proprietate', 100)

                                col_save, col_cancel = st.columns(2)

                                with col_save:
                                    submitted = st.form_submit_button("💾 Salvează", use_container_width=True, type="primary")

                                with col_cancel:
                                    cancel = st.form_submit_button("✖️ Anulează", use_container_width=True)

                                if cancel:
                                    del st.session_state[f"editing_{imobil['id']}"]
                                    st.rerun()

                                if submitted:
                                    if not edit_nume.strip():
                                        st.error("❌ Numele imobilului este obligatoriu!")
                                    elif len(edit_nume) > 100:
                                        st.error("❌ Numele este prea lung (max 100 caractere)")
                                    else:
                                        try:
                                            # Actualizează imobilul
                                            update_data = {
                                                "nume": edit_nume.strip(),
                                                "adresa": edit_adresa.strip() if edit_adresa else None,
                                                "procent_proprietate": edit_procent
                                            }

                                            supabase.table("imobile").update(update_data).eq("id", imobil['id']).execute()

                                            # Dacă e proprietar singular, actualizează și în tabelul de co-proprietari
                                            if len(coproprietari) == 1:
                                                supabase.table("imobile_proprietari").update({
                                                    "procent_proprietate": edit_procent
                                                }).eq("imobil_id", imobil['id']).eq("user_id", st.session_state.user_id).execute()

                                            st.success(f"✅ Imobilul '{edit_nume}' a fost actualizat!")
                                            del st.session_state[f"editing_{imobil['id']}"]
                                            st.rerun()
                                        except Exception as e:
                                            st.error(f"❌ Eroare la actualizare: {str(e)}")

                    # Panel gestionare co-proprietari (extensibil)
                    if st.session_state.get(f"managing_{imobil['id']}", False):
                        with st.expander("⚙️ Gestionare Co-proprietari", expanded=True):
                            tab_add, tab_edit, tab_remove = st.tabs(["➕ Adaugă", "✏️ Editează", "🗑️ Șterge"])

                            with tab_add:
                                st.markdown("#### Adaugă Co-proprietar Nou")

                                # Selectare utilizator
                                try:
                                    all_users = supabase.table("users").select("id, nume, email").eq("active", True).execute()
                                    # Exclude utilizatorii care sunt deja co-proprietari
                                    existing_ids = [p['user_id'] for p in coproprietari]
                                    available_users = [u for u in all_users.data if u['id'] not in existing_ids]

                                    if available_users:
                                        users_dict_add = {u['id']: f"{u['nume']} ({u['email']})" for u in available_users}

                                        new_coprop_id = st.selectbox(
                                            "Selectează utilizator:",
                                            options=list(users_dict_add.keys()),
                                            format_func=lambda x: users_dict_add[x],
                                            key=f"add_user_{imobil['id']}"
                                        )

                                        new_procent = st.slider(
                                            "Procent proprietate (%):",
                                            0, 100, 25,
                                            key=f"add_proc_{imobil['id']}"
                                        )

                                        cota_actuala = coproprietate.get_procent_total_imobil(supabase, imobil['id'])
                                        cota_noua = cota_actuala + new_procent

                                        if cota_noua > 100:
                                            st.warning(f"⚠️ Suma va fi {cota_noua}% (depășește 100%)")

                                        if st.button("➕ Adaugă Co-proprietar", key=f"btn_add_{imobil['id']}"):
                                            success, msg = coproprietate.adauga_coproprietar_imobil(
                                                supabase,
                                                imobil['id'],
                                                new_coprop_id,
                                                new_procent
                                            )

                                            if success:
                                                st.success(msg)
                                                del st.session_state[f"managing_{imobil['id']}"]
                                                st.rerun()
                                            else:
                                                st.error(msg)
                                    else:
                                        st.info("Nu există utilizatori disponibili pentru adăugare.")
                                except Exception as e:
                                    st.error(f"Eroare: {str(e)}")

                            with tab_edit:
                                st.markdown("#### Actualizează Procent Proprietate")

                                if coproprietari:
                                    coprop_to_edit = st.selectbox(
                                        "Selectează co-proprietar:",
                                        options=[p['user_id'] for p in coproprietari],
                                        format_func=lambda x: next((p['users']['nume'] for p in coproprietari if p['user_id'] == x), "Unknown"),
                                        key=f"edit_user_{imobil['id']}"
                                    )

                                    current_procent = next((p['procent_proprietate'] for p in coproprietari if p['user_id'] == coprop_to_edit), 0)

                                    new_procent_edit = st.slider(
                                        f"Procent nou (actual: {current_procent}%):",
                                        0, 100, int(current_procent),
                                        key=f"edit_proc_{imobil['id']}"
                                    )

                                    if st.button("💾 Salvează", key=f"btn_edit_{imobil['id']}"):
                                        success, msg = coproprietate.actualizeaza_procent_coproprietar(
                                            supabase,
                                            imobil['id'],
                                            coprop_to_edit,
                                            new_procent_edit
                                        )

                                        if success:
                                            st.success(msg)
                                            del st.session_state[f"managing_{imobil['id']}"]
                                            st.rerun()
                                        else:
                                            st.error(msg)

                            with tab_remove:
                                st.markdown("#### Șterge Co-proprietar")

                                if len(coproprietari) > 1:
                                    coprop_to_remove = st.selectbox(
                                        "Selectează co-proprietar de șters:",
                                        options=[p['user_id'] for p in coproprietari],
                                        format_func=lambda x: next((p['users']['nume'] for p in coproprietari if p['user_id'] == x), "Unknown"),
                                        key=f"remove_user_{imobil['id']}"
                                    )

                                    st.warning("⚠️ Ștergerea unui co-proprietar va șterge și accesul acestuia la toate contractele acestui imobil!")

                                    if st.button("🗑️ Șterge Co-proprietar", key=f"btn_remove_{imobil['id']}", type="primary"):
                                        success, msg = coproprietate.sterge_coproprietar_imobil(
                                            supabase,
                                            imobil['id'],
                                            coprop_to_remove
                                        )

                                        if success:
                                            st.success(msg)
                                            del st.session_state[f"managing_{imobil['id']}"]
                                            st.rerun()
                                        else:
                                            st.error(msg)
                                else:
                                    st.info("Nu poți șterge ultimul proprietar al imobilului.")

                            if st.button("✖️ Închide", key=f"close_{imobil['id']}"):
                                del st.session_state[f"managing_{imobil['id']}"]
                                st.rerun()

                    st.divider()
    except Exception as e:
        st.error(f"❌ Eroare la încărcare: {str(e)}")

# ==================== PAGINA 3: GESTIUNE CONTRACTE ====================
elif page == "📄 Gestiune Contracte":
    st.title("📄 Gestiune Contracte de Închiriere")

    # Verificare existență imobile (inclusiv co-proprietăți)
    try:
        imobile_data = coproprietate.get_imobile_user(supabase, st.session_state.user_id, include_shared=True)
        # Extrage datele imobilului din structura de co-proprietate
        imobile_lista = []
        for item in imobile_data:
            if 'imobile' in item and item['imobile']:
                imobile_lista.append(item['imobile'])
            elif 'id' in item:  # Fallback pentru imobile simple
                imobile_lista.append(item)

        if not imobile_lista:
            st.warning("⚠️ Trebuie să adaugi mai întâi un imobil în secțiunea **Gestiune Imobile**.")
        else:
            # Formular adăugare contract
            with st.expander("➕ Adaugă Contract Nou", expanded=True):
                with st.form("contract_form"):
                    # Selectare imobil
                    imobile_dict = {i['id']: i['nume'] for i in imobile_lista}
                    imobil_selectat = st.selectbox(
                        "Imobil*",
                        options=list(imobile_dict.keys()),
                        format_func=lambda x: imobile_dict[x]
                    )

                    col1, col2 = st.columns(2)
                    with col1:
                        nr_contract = st.text_input("Nr. Contract", placeholder="ex: C-2026-001")
                        locatar = st.text_input("Nume Locatar*", placeholder="ex: Popescu Ion")
                    with col2:
                        cnp_cui = st.text_input("CNP/CUI", placeholder="13 cifre pentru PF, 2-10 pentru PJ")
                        pdf_url = st.text_input("Link Contract PDF (opțional)", placeholder="https://...")

                    col3, col4 = st.columns(2)
                    with col3:
                        chirie = st.number_input("Chirie Lunară*", min_value=0.0, value=500.0, step=50.0)
                        moneda = st.selectbox("Monedă", ["RON", "EUR"])
                    with col4:
                        data_start = st.date_input("Data Început*", value=datetime.date.today())
                        data_end = st.date_input("Data Sfârșit", value=None, help="Lasă gol pentru contract pe durată nedeterminată")

                    submitted_contract = st.form_submit_button("💾 Salvează Contract", use_container_width=True)

                    if submitted_contract:
                        erori = []

                        if not locatar.strip():
                            erori.append("Numele locatarului este obligatoriu")
                        if chirie <= 0:
                            erori.append("Chiria trebuie să fie > 0")
                        if cnp_cui and not valideaza_cnp_cui(cnp_cui):
                            erori.append("CNP/CUI invalid (doar cifre, lungime 6-13)")
                        if data_end and data_end < data_start:
                            erori.append("Data sfârșit nu poate fi înainte de data început")

                        if erori:
                            for err in erori:
                                st.error(f"❌ {err}")
                        else:
                            try:
                                supabase.table("contracte").insert({
                                    "imobil_id": imobil_selectat,
                                    "nr_contract": nr_contract.strip() if nr_contract else None,
                                    "locatar": locatar.strip(),
                                    "cnp_cui": cnp_cui.strip() if cnp_cui else None,
                                    "chirie_lunara": chirie,
                                    "moneda": moneda,
                                    "data_inceput": data_start.isoformat(),
                                    "data_sfarsit": data_end.isoformat() if data_end else None,
                                    "pdf_url": pdf_url.strip() if pdf_url else None,
                                    "user_id": st.session_state.user_id
                                }).execute()
                                st.success(f"✅ Contract pentru '{locatar}' a fost salvat!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"❌ Eroare la salvare: {str(e)}")

            # Listare contracte existente
            st.markdown("### 📋 Contracte Active")

            # Filtrare pentru admini
            if auth.is_admin():
                st.info("👑 **Mod Administrator:** Vezi toate contractele sau filtrează după utilizator")
                try:
                    users_result_c = supabase.table("users").select("id, nume, email").order("nume").execute()
                    if users_result_c.data:
                        filter_options_c = {"all": "🌐 Toate contractele"}
                        filter_options_c.update({u['id']: f"{u['nume']} ({u['email']})" for u in users_result_c.data})

                        selected_user_filter_c = st.selectbox(
                            "Filtrează contracte:",
                            options=list(filter_options_c.keys()),
                            format_func=lambda x: filter_options_c[x]
                        )
                except:
                    selected_user_filter_c = st.session_state.user_id
            else:
                selected_user_filter_c = st.session_state.user_id

            try:
                # Query cu sau fără filtrare
                if selected_user_filter_c == "all":
                    res_contracte = supabase.table("contracte").select("*, imobile(nume), users(nume, email)").order("data_inceput", desc=True).execute()
                else:
                    res_contracte = supabase.table("contracte").select("*, imobile(nume), users(nume, email)").eq("user_id", selected_user_filter_c).order("data_inceput", desc=True).execute()

                if not res_contracte.data:
                    st.info("📭 Niciun contract înregistrat încă.")
                else:
                    for contract in res_contracte.data:
                        with st.container():
                            col1, col2, col3, col4 = st.columns([3, 2, 2, 1])

                            with col1:
                                st.markdown(f"**{contract['locatar']}**")
                                st.caption(f"🏠 {contract['imobile']['nume']}")
                                if contract.get('nr_contract'):
                                    st.caption(f"📋 {contract['nr_contract']}")
                                # Afișează proprietarul pentru admini
                                if auth.is_admin() and contract.get('users'):
                                    st.caption(f"👤 {contract['users']['nume']}")

                            with col2:
                                st.metric("Chirie", f"{contract['chirie_lunara']:,.0f} {contract['moneda']}")

                            with col3:
                                data_start = contract['data_inceput']
                                data_end = contract['data_sfarsit'] if contract.get('data_sfarsit') else "Nedeterminat"
                                st.text(f"📅 {data_start}")
                                st.text(f"→ {data_end}")

                            with col4:
                                if contract.get('pdf_url'):
                                    st.link_button("📄", contract['pdf_url'], help="Vezi contract")

                                # Adminii pot edita orice, userii doar ale lor
                                can_edit_c = auth.is_admin() or contract.get('user_id') == st.session_state.user_id
                                if can_edit_c:
                                    if st.button("✏️", key=f"edit_contract_{contract['id']}", help="Editează contract"):
                                        st.session_state[f"editing_contract_{contract['id']}"] = True
                                        st.rerun()

                                # Adminii pot șterge orice, userii doar ale lor
                                can_delete_c = auth.is_admin() or contract.get('user_id') == st.session_state.user_id
                                if can_delete_c:
                                    if st.button("🗑️", key=f"del_contract_{contract['id']}", help="Șterge contract"):
                                        try:
                                            supabase.table("contracte").delete().eq("id", contract['id']).execute()
                                            st.success("✅ Contract șters!")
                                            st.rerun()
                                        except Exception as e:
                                            st.error(f"❌ {str(e)}")

                            # Panel editare contract
                            if st.session_state.get(f"editing_contract_{contract['id']}", False):
                                with st.expander("✏️ Editare Contract", expanded=True):
                                    st.markdown("#### Modifică Datele Contractului")

                                    with st.form(key=f"edit_contract_form_{contract['id']}"):
                                        # Selectare imobil (doar imobilele utilizatorului)
                                        user_imobile_data = coproprietate.get_imobile_user(supabase, st.session_state.user_id, include_shared=True)
                                        user_imobile_lista = []
                                        for item in user_imobile_data:
                                            if 'imobile' in item and item['imobile']:
                                                user_imobile_lista.append(item['imobile'])
                                            elif 'id' in item:
                                                user_imobile_lista.append(item)

                                        if user_imobile_lista:
                                            imobile_dict_edit = {i['id']: i['nume'] for i in user_imobile_lista}
                                            current_imobil_idx = list(imobile_dict_edit.keys()).index(contract['imobil_id']) if contract['imobil_id'] in imobile_dict_edit else 0

                                            edit_imobil = st.selectbox(
                                                "Imobil*",
                                                options=list(imobile_dict_edit.keys()),
                                                index=current_imobil_idx,
                                                format_func=lambda x: imobile_dict_edit[x],
                                                key=f"edit_imobil_{contract['id']}"
                                            )

                                            col1_e, col2_e = st.columns(2)
                                            with col1_e:
                                                edit_nr_contract = st.text_input(
                                                    "Nr. Contract",
                                                    value=contract.get('nr_contract', ''),
                                                    placeholder="ex: C-2026-001",
                                                    key=f"edit_nr_{contract['id']}"
                                                )
                                                edit_locatar = st.text_input(
                                                    "Nume Locatar*",
                                                    value=contract['locatar'],
                                                    placeholder="ex: Popescu Ion",
                                                    key=f"edit_locatar_{contract['id']}"
                                                )
                                            with col2_e:
                                                edit_cnp_cui = st.text_input(
                                                    "CNP/CUI",
                                                    value=contract.get('cnp_cui', ''),
                                                    placeholder="13 cifre pentru PF, 2-10 pentru PJ",
                                                    key=f"edit_cnp_{contract['id']}"
                                                )
                                                edit_pdf_url = st.text_input(
                                                    "Link Contract PDF (opțional)",
                                                    value=contract.get('pdf_url', ''),
                                                    placeholder="https://...",
                                                    key=f"edit_pdf_{contract['id']}"
                                                )

                                            col3_e, col4_e = st.columns(2)
                                            with col3_e:
                                                edit_chirie = st.number_input(
                                                    "Chirie Lunară*",
                                                    min_value=0.0,
                                                    value=float(contract['chirie_lunara']),
                                                    step=50.0,
                                                    key=f"edit_chirie_{contract['id']}"
                                                )
                                                moneda_idx = 0 if contract['moneda'] == 'RON' else 1
                                                edit_moneda = st.selectbox(
                                                    "Monedă",
                                                    ["RON", "EUR"],
                                                    index=moneda_idx,
                                                    key=f"edit_moneda_{contract['id']}"
                                                )
                                            with col4_e:
                                                edit_data_start = st.date_input(
                                                    "Data Început*",
                                                    value=datetime.datetime.strptime(contract['data_inceput'], '%Y-%m-%d').date(),
                                                    key=f"edit_start_{contract['id']}"
                                                )
                                                current_data_end = datetime.datetime.strptime(contract['data_sfarsit'], '%Y-%m-%d').date() if contract.get('data_sfarsit') else None
                                                edit_data_end = st.date_input(
                                                    "Data Sfârșit",
                                                    value=current_data_end,
                                                    help="Lasă gol pentru contract pe durată nedeterminată",
                                                    key=f"edit_end_{contract['id']}"
                                                )

                                            col_save_c, col_cancel_c = st.columns(2)

                                            with col_save_c:
                                                submitted_edit = st.form_submit_button("💾 Salvează", use_container_width=True, type="primary")

                                            with col_cancel_c:
                                                cancel_edit = st.form_submit_button("✖️ Anulează", use_container_width=True)

                                            if cancel_edit:
                                                del st.session_state[f"editing_contract_{contract['id']}"]
                                                st.rerun()

                                            if submitted_edit:
                                                erori_edit = []

                                                if not edit_locatar.strip():
                                                    erori_edit.append("Numele locatarului este obligatoriu")
                                                if edit_chirie <= 0:
                                                    erori_edit.append("Chiria trebuie să fie > 0")
                                                if edit_cnp_cui and not valideaza_cnp_cui(edit_cnp_cui):
                                                    erori_edit.append("CNP/CUI invalid (doar cifre, lungime 6-13)")
                                                if edit_data_end and edit_data_end < edit_data_start:
                                                    erori_edit.append("Data sfârșit nu poate fi înainte de data început")

                                                if erori_edit:
                                                    for err in erori_edit:
                                                        st.error(f"❌ {err}")
                                                else:
                                                    try:
                                                        update_contract_data = {
                                                            "imobil_id": edit_imobil,
                                                            "nr_contract": edit_nr_contract.strip() if edit_nr_contract else None,
                                                            "locatar": edit_locatar.strip(),
                                                            "cnp_cui": edit_cnp_cui.strip() if edit_cnp_cui else None,
                                                            "chirie_lunara": edit_chirie,
                                                            "moneda": edit_moneda,
                                                            "data_inceput": edit_data_start.isoformat(),
                                                            "data_sfarsit": edit_data_end.isoformat() if edit_data_end else None,
                                                            "pdf_url": edit_pdf_url.strip() if edit_pdf_url else None
                                                        }

                                                        supabase.table("contracte").update(update_contract_data).eq("id", contract['id']).execute()

                                                        st.success(f"✅ Contractul pentru '{edit_locatar}' a fost actualizat!")
                                                        del st.session_state[f"editing_contract_{contract['id']}"]
                                                        st.rerun()
                                                    except Exception as e:
                                                        st.error(f"❌ Eroare la actualizare: {str(e)}")
                                        else:
                                            st.warning("⚠️ Nu ai imobile înregistrate pentru a edita acest contract.")
                                            if st.form_submit_button("✖️ Închide"):
                                                del st.session_state[f"editing_contract_{contract['id']}"]
                                                st.rerun()

                            st.divider()
            except Exception as e:
                st.error(f"❌ Eroare la încărcare: {str(e)}")

    except Exception as e:
        st.error(f"❌ Eroare la verificarea imobilelor: {str(e)}")

# Footer
st.sidebar.markdown("---")
st.sidebar.caption("🏢 Proprieto ANAF 2026 v1.0")
st.sidebar.caption(f"💾 Conectat la DB: {'✅' if DB_CONNECTED else '❌'}")
