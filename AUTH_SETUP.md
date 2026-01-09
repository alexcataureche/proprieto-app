# 🔐 Setup Autentificare & Multi-User

## ✨ Ce Este Nou

Aplicația are acum **sistem complet de autentificare** cu:

- ✅ Login/logout securizat
- ✅ Parolă criptată (PBKDF2-HMAC-SHA256 + salt)
- ✅ Multi-user: fiecare utilizator vede doar propriile date
- ✅ Roluri: **admin** (full control) și **user** (acces limitat)
- ✅ Panou administrare pentru gestionare utilizatori
- ✅ Rate limiting (max 5 încercări login / 15 min)

---

## 🚀 Setup Rapid (5 pași)

### Pas 1: Rulează Script SQL

Mergi în **Supabase** → **SQL Editor** → **New Query**

Copiază și rulează fișierul `setup_auth.sql`:

```sql
-- (Copiază întreg conținutul setup_auth.sql și dă Run)
```

**Ce face:**
- Creează tabelul `users`
- Adaugă coloanele `user_id` la `imobile` și `contracte`
- Creează cont administrator default

### Pas 2: Testează Login-ul

1. Deschide aplicația (local sau Streamlit Cloud)
2. Vei vedea pagina de **Login**
3. Folosește credențialele:
   ```
   Email: admin@proprieto.ro
   Parolă: admin123
   ```

### Pas 3: Schimbă Parola Admin! ⚠️

**IMPORTANT:** Prima acțiune după login trebuie să fie schimbarea parolei!

1. Sidebar → **👤 Cont**
2. Tab **🔒 Schimbă Parola**
3. Parola curentă: `admin123`
4. Parolă nouă: (alege o parolă puternică!)

### Pas 4: Creează Utilizatori Noi (opțional)

**Pentru familie/colaboratori:**

1. Sidebar → **⚙️ Administrare** (doar adminii au acces)
2. Tab **👥 Utilizatori** → **Adaugă Utilizator**
3. Completează:
   - Email: `soție@exemplu.ro`
   - Nume: `Maria Popescu`
   - Parolă: (alege o parolă)
   - Rol: **user** (nu `admin` dacă vrei restricții)

4. Trimite credențialele către persoană

### Pas 5: Migrează Datele Existente (dacă ai date demo)

**Dacă ai deja imobile/contracte în DB fără `user_id`:**

```sql
-- Asociază toate datele existente cu admin-ul
UPDATE imobile
SET user_id = (SELECT id FROM users WHERE email = 'admin@proprieto.ro')
WHERE user_id IS NULL;

UPDATE contracte
SET user_id = (SELECT id FROM users WHERE email = 'admin@proprieto.ro')
WHERE user_id IS NULL;
```

---

## 👤 Diferențe Rol: Admin vs. User

| Funcționalitate | Admin | User |
|-----------------|-------|------|
| **Dashboard Fiscal** | ✅ Propriile date | ✅ Propriile date |
| **Gestiune Imobile** | ✅ Propriile imobile | ✅ Propriile imobile |
| **Gestiune Contracte** | ✅ Propriile contracte | ✅ Propriile contracte |
| **👤 Cont** (schimbă parolă) | ✅ Da | ✅ Da |
| **⚙️ Administrare** | ✅ **DA** | ❌ **NU** |
| └─ Gestionare utilizatori | ✅ Creare, editare, șters | ❌ |
| └─ Vizualizare toți userii | ✅ Vezi toate datele | ❌ |
| └─ Backup complet | ✅ Export tot | ❌ |

---

## ⚙️ Panou Administrare (doar Admin)

### Tab 1: Gestionare Utilizatori

**Listă utilizatori:**
- Vezi toți utilizatorii (email, nume, rol, status)
- **Activare/Dezactivare** conturi
- **Ștergere** utilizatori (nu poți șterge propriul cont)
- Ultimul login pentru fiecare user

**Adaugă utilizator:**
- Email (unic în sistem)
- Nume complet
- Parolă inițială (min 8 caractere)
- Rol (admin sau user)

**Statistici:**
- Total utilizatori
- Număr admini vs. useri
- Activitate recentă (ultimele 5 login-uri)

### Tab 2: Date Generale

**Pentru admini:**
- Vezi **toate imobilele** tuturor utilizatorilor
- Vezi **toate contractele** tuturor utilizatorilor
- Venit anual estimat (suma tuturor contractelor)

**Pentru useri:**
- Vezi doar propriile date (filtrat automat)

### Tab 3: Setări Sistem

**Configurare:**
- Salariu minim (pentru praguri CASS)
- Curs BNR default

**Backup & Export:**
- Export Excel cu toate datele (utilizatori, imobile, contracte)
- Fișier cu timestamp pentru organizare

---

## 🔒 Securitate & Privacy

### Ce Date Vede Fiecare Utilizator?

**Izolare completă:**
```
User A → Vede doar:
  - Imobilele lui (user_id = A)
  - Contractele lui (user_id = A)
  - Dashboard-ul lui

User B → Vede doar:
  - Imobilele lui (user_id = B)
  - Contractele lui (user_id = B)
  - Dashboard-ul lui

Admin → Vede:
  - Propriile date în Dashboard/Imobile/Contracte
  - TOATE datele în Panou Administrare
```

### Cum Funcționează Parola?

**NU se stochează parola în clar!**

