# ✅ Checklist de Verificare - Proprieto ANAF 2026

## 🎯 Folosire

Bifează fiecare pas pe măsură ce îl completezi. La final, aplicația va fi LIVE.

---

## 📦 FAZA 1: Setup Inițial (5 minute)

### Supabase Database

- [ ] Creat cont pe [supabase.com](https://supabase.com)
- [ ] Creat proiect nou (așteaptă ~2 min)
- [ ] Mers la **SQL Editor** (sidebar stânga)
- [ ] Copiat întreg fișierul `setup.sql`
- [ ] **Run** → Vezi mesaj "Success"
- [ ] Verificat că queries de verificare arată 2 imobile + 2 contracte (date demo)

### Credențiale

- [ ] Supabase → **Settings** → **API**
- [ ] Copiat **Project URL** (ex: https://abc123.supabase.co)
- [ ] Copiat **anon public** key (cheie lungă)

**PAUZĂ:** Acum ai baza de date funcțională! ✅

---

## 💻 FAZA 2: Testare Locală (5 minute)

### Instalare

- [ ] Deschis Terminal/Command Prompt
- [ ] Navigat către folder: `cd proprieto-app`
- [ ] Instalat dependențe: `pip install -r requirements.txt`
- [ ] Creat folder secrets: `mkdir .streamlit`

### Configurare Secrets

- [ ] Creat fișier `.streamlit/secrets.toml` cu conținut:
  ```toml
  SUPABASE_URL = "paste-url-aici"
  SUPABASE_KEY = "paste-key-aici"
  ```
- [ ] Înlocuit `paste-url-aici` cu URL-ul tău real
- [ ] Înlocuit `paste-key-aici` cu KEY-ul tău real
- [ ] Salvat fișierul

### Rulare Aplicație

- [ ] Rulat: `streamlit run app.py`
- [ ] Browser s-a deschis automat pe `localhost:8501`
- [ ] Footer aplicației arată "Conectat la DB: ✅"

### Test Funcțional

- [ ] **Dashboard Fiscal** arată metrics (Venit Brut, Impozit, CASS)
- [ ] **Gestiune Imobile** listează 2 imobile demo
- [ ] **Gestiune Contracte** listează 2 contracte demo
- [ ] Descărcat Excel → fișierul se deschide cu date
- [ ] Descărcat PDF → documentul arată instrucțiuni D212

**PAUZĂ:** Aplicația funcționează local! 🎉

---

## 🧪 FAZA 3: Test Proprii Date (5 minute)

### Curățare Date Demo (opțional)

- [ ] **Gestiune Contracte** → Șters contractele demo (buton 🗑️)
- [ ] **Gestiune Imobile** → Șters imobilele demo (buton 🗑️)

SAU în Supabase SQL Editor:
```sql
DELETE FROM contracte;
DELETE FROM imobile;
```

### Adăugare Date Reale

- [ ] **Gestiune Imobile** → ➕ Adaugă Imobil Nou
  - Nume: `Apartamentul meu`
  - Adresă: (adresa ta)
  - Procent: `100` (sau cât deții)
  - **Salvează**

- [ ] Verificat că imobilul apare în listă

- [ ] **Gestiune Contracte** → ➕ Adaugă Contract Nou
  - Imobil: Selectat din dropdown
  - Locatar: (numele locatarului)
  - Chirie: (suma)
  - Monedă: RON sau EUR
  - Data început: (ex: 01-01-2026)
  - Data sfârșit: (lasă gol pentru nedeterminat)
  - **Salvează**

- [ ] Verificat că contractul apare în listă

### Verificare Calcul Fiscal

- [ ] **Dashboard Fiscal** → Vezi metrics actualizate
- [ ] Verificat manual calculul:
  - Venit brut = Chirie × Luni active × Cotă proprietate
  - Impozit = (Venit brut × 0.8) × 0.1
  - CASS = conform pragului indicat
- [ ] Export Excel conține datele tale reale
- [ ] Export PDF arată pragul CASS corect

**PAUZĂ:** Aplicația funcționează cu datele tale! 🚀

---

## ☁️ FAZA 4: Deployment Online (10 minute)

### Git & GitHub

- [ ] Deschis Terminal în folder `proprieto-app`
- [ ] Inițializat Git: `git init`
- [ ] Verificat că `.gitignore` există (protejează secrets)
- [ ] Adăugat fișiere: `git add .`
- [ ] Commit inițial: `git commit -m "Initial commit - Proprieto ANAF 2026"`

- [ ] Creat repository nou pe [github.com](https://github.com/new)
  - Nume: `proprieto-app`
  - Vizibilitate: **Private** (recomandat)
  - **NU** bifa "Add README" (deja există)

- [ ] Copiat comenzile de push afișate de GitHub:
  ```bash
  git remote add origin https://github.com/USERNAME/proprieto-app.git
  git branch -M main
  git push -u origin main
  ```

- [ ] Verificat că fișierele apar pe GitHub
- [ ] **IMPORTANT:** Verificat că `.streamlit/secrets.toml` NU apare (e protejat de .gitignore)

### Streamlit Cloud

- [ ] Mers pe [share.streamlit.io](https://share.streamlit.io)
- [ ] **Sign in with GitHub**
- [ ] **New app**
- [ ] Selectat repository `proprieto-app`
- [ ] Branch: `main`
- [ ] Main file path: `app.py`

- [ ] **Advanced settings** → **Secrets** → Lipit:
  ```toml
  SUPABASE_URL = "https://abc123.supabase.co"
  SUPABASE_KEY = "cheia-ta-aici"
  ```
  (Folosește aceleași valori ca în `.streamlit/secrets.toml` local)

- [ ] **Deploy!**
- [ ] Așteptat ~2 minute (progress bar)

### Verificare Deployment

- [ ] Aplicația s-a deschis la URL public (ex: `https://share.streamlit.io/username/proprieto-app`)
- [ ] Footer arată "Conectat la DB: ✅"
- [ ] Datele tale apar (imobile + contracte)
- [ ] Export-urile funcționează

**PAUZĂ:** Aplicația este LIVE pe internet! 🌍

---

## 🔐 FAZA 5: Securitate (opțional - 5 minute)

### Protecție cu Parolă

- [ ] Deschis `app.py` în editor
- [ ] Adăugat codul de protecție după linia 10 (vezi QUICKSTART.md)
- [ ] Adăugat în Secrets (local și Streamlit Cloud):
  ```toml
  APP_PASSWORD = "parolavostrasecreta"
  ```
- [ ] Salvat și push pe GitHub
- [ ] Streamlit Cloud va face auto-redeploy (~1 min)
- [ ] Verificat că aplicația cere parolă la deschidere

### Partajare Acces

- [ ] Trimis link către soție/colaboratori
- [ ] Trimis parola (separat, prin SMS/WhatsApp)
- [ ] Testat că ei pot accesa aplicația

---

## 📊 FAZA 6: Utilizare Curentă

### Workflow Lunar

- [ ] La început de lună: Verificat că toate contractele sunt active
- [ ] Adăugat contracte noi (dacă ai încheiat unele noi)
- [ ] Actualizat contracte expirate (buton 🗑️ pe cele vechi)

### Workflow Anual (Declarație D212)

- [ ] Ianuarie-Martie: Mers la **Dashboard Fiscal**
- [ ] Selectat anul anterior (ex: 2025) din dropdown
- [ ] Verificat curs BNR mediu anual (caută pe Google: "curs mediu BNR 2025")
- [ ] Descărcat **Excel** pentru evidența ta
- [ ] Descărcat **PDF** cu ghidul D212
- [ ] Completat formularul D212 pe [anaf.ro](https://www.anaf.ro) urmând instrucțiunile
- [ ] Plătit taxele (impozit + CASS) conform sumei calculate

---

## 🆘 TROUBLESHOOTING

### ❌ "Eroare conexiune Supabase"

- [ ] Verificat URL și KEY în Secrets
- [ ] Verificat că în Supabase proiectul este active (nu paused)
- [ ] Verificat că tabelele există: Supabase → Table Editor → vezi `imobile` și `contracte`

### ❌ "ModuleNotFoundError"

- [ ] Rulat: `pip install -r requirements.txt --upgrade`
- [ ] Verificat că Python version ≥ 3.8: `python --version`

### ❌ Aplicația nu afișează date

- [ ] Verificat că ai adăugat cel puțin 1 imobil ȘI 1 contract
- [ ] Verificat în Supabase → Table Editor că datele există efectiv în DB
- [ ] Forțat refresh în browser (Ctrl+F5 sau Cmd+R)

### ❌ Export PDF arată caractere ciudate

- [ ] Folosește Export Excel în schimb (funcționează perfect)
- [ ] Sau vezi fix-ul din QUICKSTART.md secțiunea Troubleshooting

---

## 🎉 FINAL CHECKLIST

- [ ] ✅ Aplicația rulează local
- [ ] ✅ Aplicația rulează online (Streamlit Cloud)
- [ ] ✅ Datele tale reale sunt în sistem
- [ ] ✅ Calculul fiscal este corect (verificat manual)
- [ ] ✅ Export-urile funcționează
- [ ] ✅ Link-ul este partajat cu cei care au nevoie
- [ ] ✅ Am salvat parola într-un loc sigur
- [ ] ✅ Am bookmarked link-ul aplicației

---

## 📅 Reminder-e Importante

### ANUAL (Ianuarie)
- [ ] Actualizare salariu minim în `app.py` linia 28
- [ ] Verificare modificări legislative CASS
- [ ] Completare D212 pentru anul anterior

### LA NEVOIE
- [ ] Backup date: Supabase → Table Editor → Export to CSV
- [ ] Update contracte expirate (șterge sau marchează)

---

## 🏆 FELICITĂRI!

Dacă toate checkbox-urile sunt bifate, ai:
- ✅ Aplicație web funcțională
- ✅ Bază de date cloud securizată
- ✅ Calcul fiscal automat
- ✅ Deployment profesional
- ✅ Zero costuri operaționale

**Next Step:** Folosește aplicația lunar pentru monitorizare și anual pentru declarația D212!

---

*Creat de Claude Code - Ianuarie 2026*
