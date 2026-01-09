# 🏠 Proprieto ANAF-Ready 2026 v2.0

**Aplicație multi-user de gestiune imobiliară și calculare automată a taxelor conform legislației fiscale românești 2026**

[![Security: Authentication](https://img.shields.io/badge/Security-Authenticated-green)]()
[![Multi-User](https://img.shields.io/badge/Multi--User-Enabled-blue)]()
[![Admin Panel](https://img.shields.io/badge/Admin-Panel-orange)]()
[![Co-Ownership](https://img.shields.io/badge/Co--Ownership-Supported-purple)]()

---

## 🎉 Noutăți v2.0

### ✨ Funcționalități Noi
- **🔐 Autentificare Securizată**: Login cu email/parolă, hash-uri PBKDF2, rate limiting
- **👥 Co-Proprietate**: Mai mulți utilizatori pot deține același imobil cu procente diferite
- **⚙️ Panou Administrare**: Gestionare utilizatori, statistici, backup complet
- **🔒 Izolare Date**: Fiecare utilizator vede doar proprietățile și contractele sale
- **📊 Raportare Avansată**: Adminii pot vedea date consolidate pentru toți utilizatorii

### 🔄 Upgrade de la v1.0?
Consultă [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md) pentru instrucțiuni complete.

---

## 📋 Ce Face Aplicația?

Proprieto este o platformă web securizată care automatizează:
- 🔐 **Autentificare & Management utilizatori** (admin panel complet)
- 🏠 **Gestiunea portofoliului imobiliar** (multiple proprietăți, co-proprietate)
- 📄 **Evidența contractelor de închiriere** (RON/EUR, perioade multiple)
- 💰 **Calculul automat al taxelor ANAF**: Impozit (10%) + CASS (praguri 0/1/2/3)
- 📊 **Export rapoarte** pentru declarația D212 (Excel + PDF cu instrucțiuni)
- 👥 **Multi-user support** (fiecare utilizator vede doar propriile date)
- 🤝 **Co-proprietate** (gestionare proprietăți comune cu mai mulți proprietari)

---

## ⚡ Instalare Rapidă (6 pași)

### 1. Pregătire Bază de Date (Supabase)

Creează un cont gratuit pe [supabase.com](https://supabase.com) și creează un proiect nou.

**SQL Script pentru Setup Complet:**

1. Mergi la **Supabase Dashboard** → **SQL Editor** → **New Query**
2. Copiază întreg conținutul din fișierul `setup.sql` (din acest repository)
3. Click pe **Run**
4. Așteaptă mesajul "Success"

**Ce Creează `setup.sql`:**
- ✅ Tabel `users` (autentificare și management utilizatori)
- ✅ Tabel `imobile` (proprietăți cu user_id)
- ✅ Tabel `contracte` (contracte de închiriere)
- ✅ Tabel `imobile_proprietari` (co-proprietate)
- ✅ Tabel `contracte_proprietari` (acces partajat la contracte)
- ✅ Indexuri pentru performanță
- ✅ Cont admin default: `admin@proprieto.ro` / `admin123`
- ✅ Date demo pentru testare

**⚠️ IMPORTANT:** După primul login, schimbă parola adminului din secțiunea "👤 Cont"!

**📖 Ghiduri detaliate:**
- `AUTH_SETUP.md` - Configurare autentificare
- `MIGRATION_GUIDE.md` - Upgrade de la v1.0 la v2.0

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

### Pas 0: Autentificare
**Prima dată:**
- Email: `admin@proprieto.ro`
- Parolă: `admin123`
- ⚠️ **Schimbă imediat parola** din "👤 Cont" → "Schimbă Parola"

**Creează conturi pentru alți utilizatori:**
- Mergi la "⚙️ Administrare" → "Adaugă Utilizator"
- Introdu email, nume, parolă inițială
- Comunică credențialele securizat

### Pas 1: Adaugă Imobilele
**Navigare:** `🏠 Gestiune Imobile`

**Proprietate Simplă:**
- Introdu denumire (ex: "Apartament Centru")
- Adresă (opțional)
- **Procent proprietate** (dacă deții doar o cotă parte, ex: 50%)

**Co-Proprietate (Nou în v2.0!):**
- Tab "👥 Co-proprietate"
- Adaugă imobilul și selectează co-proprietarii
- Setează procentele pentru fiecare (suma = 100%)
- Ambii proprietari vor avea acces la imobil și contractele sale

**Gestionare Co-Proprietari:**
- Click pe ⚙️ lângă imobil
- Adaugă/Editează/Șterge co-proprietari
- Actualizează procente

### Pas 2: Adaugă Contractele
**Navigare:** `📄 Gestiune Contracte`

- Selectează imobilul (vezi toate imobilele tale + co-proprietățile)
- Introdu datele locatarului (nume, CNP/CUI)
- **Chirie lunară** și monedă (RON/EUR)
- **Perioada contractului** (data început + data sfârșit sau nedeterminat)

**Notă:** Contractele pentru imobile în co-proprietate sunt vizibile pentru toți co-proprietarii.

### Pas 3: Monitorizare și Export
**Navigare:** `📊 Dashboard Fiscal`

**Pentru Utilizatori:**
- **Vizualizare:** Venit brut, impozit, CASS, total taxe (doar datele tale)
- **Instrucțiuni D212:** Indicație automată pentru pragul CASS de bifat
- **Export Excel:** Raport complet cu toate veniturile
- **Export PDF:** Ghid pas-cu-pas pentru completarea formularului D212

**Pentru Admini (Nou în v2.0!):**
- **Filtrare:** Vezi date pentru toți utilizatorii sau selectează un utilizator specific
- **Raportare consolidată:** Agregare date pentru întreaga organizație
- **Management:** Creează/Șterge utilizatori, activează/dezactivează conturi

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

### Funcționalități de Securitate v2.0

- **✅ Autentificare Robustă:** Login cu email/parolă obligatoriu
- **✅ Hash-uri Parolă:** PBKDF2-HMAC-SHA256 cu salt unic per user
- **✅ Rate Limiting:** Max 5 încercări de login în 15 minute
- **✅ Izolare Date:** Utilizatorii văd doar datele proprii
- **✅ Permisiuni pe Rol:** Admini au acces complet, userii au acces limitat
- **✅ Audit Trail:** Timestamp last_login pentru fiecare utilizator
- **✅ Credențiale Securizate:** Toate secretele în Supabase Secrets (nu în cod)
- **✅ HTTPS:** Toate conexiunile către Supabase sunt criptate

### Practici Recomandate

1. **Schimbă parola adminului** imediat după primul login
2. **Folosește parole puternice** (min 8 caractere, combinație litere/cifre/simboluri)
3. **Nu partaja parole** prin email - folosește manageri de parole
4. **Revizuiește utilizatori** periodic în panoul de administrare
5. **Dezactivează conturi** nefolosite în loc să le ștergi
6. **Backup regulat** - exportă datele lunar din panoul admin

---

## 🚀 Funcționalități Avansate

### 👥 Co-Proprietate (NOU în v2.0)

**Scenarii de Utilizare:**
- **Familie:** Soț și soție dețin împreună un apartament (50%-50%)
- **Moștenire:** Frați moștenesc o casă (33%-33%-34%)
- **Investiție:** Parteneri de afaceri dețin un imobil comercial (60%-40%)

**Cum Funcționează:**
1. Un proprietar creează imobilul în sistem
2. Adaugă co-proprietari din lista utilizatorilor
3. Setează procentele pentru fiecare (suma = 100%)
4. Toți co-proprietarii văd imobilul și contractele sale
5. Calculul taxelor se face automat pe cota fiecăruia

**Exemplu Practic:**
- Imobil: Casa Ploiești
- Co-proprietari: Alexandru (60%) și Maria (40%)
- Contract: 3000 RON/lună
- Alexandru vede în Dashboard: 1800 RON/lună (60% din 3000)
- Maria vede în Dashboard: 1200 RON/lună (40% din 3000)

### 📊 Calcul Proporțional Perioade
Aplicația calculează automat numărul de luni active pentru contracte care:
- Încep în cursul anului fiscal
- Se încheie înainte de 31 decembrie
- Sunt active doar parțial

**Exemplu:** Contract activ între 15 Mar 2026 - 20 Nov 2026 → 9 luni (nu 12)

### 💱 Conversie Valutară Automată
Pentru contracte în EUR, aplicația convertește la RON folosind cursul mediu BNR introdus manual (sau default 5.02).

### ⚙️ Panou Administrare (NOU în v2.0)

**Management Utilizatori:**
- Creează conturi noi cu role (user/admin)
- Activează/Dezactivează conturi
- Vizualizează statistici login
- Șterge utilizatori (cu ștergere cascadă a datelor)

**Raportare Globală:**
- Vezi toate imobilele din sistem
- Vezi toate contractele din sistem
- Export complet al bazei de date
- Statistici agregate pe organizație

**Setări Sistem:**
- Configurare salariu minim (pentru CASS)
- Configurare curs BNR default
- Backup automat în Excel

---

## 📦 Structura Fișierelor

```
proprieto-app/
├── app.py                    # Aplicația principală (950 linii)
├── auth.py                   # Modul autentificare (213 linii)
├── coproprietate.py          # Modul co-proprietate (286 linii)
├── admin_panel.py            # Panou administrare (294 linii)
├── requirements.txt          # Dependențe Python
├── setup.sql                 # Script SQL complet (5 tabele + demo data)
├── README.md                 # Documentație principală
├── AUTH_SETUP.md             # Ghid configurare autentificare
├── MIGRATION_GUIDE.md        # Ghid upgrade v1.0 → v2.0
├── QUICKSTART.md             # Ghid rapid pornire
├── CHECKLIST.md              # Checklist deployment
├── DELIVERY_SUMMARY.md       # Rezumat livrare
├── DEPLOYMENT_FIX.md         # Troubleshooting deployment
└── .streamlit/
    └── secrets.toml          # Credențiale (doar local, NU urca pe GitHub!)
```

**Linii de Cod:**
- **Python:** ~1,750 linii
- **SQL:** ~350 linii
- **Documentație:** ~2,500 linii

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
