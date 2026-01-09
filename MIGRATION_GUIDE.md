# 🔄 Ghid Migrare v1.0 → v2.0

**Proprieto ANAF 2026 - Migration Guide**

## 📋 Ce este Nou în v2.0?

### Funcționalități Noi
- ✅ **Autentificare multi-user** (login/logout cu email și parolă)
- ✅ **Co-proprietate** (mai mulți utilizatori pot deține același imobil)
- ✅ **Panou administrare** (management utilizatori și date)
- ✅ **Permisiuni pe utilizator** (fiecare user vede doar datele sale)
- ✅ **Securitate îmbunătățită** (hash-uri parolă, rate limiting)

### Ce se Schimbă?
- **Tabele noi:** `users`, `imobile_proprietari`, `contracte_proprietari`
- **Modificări structură:** Câmpul `user_id` devine obligatoriu în `imobile` și `contracte`
- **Autentificare:** Aplicația cere acum login înainte de acces

---

## ⚠️ IMPORTANT: Backup Înainte de Migrare

### Pas 1: Exportă Datele Existente

1. Mergi la **Supabase Dashboard** → **Table Editor**
2. Pentru fiecare tabel (`imobile`, `contracte`):
   - Click pe tabel
   - Click pe **"Export to CSV"**
   - Salvează fișierul

**SAU** folosește SQL:

```sql
-- Export imobile
COPY (SELECT * FROM imobile) TO STDOUT WITH CSV HEADER;

-- Export contracte
COPY (SELECT * FROM contracte) TO STDOUT WITH CSV HEADER;
```

### Pas 2: Salvează Backup-ul Complet

```sql
-- Backup complet înainte de migrare
CREATE TABLE imobile_backup AS SELECT * FROM imobile;
CREATE TABLE contracte_backup AS SELECT * FROM contracte;
```

---

## 🛠️ Opțiuni de Migrare

Alege una din cele două metode:

### **Metoda A: Migrare Automată** (recomandată, păstrează datele)
### **Metoda B: Start de la Zero** (șterge tot și reinstalează)

---

## 🟢 METODA A: Migrare Automată cu Păstrare Date

Această metodă adaugă tabelele noi și migrează datele existente.

### Pas 1: Rulează Script-ul de Migrare

Deschide **Supabase Dashboard** → **SQL Editor** → **New Query** și rulează:

