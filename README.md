# 🏠 Proprieto ANAF-Ready 2026 v2.0

**Aplicație multi-user de gestiune imobiliară și calculare automată a taxelor conform legislației fiscale românești 2026**

[![Security: Authentication](https://img.shields.io/badge/Security-Authenticated-green)]()
[![Multi-User](https://img.shields.io/badge/Multi--User-Enabled-blue)]()
[![Admin Panel](https://img.shields.io/badge/Admin-Panel-orange)]()

---

## 📋 Ce Face Aplicația?

Proprieto este o platformă web securizată care automatizează:
- 🔐 **Autentificare & Management utilizatori** (admin panel complet)
- 🏠 **Gestiunea portofoliului imobiliar** (multiple proprietăți, cote de proprietate)
- 📄 **Evidența contractelor de închiriere** (RON/EUR, perioade multiple)
- 💰 **Calculul automat al taxelor ANAF**: Impozit (10%) + CASS (praguri 0/1/2/3)
- 📊 **Export rapoarte** pentru declarația D212 (Excel + PDF cu instrucțiuni)
- 👥 **Multi-user support** (fiecare utilizator vede doar propriile date)

---

## ⚡ Instalare Rapidă (6 pași)

### 1. Pregătire Bază de Date (Supabase)

Creează un cont gratuit pe [supabase.com](https://supabase.com) și creează un proiect nou.

**SQL Script pentru Setup:**

**A. Rulează `setup.sql` (Database principal):**

```sql
-- Tabel Imobile
CREATE TABLE imobile (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nume TEXT NOT NULL,
    adresa TEXT,
    procent_proprietate NUMERIC(5,2) DEFAULT 100,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Tabel Contracte
CREATE TABLE contracte (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    imobil_id UUID REFERENCES imobile(id) ON DELETE CASCADE,
    nr_contract TEXT,
    locatar TEXT NOT NULL,
    cnp_cui TEXT,
    chirie_lunara NUMERIC(10,2) NOT NULL,
    moneda TEXT CHECK (moneda IN ('RON', 'EUR')) DEFAULT 'RON',
    data_inceput DATE NOT NULL,
    data_sfarsit DATE,
    pdf_url TEXT,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Index pentru performanță
CREATE INDEX idx_contracte_imobil ON contracte(imobil_id);
CREATE INDEX idx_contracte_perioada ON contracte(data_inceput, data_sfarsit);
```

Copiază scriptul în **Supabase Dashboard** → **SQL Editor** → **New Query** → **Run**.

**B. Rulează `setup_auth.sql` (Autentificare):**

Creează tabelul utilizatori și cont admin default:

```sql
-- Vezi fișierul setup_auth.sql pentru scriptul complet
-- Cont default: admin@proprieto.ro / admin123
-- ⚠️ SCHIMBĂ PAROLA după primul login!
```

**📖 Ghid detaliat:** Vezi `AUTH_SETUP.md` pentru instrucțiuni complete de configurare autentificare.

---

### 2. Configurare Credențiale

Din Supabase Dashboard → **Settings** → **API**, copiază:
- **URL** (ex: `https://xyz.supabase.co`)
- **anon public key** (cheia publică)

---

### 3. Instalare Locală (Testare)

```bash
# Clonează repository-ul
git clone https://github.com/USERNAME/proprieto-app.git
cd proprieto-app

# Instalare dependențe
pip install -r requirements.txt

# Configurare credențiale (creează fișier .streamlit/secrets.toml)
mkdir .streamlit
cat > .streamlit/secrets.toml << EOF
SUPABASE_URL = "https://xyz.supabase.co"
SUPABASE_KEY = "cheia-ta-aici"
EOF

# Rulare aplicație
streamlit run app.py
```

Aplicația va rula pe `http://localhost:8501`

---

### 4. Deployment Streamlit Cloud (Producție)

1. Creează repository GitHub cu fișierele:
   - `app.py`
   - `requirements.txt`
   - `README.md` (opțional)

2. Mergi pe [share.streamlit.io](https://share.streamlit.io)

3. **Connect Repository** → Alege repository-ul

4. **Advanced Settings** → **Secrets** → Adaugă:
   ```toml
   SUPABASE_URL = "https://xyz.supabase.co"
   SUPABASE_KEY = "cheia-ta-aici"
   ```

5. **Deploy!** → Link-ul aplicației va fi: `https://share.streamlit.io/username/proprieto-app`

---

## 🎯 Ghid de Utilizare

### Pas 1: Adaugă Imobilele
**Navigare:** `🏠 Gestiune Imobile`

- Introdu denumire (ex: "Apartament Centru")
- Adresă (opțional)
- **Procent proprietate** (dacă deții doar o cotă parte, ex: 50%)

### Pas 2: Adaugă Contractele
**Navigare:** `📄 Gestiune Contracte`

- Selectează imobilul
- Introdu datele locatarului (nume, CNP/CUI)
- **Chirie lunară** și monedă (RON/EUR)
- **Perioada contractului** (data început + data sfârșit sau nedeterminat)

### Pas 3: Monitorizare și Export
**Navigare:** `📊 Dashboard Fiscal`

- **Vizualizare:** Venit brut, impozit, CASS, total taxe
- **Instrucțiuni D212:** Indicație automată pentru pragul CASS de bifat
- **Export Excel:** Raport complet cu toate veniturile
- **Export PDF:** Ghid pas-cu-pas pentru completarea formularului D212

---

## 📊 Legislație Fiscală Implementată

### Impozit pe Venit (10%)
- **Bază de calcul:** Venit net (venit brut - 20% cheltuieli forfetare)
- **Cotă:** 10% din venitul net

### CASS (Contribuție Asigurări Sociale de Sănătate)
Calcul pe praguri conform Codului Fiscal:

| Prag | Venit Net Anual | CASS Datorat | Bază Calcul |
|------|-----------------|--------------|-------------|
| **0** | < 24.300 RON | 0 RON | - |
| **1** | ≥ 24.300 RON | 2.430 RON | 6 × salariu minim |
| **2** | ≥ 48.600 RON | 4.860 RON | 12 × salariu minim |
| **3** | ≥ 97.200 RON | 9.720 RON | 24 × salariu minim |

*Salariu minim brut 2026: 4.050 RON*

---

## 🔒 Securitate & Privacy

- **Date sensitive:** Toate datele sunt stocate în Supabase (securizat cu SSL)
- **Credențiale:** Niciodată în cod, doar în Secrets
- **Acces:** Pentru acces multi-user, adaugă autentificare în `app.py` (vezi secțiunea următoare)

### Adăugare Parolă Simplă (opțional)

Adaugă după linia 10 în `app.py`:

```python
# Autentificare simplă
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    pwd = st.text_input("Parolă Acces:", type="password")
    if st.button("Login"):
        if pwd == st.secrets.get("APP_PASSWORD", "parola123"):
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("Parolă incorectă!")
    st.stop()
```

Adaugă în Secrets: `APP_PASSWORD = "parola-ta-aici"`

---

## 🚀 Funcționalități Avansate

### Calcul Proporțional Perioade
Aplicația calculează automat numărul de luni active pentru contracte care:
- Încep în cursul anului fiscal
- Se încheie înainte de 31 decembrie
- Sunt active doar parțial

**Exemplu:** Contract activ între 15 Mar 2026 - 20 Nov 2026 → 9 luni (nu 12)

### Conversie Valutară Automată
Pentru contracte în EUR, aplicația convertește la RON folosind cursul mediu BNR introdus manual (sau default 5.02).

---

## 📦 Structura Fișierelor

```
proprieto-app/
├── app.py                 # Aplicația principală
├── requirements.txt       # Dependențe Python
├── README.md             # Documentație (acest fișier)
├── setup.sql             # Script SQL pentru Supabase
└── .streamlit/
    └── secrets.toml      # Credențiale (doar local, NU urca pe GitHub!)
```

---

## 🛠️ Suport Tehnic

### Probleme Frecvente

**❌ "Eroare conexiune Supabase"**
- Verifică că URL și KEY sunt corecte în Secrets
- Verifică că tabelele `imobile` și `contracte` există în DB

**❌ "ModuleNotFoundError"**
- Rulează: `pip install -r requirements.txt`

**❌ "No module named 'fpdf2'"**
- Verifică că în `requirements.txt` scrie `fpdf2==2.7.8` (nu `fpdf`)

---

## 📄 Licență

Acest proiect este open-source pentru uz personal. Pentru uz comercial, contactează autorul.

---

## 🎉 Contribuții

Pull requests sunt binevenite! Pentru schimbări majore, deschide mai întâi un issue.

---

**Dezvoltat cu 💙 pentru simplificarea fiscalității românești**

v1.0 - Ianuarie 2026