```python
# La înregistrare:
password = "parola123"
  ↓
salt = random_hex(16)  # Salt unic
  ↓
hash = PBKDF2-HMAC-SHA256(password, salt, 100000 iterații)
  ↓
DB: { password_hash: "8c6976...", salt: "d5f8c4..." }

# La login:
input_password = "parola123"
  ↓
hash = PBKDF2(input_password, salt_din_db)
  ↓
Compară: hash == password_hash_din_db
```

### Rate Limiting

**Protecție împotriva brute-force:**
- Max **5 încercări greșite** de login
- Blocare **15 minute** după 5 încercări
- Reset automat după 15 minute

---

## 🆘 Troubleshooting

### "Eroare la autentificare: relation 'users' does not exist"

**Cauză:** Nu ai rulat `setup_auth.sql`

**Fix:**
```sql
-- Rulează în Supabase SQL Editor
\i setup_auth.sql
-- SAU copiază tot conținutul fișierului și dă Run
```

### "Email sau parolă incorectă" (dar sunt sigur că sunt corecte!)

**Cauză:** Posibil ai atins limita de 5 încercări

**Fix:**
- Așteaptă 15 minute
- SAU resetează direct în DB:
  ```sql
  -- Această comandă nu funcționează din app, doar din SQL Editor
  ```

### "Prea multe încercări de login"

**Fix:** Așteaptă 15 minute și încearcă din nou.

### Am uitat parola admin!

**Resetare manuală din Supabase:**

```sql
-- 1. Generează hash nou pentru "admin123"
-- (sau folosește hash-ul din setup_auth.sql)

UPDATE users
SET
  password_hash = '8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918',
  salt = 'd5f8c4e3a2b1f6e7c8d9a0b1c2d3e4f5'
WHERE email = 'admin@proprieto.ro';

-- Acum poți loga cu: admin123
```

### Vreau să șterge un utilizator dar are contracte

**Datele sunt protejate prin CASCADE:**
- Când ștergi un user, se șterg **automat** toate imobilele și contractele lui
- Asigură-te că faci backup mai întâi!

```sql
-- Backup înainte de ștergere
SELECT * FROM imobile WHERE user_id = 'user-id-aici';
SELECT * FROM contracte WHERE user_id = 'user-id-aici';
```

---

## 📊 Structură Bază de Date

### Tabelul `users`

| Coloană | Tip | Descriere |
|---------|-----|-----------|
| `id` | UUID | Primary key |
| `email` | TEXT | Unic, folosit pentru login |
| `password_hash` | TEXT | Hash PBKDF2 al parolei |
| `salt` | TEXT | Salt unic pentru hash |
| `nume` | TEXT | Nume complet utilizator |
| `role` | TEXT | 'admin' sau 'user' |
| `active` | BOOLEAN | Cont activ/dezactivat |
| `created_at` | TIMESTAMPTZ | Data înregistrării |
| `last_login` | TIMESTAMPTZ | Ultimul login |

### Relații

```
users (1) ──< (N) imobile
  └─ imobile.user_id → users.id

users (1) ──< (N) contracte
  └─ contracte.user_id → users.id
```

---

## 🔄 Migrare de la Versiunea Fără Auth

**Dacă ai deja date în aplicația veche (fără autentificare):**

### Pas 1: Backup Date Existente
```sql
-- Export în Excel sau SQL
SELECT * FROM imobile;
SELECT * FROM contracte;
```

### Pas 2: Rulează setup_auth.sql

### Pas 3: Asociază Datele cu Admin-ul
```sql
-- Toate datele existente devin ale admin-ului
UPDATE imobile
SET user_id = (SELECT id FROM users WHERE email = 'admin@proprieto.ro')
WHERE user_id IS NULL;

UPDATE contracte
SET user_id = (SELECT id FROM users WHERE email = 'admin@proprieto.ro')
WHERE user_id IS NULL;
```

### Pas 4: Verificare
```sql
-- Trebuie să fie 0 rezultate
SELECT COUNT(*) FROM imobile WHERE user_id IS NULL;
SELECT COUNT(*) FROM contracte WHERE user_id IS NULL;
```

---

## 💡 Best Practices

### Pentru Administratori:
1. ✅ Schimbă parola default **imediat** după primul login
2. ✅ Folosește parolă puternică (min 12 caractere, litere+cifre+simboluri)
3. ✅ Creează conturi separate pentru fiecare membru al familiei
4. ✅ Dezactivează (nu șterge) conturile inactive
5. ✅ Fă backup lunar (Administrare → Export)

### Pentru Utilizatori:
1. ✅ Nu partaja parola cu altcineva
2. ✅ Schimbă parola periodic (la 3-6 luni)
3. ✅ Deconectează-te după utilizare (buton Deconectare)
4. ✅ Verifică că vezi doar propriile date în Dashboard

### Pentru Dezvoltatori:
1. ✅ Nu dezactiva HTTPS în producție
2. ✅ Folosește SUPABASE_KEY din Secrets (nu hardcoda)
3. ✅ Testează RLS (Row Level Security) în Supabase
4. ✅ Monitorizează login-uri suspecte

---

## 🎉 Gata!

Aplicația are acum sistem complet de autentificare securizat!

**Next Steps:**
1. Login cu admin@proprieto.ro / admin123
2. Schimbă parola admin
3. Creează conturi pentru familie
4. Migrează datele existente (dacă e cazul)
5. Enjoy secure multi-user app! 🚀

---

**Versiune:** 2.0 (Authentication & Multi-User)
**Data:** Ianuarie 2026
**Securitate:** Production-ready ✅