```sql
-- ================================================================
-- MIGRATION SCRIPT v1.0 → v2.0
-- Proprieto ANAF 2026
-- ================================================================

BEGIN;

-- ----------------------------------------------------------------
-- PARTEA 1: CREEAZĂ TABELUL USERS
-- ----------------------------------------------------------------

CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    salt TEXT NOT NULL,
    nume TEXT NOT NULL,
    role TEXT CHECK (role IN ('user', 'admin')) DEFAULT 'user',
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT now(),
    last_login TIMESTAMPTZ,
    CONSTRAINT email_format CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$')
);

-- Creează index
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_active ON users(active);

-- ----------------------------------------------------------------
-- PARTEA 2: ADAUGĂ UTILIZATOR ADMIN DEFAULT
-- ----------------------------------------------------------------

INSERT INTO users (email, password_hash, salt, nume, role, active)
VALUES (
    'admin@proprieto.ro',
    '8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918',
    'defaultsalt123456',
    'Administrator',
    'admin',
    TRUE
)
ON CONFLICT (email) DO NOTHING;

-- ----------------------------------------------------------------
-- PARTEA 3: ADAUGĂ COLOANA user_id LA TABELE EXISTENTE
-- ----------------------------------------------------------------

-- Adaugă coloana user_id la imobile (dacă nu există deja)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name='imobile' AND column_name='user_id'
    ) THEN
        -- Obține ID-ul adminului
        DECLARE admin_id UUID;
        BEGIN
            SELECT id INTO admin_id FROM users WHERE email = 'admin@proprieto.ro';

            -- Adaugă coloana
            ALTER TABLE imobile ADD COLUMN user_id UUID;

            -- Setează toate imobilele existente să aparțină adminului
            UPDATE imobile SET user_id = admin_id WHERE user_id IS NULL;

            -- Fă coloana obligatorie
            ALTER TABLE imobile ALTER COLUMN user_id SET NOT NULL;

            -- Adaugă foreign key
            ALTER TABLE imobile ADD CONSTRAINT fk_imobile_user
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;

            -- Creează index
            CREATE INDEX idx_imobile_user ON imobile(user_id);
        END;
    END IF;
END $$;

-- Adaugă coloana user_id la contracte (dacă nu există deja)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name='contracte' AND column_name='user_id'
    ) THEN
        -- Obține ID-ul adminului
        DECLARE admin_id UUID;
        BEGIN
            SELECT id INTO admin_id FROM users WHERE email = 'admin@proprieto.ro';

            -- Adaugă coloana
            ALTER TABLE contracte ADD COLUMN user_id UUID;

            -- Setează toate contractele existente să aparțină adminului
            UPDATE contracte SET user_id = admin_id WHERE user_id IS NULL;

            -- Fă coloana obligatorie
            ALTER TABLE contracte ALTER COLUMN user_id SET NOT NULL;

            -- Adaugă foreign key
            ALTER TABLE contracte ADD CONSTRAINT fk_contracte_user
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;

            -- Creează index
            CREATE INDEX idx_contracte_user ON contracte(user_id);
        END;
    END IF;
END $$;

-- ----------------------------------------------------------------
-- PARTEA 4: CREEAZĂ TABELE CO-PROPRIETATE
-- ----------------------------------------------------------------

-- Tabel co-proprietari imobile
CREATE TABLE IF NOT EXISTS imobile_proprietari (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    imobil_id UUID NOT NULL REFERENCES imobile(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    procent_proprietate NUMERIC(5,2) NOT NULL CHECK (procent_proprietate > 0 AND procent_proprietate <= 100),
    created_at TIMESTAMPTZ DEFAULT now(),
    UNIQUE(imobil_id, user_id)
);

CREATE INDEX IF NOT EXISTS idx_imobile_prop_imobil ON imobile_proprietari(imobil_id);
CREATE INDEX IF NOT EXISTS idx_imobile_prop_user ON imobile_proprietari(user_id);

-- Tabel co-proprietari contracte
CREATE TABLE IF NOT EXISTS contracte_proprietari (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    contract_id UUID NOT NULL REFERENCES contracte(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ DEFAULT now(),
    UNIQUE(contract_id, user_id)
);

CREATE INDEX IF NOT EXISTS idx_contracte_prop_contract ON contracte_proprietari(contract_id);
CREATE INDEX IF NOT EXISTS idx_contracte_prop_user ON contracte_proprietari(user_id);

-- ----------------------------------------------------------------
-- PARTEA 5: MIGREAZĂ DATE EXISTENTE ÎN TABELE CO-PROPRIETATE
-- ----------------------------------------------------------------

-- Adaugă toate imobilele existente în tabelul de co-proprietari
INSERT INTO imobile_proprietari (imobil_id, user_id, procent_proprietate)
SELECT id, user_id, procent_proprietate
FROM imobile
WHERE NOT EXISTS (
    SELECT 1 FROM imobile_proprietari ip
    WHERE ip.imobil_id = imobile.id AND ip.user_id = imobile.user_id
);

-- Adaugă toate contractele existente în tabelul de co-proprietari
INSERT INTO contracte_proprietari (contract_id, user_id)
SELECT id, user_id
FROM contracte
WHERE NOT EXISTS (
    SELECT 1 FROM contracte_proprietari cp
    WHERE cp.contract_id = contracte.id AND cp.user_id = contracte.user_id
);

-- ----------------------------------------------------------------
-- PARTEA 6: TRIGGER PENTRU AUTO-UPDATE
-- ----------------------------------------------------------------

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Adaugă coloana updated_at dacă nu există
ALTER TABLE imobile ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ DEFAULT now();
ALTER TABLE contracte ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ DEFAULT now();

-- Creează triggere
DROP TRIGGER IF EXISTS update_imobile_updated_at ON imobile;
CREATE TRIGGER update_imobile_updated_at
    BEFORE UPDATE ON imobile
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_contracte_updated_at ON contracte;
CREATE TRIGGER update_contracte_updated_at
    BEFORE UPDATE ON contracte
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

COMMIT;

-- ----------------------------------------------------------------
-- VERIFICĂRI FINALE
-- ----------------------------------------------------------------

SELECT
    '✅ MIGRARE COMPLETĂ!' AS status,
    (SELECT COUNT(*) FROM users) AS total_users,
    (SELECT COUNT(*) FROM imobile) AS total_imobile,
    (SELECT COUNT(*) FROM contracte) AS total_contracte,
    (SELECT COUNT(*) FROM imobile_proprietari) AS total_imobile_proprietari,
    (SELECT COUNT(*) FROM contracte_proprietari) AS total_contracte_proprietari;
```

