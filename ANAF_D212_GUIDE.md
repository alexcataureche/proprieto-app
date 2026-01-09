# 📋 Ghid Complet - Conformitate ANAF D212

Acest ghid te va ajuta să folosești noile funcționalități pentru declarația ANAF D212.

---

## 🚀 Pasul 1: Migrarea Bazei de Date

**IMPORTANT:** Înainte de a putea folosi noile funcționalități, trebuie să rulezi scriptul de migrare în baza ta de date Supabase.

### Cum rulezi migrarea:

1. **Accesează Supabase Dashboard**
   - Intră pe [https://supabase.com](https://supabase.com)
   - Selectează proiectul tău

2. **Deschide SQL Editor**
   - Din meniul lateral, click pe **SQL Editor**
   - Click pe **New Query**

3. **Copiază scriptul de migrare**
   - Deschide fișierul `migration_anaf_data.sql` din repository
   - Copiază **tot** conținutul fișierului

4. **Rulează scriptul**
   - Lipește conținutul în SQL Editor
   - Click pe **Run** (sau apasă `Ctrl + Enter`)
   - Așteaptă confirmarea: ar trebui să vezi mesaje de succes

5. **Verifică rezultatele**
   - La final, scriptul va afișa statistici despre tabelele modificate
   - Verifică că vezi mesajul: `✅ MIGRATION COMPLETĂ!`

---

## 👤 Pasul 2: Completează Datele Tale de Proprietar

Pentru ca declarația ANAF să fie completă, trebuie să îți completezi datele personale.

### Cum completezi profilul:

1. **Accesează aplicația** și autentifică-te

2. **Du-te la Setări**
   - Click pe **⚙️ Setări** din meniul lateral

3. **Selectează tab-ul "Editează Profil"**
   - Aici vei găsi formularul extins cu toate câmpurile necesare

4. **Completează toate câmpurile obligatorii (*)**:
   - **Nume Complet** - exact ca în CI/Pașaport
   - **CNP / NIF** - 13 cifre (va fi validat automat)
   - **Telefon** - format românesc (ex: 0722123456)
   - **Județ** - selectează din listă
   - **Localitate** - orașul/comuna ta
   - **Strada** - numele străzii (fără "Str.")
   - **Număr** - numărul străzii

5. **Completează câmpurile opționale** (recomandate):
   - Bloc, Scară, Etaj, Apartament
   - Cod Poștal (6 cifre)

6. **Verifică preview-ul adresei**
   - Sub formular vei vedea cum va arăta adresa ta completă

7. **Salvează**
   - Click pe **💾 Salvează Profil**
   - Vei primi confirmare de succes

---

## 🏠 Pasul 3: Adaugă/Actualizează Imobilele

Acum trebuie să completezi datele detaliate pentru fiecare imobil.

### Pentru imobile noi:

1. **Du-te la Gestiune Imobile**
   - Click pe **🏠 Gestiune Imobile** din meniu

2. **Click pe "➕ Adaugă Imobil Nou"**

3. **Selectează tipul de proprietate**:
   - **👤 Proprietate Singulară** - doar tu
   - **👥 Co-proprietate** - cu alți co-proprietari

4. **Completează datele imobilului**:
   - **Nume Identificare** - nume descriptiv (ex: "Apartament Centru")
   - **Adresa completă** - toate câmpurile (județ, localitate, stradă, număr, etc.)
   - **Număr Camere** - câte camere are imobilul (1-20)
   - **Procent Proprietate** - cât deții (%)

5. **Salvează imobilul**

### Pentru imobile existente:

1. **Găsește imobilul** în lista de imobile

2. **Click pe butonul ✏️ (Editează)**

3. **Completează câmpurile noi**:
   - Adresa detaliată (județ, localitate, stradă, etc.)
   - Număr de camere

4. **Salvează modificările**

---

## 📄 Pasul 4: Adaugă/Actualizează Contractele

Contractele necesită acum informații complete despre locatar (chiriaș).

### Pentru contracte noi:

1. **Du-te la Gestiune Contracte**
   - Click pe **📄 Contracte** din meniu

2. **Click pe "➕ Adaugă Contract Nou"**

3. **Completează cele 3 secțiuni**:

#### Secțiunea 1: Date Contract
   - **Nr. Contract*** - numărul contractului (ex: C-2026-001)
   - **Data Contract*** - data semnării
   - **Link Contract PDF** - opțional

#### Secțiunea 2: Date Locatar (Chiriaș)
   - **Tip Locatar*** - Persoană Fizică sau Persoană Juridică
   - **Nume Complet / Denumire*** - numele chiriașului sau firma
   - **CNP / CUI*** - CNP pentru PF (13 cifre), CUI pentru PJ (2-10 cifre)
   - **Telefon Locatar*** - număr de contact
   - **Email Locatar** - opțional
   - **Adresă Domiciliu Locatar*** - adresa completă

#### Secțiunea 3: Date Financiare și Perioada
   - **Chirie Lunară*** - suma în RON/EUR/USD
   - **Monedă*** - RON, EUR sau USD
   - **Frecvență Plată*** - lunar, trimestrial, semestrial sau anual
   - **Data Început*** - data de începere a închirierii
   - **Data Sfârșit** - opțional (lasă gol pentru nedeterminat)
   - **Nr. Camere Închiriate** - 0 = tot imobilul, altfel numărul de camere

4. **Salvează contractul**

### Pentru contracte existente:

1. **Găsește contractul** în lista de contracte

2. **Click pe butonul ✏️ (Editează)**

3. **Completează câmpurile noi** (aceleași ca mai sus)

4. **Salvează modificările**

---

## ✅ Validări Automate

Aplicația validează automat următoarele:

### CNP (Cod Numeric Personal) - 13 cifre:
- ✅ Lungime exactă (13 cifre)
- ✅ Prima cifră (sex) validă (1-9)
- ✅ Luna validă (01-12)
- ✅ Ziua validă (01-31)
- ✅ Cifra de control corectă

### CUI (Cod Unic de Înregistrare) - 2-10 cifre:
- ✅ Lungime validă (2-10 cifre)
- ✅ Acceptă prefix RO
- ✅ Doar cifre

### Telefon (format românesc):
- ✅ Acceptă format: 0722123456, +40722123456, 0040722123456
- ✅ 9 cifre după prefix
- ✅ Începe cu 7 (mobil) sau 2/3 (fix)

### Cod Poștal:
- ✅ Exact 6 cifre

### Email:
- ✅ Format valid (user@domain.com)

---

## 📊 Raportare ANAF

### View pentru raportare:

După migrare, vei avea disponibil un **view** special în Supabase pentru raportare:

**Nume view:** `view_contracte_anaf`

Acest view conține **toate** datele necesare pentru declarația D212:
- Date Proprietar (Locator): nume, CNP, email, telefon, adresă
- Date Locatar: nume, tip, CNP/CUI, email, telefon, adresă
- Date Imobil: nume, adresă completă, camere
- Date Financiare: chirie, monedă, frecvență, venit anual calculat automat
- Date Contract: număr, date, perioada

### Cum accesezi datele:

```sql
-- Toate contractele active
SELECT * FROM view_contracte_anaf
WHERE data_sfarsit IS NULL OR data_sfarsit >= CURRENT_DATE;

-- Contractele pentru un an specific
SELECT * FROM view_contracte_anaf
WHERE EXTRACT(YEAR FROM data_inceput) <= 2026
  AND (data_sfarsit IS NULL OR EXTRACT(YEAR FROM data_sfarsit) >= 2026);

-- Export pentru declarație ANAF
SELECT
    proprietar_nume,
    proprietar_cnp,
    proprietar_telefon,
    proprietar_adresa,
    imobil_adresa,
    locatar_nume,
    locatar_cnp_cui,
    venit_anual_brut
FROM view_contracte_anaf
WHERE EXTRACT(YEAR FROM data_inceput) <= 2026;
```

---

## 🔄 Frecvențe de Plată și Calcul Venit Anual

Aplicația calculează automat venitul anual în funcție de frecvența plății:

| Frecvență | Formula | Exemplu (1000 RON/lună) |
|-----------|---------|-------------------------|
| **Lunar** | chirie × 12 | 1000 × 12 = 12,000 RON |
| **Trimestrial** | chirie × 4 | 1000 × 4 = 4,000 RON |
| **Semestrial** | chirie × 2 | 1000 × 2 = 2,000 RON |
| **Anual** | chirie × 1 | 1000 × 1 = 1,000 RON |

---

## 💰 Monede Suportate

Aplicația suportă 3 monede:
- **RON** - Leu românesc
- **EUR** - Euro
- **USD** - Dolar american

**Notă:** Pentru declarația ANAF, sumele în valută străină se convertesc la cursul BNR din ziua anterioară depunerii sau a datei calculului.

---

## 🗺️ Județe Disponibile

Aplicația include toate cele **42 de județe** din România:

Alba, Arad, Argeș, Bacău, Bihor, Bistrița-Năsăud, Botoșani, Brașov, Brăila, București, Buzău, Caraș-Severin, Călărași, Cluj, Constanța, Covasna, Dâmbovița, Dolj, Galați, Giurgiu, Gorj, Harghita, Hunedoara, Ialomița, Iași, Ilfov, Maramureș, Mehedinți, Mureș, Neamț, Olt, Prahova, Satu Mare, Sălaj, Sibiu, Suceava, Teleorman, Timiș, Tulcea, Vaslui, Vâlcea, Vrancea

---

## ❓ Întrebări Frecvente (FAQ)

### 1. Trebuie să completez toate câmpurile?

**Câmpurile marcate cu \* sunt obligatorii.** Celelalte sunt opționale dar recomandate pentru o declarație completă.

### 2. Ce fac dacă am deja date în aplicație?

**Trebuie să editezi fiecare înregistrare** (profil, imobile, contracte) pentru a completa câmpurile noi. Datele vechi nu vor fi șterse.

### 3. CNP-ul meu nu este validat corect. Ce fac?

Verifică că:
- Are exact 13 cifre
- Este corect (verifică cartea de identitate)
- Nu conține spații sau alte caractere

### 4. Pot avea contracte cu locatari persoane juridice?

**Da!** Selectează "Persoană Juridică" și introdu CUI-ul firmei (2-10 cifre, poate avea prefix RO).

### 5. Ce înseamnă "Număr Camere Închiriate = 0"?

**0 înseamnă că închiriezi tot imobilul.** Dacă închiriezi doar o parte (ex: 2 camere dintr-un apartament cu 4 camere), introdu 2.

### 6. Pot avea contracte în EUR sau USD?

**Da!** Aplicația suportă RON, EUR și USD. Pentru declarația ANAF, va trebui să convertești la RON la cursul BNR.

### 7. Cum export datele pentru ANAF?

Folosește **view-ul `view_contracte_anaf`** din Supabase. Vezi secțiunea "Raportare ANAF" de mai sus pentru exemple de query-uri SQL.

---

## 🆘 Suport

Dacă întâmpini probleme:

1. **Verifică că ai rulat scriptul de migrare** (`migration_anaf_data.sql`)
2. **Verifică că toate câmpurile obligatorii sunt completate**
3. **Verifică consolă pentru erori** (F12 în browser)
4. **Contactează dezvoltatorul** pentru asistență

---

## 📚 Documente Importante

- **migration_anaf_data.sql** - Script de migrare bază de date
- **validari.py** - Modul de validări CNP/CUI/telefon
- **CODE_REVIEW_FIXES.md** - Documentație tehnică modificări

---

## ✨ Funcționalități Noi

✅ **Profil Proprietar Complet** - CNP, telefon, adresă detaliată
✅ **Adrese Detaliate Imobile** - județ, localitate, stradă, număr, bloc, scară, etaj, apartament
✅ **Număr Camere Imobile** - pentru raportare precisă
✅ **Date Complete Locatar** - tip (PF/PJ), CNP/CUI, contact, adresă
✅ **Metadata Contract** - data contract, frecvență plată, camere închiriate
✅ **Validări Automate** - CNP, CUI, telefon, email, cod poștal
✅ **Preview Adresă Live** - vezi cum va arăta adresa completă
✅ **3 Monede** - RON, EUR, USD
✅ **4 Frecvențe Plată** - lunar, trimestrial, semestrial, anual
✅ **View ANAF** - raportare simplă cu query SQL

---

**Ultima actualizare:** 2026-01-09
**Versiune:** 2.1.0 - ANAF D212 Compliance
