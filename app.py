import streamlit as st
import pandas as pd
from supabase import create_client
from fpdf import FPDF
from io import BytesIO
import datetime
from dateutil.relativedelta import relativedelta

# --- CONFIGURARE ---
st.set_page_config(page_title="Proprieto 2026", layout="wide", page_icon="🏠")

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

        return pdf.output()
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
        return pdf.output()

# --- INTERFAȚĂ ---
st.sidebar.title("🏢 Proprieto ANAF 2026")
page = st.sidebar.radio("Navigare:", ["📊 Dashboard Fiscal", "🏠 Gestiune Imobile", "📄 Gestiune Contracte"])

if not DB_CONNECTED:
    st.warning("🔌 Aplicația rulează fără conexiune la baza de date. Configurează Supabase pentru funcționalitate completă.")
    st.stop()

# ==================== PAGINA 1: DASHBOARD FISCAL ====================
if page == "📊 Dashboard Fiscal":
    st.title("📊 Monitorizare Venituri și Calculatoare Fiscale")

    col_settings = st.columns([2, 1])
    with col_settings[0]:
        an_fiscal = st.selectbox("An Fiscal", [2025, 2026], index=1)
    with col_settings[1]:
        curs = st.number_input("Curs Mediu BNR (EUR→RON)", value=CURS_BNR_DEFAULT, min_value=1.0, max_value=10.0, step=0.01)

    try:
        # Preluare date
        res = supabase.table("contracte").select("*, imobile(procent_proprietate, nume)").execute()

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

                    venituri.append({
                        'Imobil': contract['imobile']['nume'],
                        'Locatar': contract['locatar'],
                        'Chirie/lună': f"{contract['chirie_lunara']:,.2f} {contract['moneda']}",
                        'Luni active': luni_active,
                        'Cotă proprietate': f"{contract['imobile']['procent_proprietate']}%",
                        'Venit RON': venit_ron
                    })
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
        with st.form("imobil_form"):
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
                        supabase.table("imobile").insert({
                            "nume": nume.strip(),
                            "adresa": adr.strip() if adr else None,
                            "procent_proprietate": proc
                        }).execute()
                        st.success(f"✅ Imobil '{nume}' a fost înregistrat!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Eroare la salvare: {str(e)}")

    # Listare imobile existente
    st.markdown("### 📋 Imobile Înregistrate")
    try:
        res = supabase.table("imobile").select("*").order("created_at", desc=True).execute()

        if not res.data:
            st.info("📭 Niciun imobil înregistrat încă.")
        else:
            for imobil in res.data:
                with st.container():
                    col1, col2, col3 = st.columns([3, 2, 1])
                    with col1:
                        st.markdown(f"**{imobil['nume']}**")
                        if imobil.get('adresa'):
                            st.caption(f"📍 {imobil['adresa']}")
                    with col2:
                        st.metric("Cotă proprietate", f"{imobil['procent_proprietate']}%")
                    with col3:
                        if st.button("🗑️", key=f"del_imobil_{imobil['id']}", help="Șterge imobil"):
                            try:
                                supabase.table("imobile").delete().eq("id", imobil['id']).execute()
                                st.success("✅ Imobil șters!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"❌ Eroare: {str(e)}")
                    st.divider()
    except Exception as e:
        st.error(f"❌ Eroare la încărcare: {str(e)}")

# ==================== PAGINA 3: GESTIUNE CONTRACTE ====================
elif page == "📄 Gestiune Contracte":
    st.title("📄 Gestiune Contracte de Închiriere")

    # Verificare existență imobile
    try:
        res_imobile = supabase.table("imobile").select("id, nume").execute()

        if not res_imobile.data:
            st.warning("⚠️ Trebuie să adaugi mai întâi un imobil în secțiunea **Gestiune Imobile**.")
        else:
            # Formular adăugare contract
            with st.expander("➕ Adaugă Contract Nou", expanded=True):
                with st.form("contract_form"):
                    # Selectare imobil
                    imobile_dict = {i['id']: i['nume'] for i in res_imobile.data}
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
                                    "pdf_url": pdf_url.strip() if pdf_url else None
                                }).execute()
                                st.success(f"✅ Contract pentru '{locatar}' a fost salvat!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"❌ Eroare la salvare: {str(e)}")

            # Listare contracte existente
            st.markdown("### 📋 Contracte Active")
            try:
                res_contracte = supabase.table("contracte").select("*, imobile(nume)").order("data_inceput", desc=True).execute()

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
                                if st.button("🗑️", key=f"del_contract_{contract['id']}", help="Șterge contract"):
                                    try:
                                        supabase.table("contracte").delete().eq("id", contract['id']).execute()
                                        st.success("✅ Contract șters!")
                                        st.rerun()
                                    except Exception as e:
                                        st.error(f"❌ {str(e)}")

                            st.divider()
            except Exception as e:
                st.error(f"❌ Eroare la încărcare: {str(e)}")

    except Exception as e:
        st.error(f"❌ Eroare la verificarea imobilelor: {str(e)}")

# Footer
st.sidebar.markdown("---")
st.sidebar.caption("🏢 Proprieto ANAF 2026 v1.0")
st.sidebar.caption(f"💾 Conectat la DB: {'✅' if DB_CONNECTED else '❌'}")