### Pas 2: Verifică Migrarea

```sql
-- Verifică că toate imobilele au user_id
SELECT COUNT(*) AS imobile_fara_user
FROM imobile
WHERE user_id IS NULL;
-- Ar trebui să fie 0

-- Verifică că toate contractele au user_id
SELECT COUNT(*) AS contracte_fara_user
FROM contracte
WHERE user_id IS NULL;
-- Ar trebui să fie 0

-- Verifică co-proprietarii
SELECT i.nume, u.nume AS proprietar, ip.procent_proprietate
FROM imobile i
JOIN imobile_proprietari ip ON i.id = ip.imobil_id
JOIN users u ON ip.user_id = u.id;
```

### Pas 3: Actualizează Aplicația

1. **Pull ultimele modificări** din repository:
   ```bash
   git pull origin main
   ```

2. **Actualizează dependențele** (dacă e necesar):
   ```bash
   pip install -r requirements.txt --upgrade
   ```

3. **Restart aplicația**:
   ```bash
   streamlit run app.py
   ```

### Pas 4: Login și Testare

- **Email:** admin@proprieto.ro
- **Parolă:** admin123
- ⚠️ **Schimbă parola imediat** din secțiunea "👤 Cont"!

---

## 🔴 METODA B: Start de la Zero

Dacă preferi să începi curat sau ai probleme cu migrarea:

### Pas 1: Backup Date (IMPORTANT!)

Salvează fișierele CSV cu datele tale (vezi secțiunea de Backup mai sus).

### Pas 2: Șterge Tot

```sql
DROP TABLE IF EXISTS contracte_proprietari CASCADE;
DROP TABLE IF EXISTS imobile_proprietari CASCADE;
DROP TABLE IF EXISTS contracte CASCADE;
DROP TABLE IF EXISTS imobile CASCADE;
DROP TABLE IF EXISTS users CASCADE;
```

### Pas 3: Rulează Setup Complet

Folosește fișierul `setup.sql` din repository:

```bash
# În Supabase SQL Editor
# Copiază întreg conținutul din setup.sql
# Apasă Run
```

### Pas 4: Re-Importă Datele (Opțional)

Dacă vrei să îți recuperezi datele vechi:

```sql
-- Obține ID-ul adminului
SELECT id FROM users WHERE email = 'admin@proprieto.ro';
-- Copiază acest UUID

-- Re-importă imobilele din backup
INSERT INTO imobile (nume, adresa, procent_proprietate, user_id)
SELECT nume, adresa, procent_proprietate, 'PASTE-UUID-AICI'::UUID
FROM imobile_backup;

-- Re-importă contractele din backup
INSERT INTO contracte (imobil_id, nr_contract, locatar, cnp_cui, chirie_lunara,
                       moneda, data_inceput, data_sfarsit, user_id)
SELECT imobil_id, nr_contract, locatar, cnp_cui, chirie_lunara,
       moneda, data_inceput, data_sfarsit, 'PASTE-UUID-AICI'::UUID
FROM contracte_backup;
```

