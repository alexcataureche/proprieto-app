{\rtf1\ansi\ansicpg1252\cocoartf2867
\cocoatextscaling0\cocoaplatform0{\fonttbl\f0\fswiss\fcharset0 Helvetica;}
{\colortbl;\red255\green255\blue255;}
{\*\expandedcolortbl;;}
\paperw11900\paperh16840\margl1440\margr1440\vieww37860\viewh21260\viewkind0
\pard\tx720\tx1440\tx2160\tx2880\tx3600\tx4320\tx5040\tx5760\tx6480\tx7200\tx7920\tx8640\pardirnatural\partightenfactor0

\f0\fs24 \cf0 import streamlit as st\
import pandas as pd\
from supabase import create_client\
from fpdf import FPDF\
from io import BytesIO\
\
# --- CONFIGURARE ---\
st.set_page_config(page_title="Proprieto 2026", layout="wide", page_icon="\uc0\u55356 \u57312 ")\
\
# Conectare la Supabase (Datele se iau din Settings > Secrets in Streamlit Cloud)\
try:\
    url = st.secrets["SUPABASE_URL"]\
    key = st.secrets["SUPABASE_KEY"]\
    supabase = create_client(url, key)\
except:\
    st.warning("\uc0\u9888 \u65039  Te rug\u259 m s\u259  configurezi SECRETS (URL \u537 i KEY) \'een dashboard-ul Streamlit.")\
\
# --- LOGIC\uc0\u258  FISCAL\u258  ANAF 2026 ---\
SALARIU_MINIM = 4050\
\
def calculeaza_taxe(venit_brut_ron):\
    venit_net = venit_brut_ron * 0.80  # Deducere forfetar\uc0\u259  20%\
    impozit = venit_net * 0.10\
    \
    # Praguri CASS conform legii\
    p6, p12, p24 = 6*SALARIU_MINIM, 12*SALARIU_MINIM, 24*SALARIU_MINIM\
    \
    if venit_net >= p24: cass, prag = p24 * 0.1, 3\
    elif venit_net >= p12: cass, prag = p12 * 0.1, 2\
    elif venit_net >= p6: cass, prag = p6 * 0.1, 1\
    else: cass, prag = 0, 0\
    \
    return \{"net": venit_net, "impozit": impozit, "cass": cass, "prag": prag\}\
\
# --- INTERFA\uc0\u538 \u258  ---\
st.sidebar.title("\uc0\u55356 \u57314  Meniu Navigare")\
page = st.sidebar.radio("Mergi la:", ["Dashboard Fiscal", "Gestiune Portofoliu"])\
\
if page == "Dashboard Fiscal":\
    st.title("\uc0\u55357 \u56522  Monitorizare Venituri \u537 i Taxe")\
    curs = st.number_input("Curs BNR (EUR/RON)", value=5.02)\
    \
    # Preluare date din Supabase\
    res = supabase.table("contracte").select("*, imobile(procent_proprietate, nume)").execute()\
    \
    if res.data:\
        df = pd.DataFrame(res.data)\
        # Calcul venituri per contract ponderat cu cota de proprietate\
        df['brut_ron'] = df.apply(lambda x: (x['chirie_lunara'] * 12 * (x['imobile']['procent_proprietate']/100)) * (curs if x['moneda']=='EUR' else 1), axis=1)\
        \
        total_brut = df['brut_ron'].sum()\
        fisc = calculeaza_taxe(total_brut)\
        \
        c1, c2, c3 = st.columns(3)\
        c1.metric("Venit Brut Anual (RON)", f"\{total_brut:,.2f\}")\
        c2.metric("Impozit de Plat\uc0\u259 ", f"\{fisc['impozit']:,.2f\}")\
        c3.metric("CASS (S\uc0\u259 n\u259 tate)", f"\{fisc['cass']:,.2f\}")\
        \
        st.write(f"\uc0\u55357 \u56481  **Indica\u539 ie D212:** Pentru CASS trebuie bifat **Pragul \{fisc['prag']\}**.")\
    else:\
        st.info("Nu exist\uc0\u259  contracte \'eenregistrate.")\
\
elif page == "Gestiune Portofoliu":\
    st.header("\uc0\u55356 \u57312  Ad\u259 ugare Imobil Nou")\
    with st.form("imobil_form"):\
        nume = st.text_input("Nume Identificare")\
        adr = st.text_input("Adresa")\
        proc = st.slider("Procent Proprietate", 0, 100, 50)\
        if st.form_submit_button("Salveaz\uc0\u259  Imobil"):\
            supabase.table("imobile").insert(\{"nume": nume, "adresa": adr, "procent_proprietate": proc\}).execute()\
            st.success("Imobil \'eenregistrat!")}