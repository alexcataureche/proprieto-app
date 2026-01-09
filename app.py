import streamlit as st
import pandas as pd
from supabase import create_client
from fpdf import FPDF
from io import BytesIO

# --- CONFIGURARE ---
st.set_page_config(page_title="Proprieto 2026", layout="wide", page_icon="🏠")

# Conectare la Supabase (Datele se iau din Settings > Secrets in Streamlit Cloud)
try:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    supabase = create_client(url, key)
except:
    st.warning("⚠️ Te rugăm să configurezi SECRETS (URL și KEY) în dashboard-ul Streamlit.")

# --- LOGICĂ FISCALĂ ANAF 2026 ---
SALARIU_MINIM = 4050

def calculeaza_taxe(venit_brut_ron):
    venit_net = venit_brut_ron * 0.80  # Deducere forfetară 20%
    impozit = venit_net * 0.10
    
    # Praguri CASS conform legii
    p6, p12, p24 = 6*SALARIU_MINIM, 12*SALARIU_MINIM, 24*SALARIU_MINIM
    
    if venit_net >= p24: cass, prag = p24 * 0.1, 3
    elif venit_net >= p12: cass, prag = p12 * 0.1, 2
    elif venit_net >= p6: cass, prag = p6 * 0.1, 1
    else: cass, prag = 0, 0
    
    return {"net": venit_net, "impozit": impozit, "cass": cass, "prag": prag}

# --- INTERFAȚĂ ---
st.sidebar.title("🏢 Meniu Navigare")
page = st.sidebar.radio("Mergi la:", ["Dashboard Fiscal", "Gestiune Portofoliu"])

if page == "Dashboard Fiscal":
    st.title("📊 Monitorizare Venituri și Taxe")
    curs = st.number_input("Curs BNR (EUR/RON)", value=5.02)
    
    # Preluare date din Supabase
    res = supabase.table("contracte").select("*, imobile(procent_proprietate, nume)").execute()
    
    if res.data:
        df = pd.DataFrame(res.data)
        # Calcul venituri per contract ponderat cu cota de proprietate
        df['brut_ron'] = df.apply(lambda x: (x['chirie_lunara'] * 12 * (x['imobile']['procent_proprietate']/100)) * (curs if x['moneda']=='EUR' else 1), axis=1)
        
        total_brut = df['brut_ron'].sum()
        fisc = calculeaza_taxe(total_brut)
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Venit Brut Anual (RON)", f"{total_brut:,.2f}")
        c2.metric("Impozit de Plată", f"{fisc['impozit']:,.2f}")
        c3.metric("CASS (Sănătate)", f"{fisc['cass']:,.2f}")
        
        st.write(f"💡 **Indicație D212:** Pentru CASS trebuie bifat **Pragul {fisc['prag']}**.")
    else:
        st.info("Nu există contracte înregistrate.")

elif page == "Gestiune Portofoliu":
    st.header("🏠 Adăugare Imobil Nou")
    with st.form("imobil_form"):
        nume = st.text_input("Nume Identificare")
        adr = st.text_input("Adresa")
        proc = st.slider("Procent Proprietate", 0, 100, 50)
        if st.form_submit_button("Salvează Imobil"):
            supabase.table("imobile").insert({"nume": nume, "adresa": adr, "procent_proprietate": proc}).execute()
            st.success("Imobil înregistrat!")