---

## 🔒 Post-Migrare: Securitate

### Pas 1: Schimbă Parola Adminului

1. Login cu `admin@proprieto.ro` / `admin123`
2. Mergi la **"👤 Cont"** → **"Schimbă Parola"**
3. Setează o parolă puternică

### Pas 2: Creează Conturi pentru Alți Utilizatori

1. Mergi la **"⚙️ Administrare"** → **"Adaugă Utilizator"**
2. Creează conturi pentru fiecare membru al familiei/echipei
3. Comunică credențialele securizat (nu prin email!)

### Pas 3: Configurează Co-Proprietățile

Dacă ai imobile deținute în comun:

1. Mergi la **"🏠 Gestiune Imobile"**
2. Click pe **⚙️** lângă imobilul dorit
3. Tab **"👥 Co-proprietate"**
4. **Adaugă co-proprietar** și setează procentele

---

## ❓ Troubleshooting

### Eroare: "column user_id does not exist"

**Cauză:** Migrarea nu s-a aplicat corect.

**Soluție:**
```sql
-- Verifică dacă coloana există
SELECT column_name
FROM information_schema.columns
WHERE table_name = 'imobile' AND column_name = 'user_id';

-- Dacă nu există, rulează din nou PARTEA 3 din scriptul de migrare
```

### Eroare: "relation users does not exist"

**Cauză:** Tabelul users nu a fost creat.

**Soluție:** Rulează din nou PARTEA 1 din scriptul de migrare.

### Nu pot face login cu admin@proprieto.ro

**Cauză:** Utilizatorul nu există sau parola e incorectă.

**Soluție:**
```sql
-- Verifică dacă există
SELECT * FROM users WHERE email = 'admin@proprieto.ro';

-- Dacă nu există, creează-l din nou
INSERT INTO users (email, password_hash, salt, nume, role, active)
VALUES (
    'admin@proprieto.ro',
    '8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918',
    'defaultsalt123456',
    'Administrator',
    'admin',
    TRUE
);
```

### Datele mele au dispărut!

**Cauză:** Posibil ai rulat scriptul de setup care șterge datele.

**Soluție:** Restaurează din backup:
```sql
-- Restaurează imobilele
INSERT INTO imobile SELECT * FROM imobile_backup;

-- Restaurează contractele
INSERT INTO contracte SELECT * FROM contracte_backup;
```

---

## ✅ Checklist Post-Migrare

- [ ] ✅ Toate tabelele noi sunt create (`users`, `imobile_proprietari`, `contracte_proprietari`)
- [ ] ✅ Coloana `user_id` există în `imobile` și `contracte`
- [ ] ✅ Toate imobilele au `user_id` populat
- [ ] ✅ Toate contractele au `user_id` populat
- [ ] ✅ Pot face login cu `admin@proprieto.ro`
- [ ] ✅ Am schimbat parola adminului
- [ ] ✅ Văd toate datele mele în aplicație
- [ ] ✅ Export Excel/PDF funcționează
- [ ] ✅ Am creat conturi pentru ceilalți utilizatori (dacă e cazul)
- [ ] ✅ Am configurat co-proprietățile (dacă e cazul)
- [ ] ✅ Am șters tabelele de backup (`imobile_backup`, `contracte_backup`)

---

## 📞 Suport

Dacă întâmpini probleme:

1. **Verifică logs:** Supabase Dashboard → Logs
2. **Check GitHub Issues:** [Repository Issues]
3. **Review documentația:** `README.md`, `AUTH_SETUP.md`

---

**🎉 Felicitări! Ai migrat cu succes la Proprieto ANAF 2026 v2.0!**

*Versiune ghid: 1.0 - Ianuarie 2026*
