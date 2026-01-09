-- ================================================================
-- PROPRIETO ANAF 2026 v2.0 - Complete Database Setup
-- Multi-User with Authentication & Co-Ownership Support
-- ================================================================
--
-- INSTRUCȚIUNI:
-- 1. Mergi la Supabase Dashboard → SQL Editor
-- 2. Creează o "New Query"
-- 3. Copiază și rulează acest script complet
-- 4. Verifică că vezi "Success" pentru toate comenzile
--
-- ================================================================

-- ================================================================
-- PARTE 1: ȘTERGERE TABELE EXISTENTE (dacă există)
-- ================================================================
-- ATENȚIE: Această secțiune șterge toate datele existente!
-- Comentează-o dacă vrei să păstrezi datele existente.

DROP TABLE IF EXISTS contracte_proprietari CASCADE;
DROP TABLE IF EXISTS imobile_proprietari CASCADE;
DROP TABLE IF EXISTS contracte CASCADE;
DROP TABLE IF EXISTS imobile CASCADE;
DROP TABLE IF EXISTS users CASCADE;

-- ================================================================
-- PARTE 2: TABELE PRINCIPALE
-- ================================================================

-- Tabel Utilizatori (cu autentificare)
CREATE TABLE users (
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

-- Tabel Imobile
CREATE TABLE imobile (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nume TEXT NOT NULL,
    adresa TEXT,
    procent_proprietate NUMERIC(5,2) DEFAULT 100 CHECK (procent_proprietate > 0 AND procent_proprietate <= 100),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- Tabel Contracte
CREATE TABLE contracte (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    imobil_id UUID NOT NULL REFERENCES imobile(id) ON DELETE CASCADE,
    nr_contract TEXT,
    locatar TEXT NOT NULL,
    cnp_cui TEXT,
    chirie_lunara NUMERIC(10,2) NOT NULL CHECK (chirie_lunara > 0),
    moneda TEXT CHECK (moneda IN ('RON', 'EUR')) DEFAULT 'RON',
    data_inceput DATE NOT NULL,
    data_sfarsit DATE,
    pdf_url TEXT,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now(),
    CONSTRAINT date_check CHECK (data_sfarsit IS NULL OR data_sfarsit >= data_inceput)
);

-- Tabel Co-Proprietari Imobile (Many-to-Many)
CREATE TABLE imobile_proprietari (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    imobil_id UUID NOT NULL REFERENCES imobile(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    procent_proprietate NUMERIC(5,2) NOT NULL CHECK (procent_proprietate > 0 AND procent_proprietate <= 100),
    created_at TIMESTAMPTZ DEFAULT now(),
    UNIQUE(imobil_id, user_id)
);

-- Tabel Co-Proprietari Contracte (Many-to-Many)
CREATE TABLE contracte_proprietari (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    contract_id UUID NOT NULL REFERENCES contracte(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ DEFAULT now(),
    UNIQUE(contract_id, user_id)
);

-- ================================================================
-- PARTE 3: INDEXURI PENTRU PERFORMANȚĂ
-- ================================================================

-- Indexuri pentru căutări rapide
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_active ON users(active);
CREATE INDEX idx_imobile_user ON imobile(user_id);
CREATE INDEX idx_contracte_imobil ON contracte(imobil_id);
CREATE INDEX idx_contracte_user ON contracte(user_id);
CREATE INDEX idx_contracte_perioada ON contracte(data_inceput, data_sfarsit);
CREATE INDEX idx_imobile_prop_imobil ON imobile_proprietari(imobil_id);
CREATE INDEX idx_imobile_prop_user ON imobile_proprietari(user_id);
CREATE INDEX idx_contracte_prop_contract ON contracte_proprietari(contract_id);
CREATE INDEX idx_contracte_prop_user ON contracte_proprietari(user_id);

-- ================================================================
-- PARTE 4: TRIGGERE PENTRU AUTO-UPDATE
-- ================================================================

-- Trigger pentru actualizare automată a updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_imobile_updated_at
    BEFORE UPDATE ON imobile
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_contracte_updated_at
    BEFORE UPDATE ON contracte
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ================================================================
-- PARTE 5: UTILIZATOR ADMIN DEFAULT
-- ================================================================
-- Crează contul de administrator implicit
-- Email: admin@proprieto.ro
-- Parolă: admin123
--
-- ⚠️ IMPORTANT: Schimbă această parolă imediat după primul login!

INSERT INTO users (email, password_hash, salt, nume, role, active)
VALUES (
    'admin@proprieto.ro',
    '8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918',
    'defaultsalt123456',
    'Administrator',
    'admin',
    TRUE
);

-- ================================================================
-- PARTE 6: DATE DEMO (OPȚIONAL)
-- ================================================================
-- Datele demo pentru testare rapidă
-- Poți șterge această secțiune sau lăsa pentru testare

-- Creează un utilizator demo
INSERT INTO users (email, password_hash, salt, nume, role, active)
VALUES (
    'user@proprieto.ro',
    '8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918',
    'defaultsalt123456',
    'Utilizator Demo',
    'user',
    TRUE
);

-- Obține ID-urile utilizatorilor (salvăm în variabile temporare)
DO $$
DECLARE
    admin_id UUID;
    user_id UUID;
    imobil1_id UUID;
    imobil2_id UUID;
BEGIN
    -- Găsește ID-urile utilizatorilor
    SELECT id INTO admin_id FROM users WHERE email = 'admin@proprieto.ro';
    SELECT id INTO user_id FROM users WHERE email = 'user@proprieto.ro';

    -- Imobil 1: Proprietate simplă (admin)
    INSERT INTO imobile (nume, adresa, procent_proprietate, user_id)
    VALUES ('Apartament Centru', 'Str. Victoriei nr. 10, București', 100, admin_id)
    RETURNING id INTO imobil1_id;

    -- Adaugă în tabelul de co-proprietari
    INSERT INTO imobile_proprietari (imobil_id, user_id, procent_proprietate)
    VALUES (imobil1_id, admin_id, 100);

    -- Imobil 2: Co-proprietate 50-50 (admin + user)
    INSERT INTO imobile (nume, adresa, procent_proprietate, user_id)
    VALUES ('Casa Ploiești', 'Str. Republicii nr. 25, Ploiești', 100, admin_id)
    RETURNING id INTO imobil2_id;

    -- Adaugă co-proprietarii
    INSERT INTO imobile_proprietari (imobil_id, user_id, procent_proprietate)
    VALUES
        (imobil2_id, admin_id, 50),
        (imobil2_id, user_id, 50);

    -- Contract pentru Imobil 1
    INSERT INTO contracte (imobil_id, nr_contract, locatar, cnp_cui, chirie_lunara, moneda,
                          data_inceput, data_sfarsit, user_id)
    VALUES (
        imobil1_id,
        'C-2026-001',
        'Popescu Ion',
        '1850203123456',
        2000,
        'RON',
        '2026-01-01',
        '2026-12-31',
        admin_id
    );

    -- Contract pentru Imobil 2 (co-proprietate)
    WITH new_contract AS (
        INSERT INTO contracte (imobil_id, nr_contract, locatar, cnp_cui, chirie_lunara, moneda,
                              data_inceput, data_sfarsit, user_id)
        VALUES (
            imobil2_id,
            'C-2026-002',
            'Ionescu Maria',
            '2900514234567',
            1500,
            'RON',
            '2026-01-01',
            NULL,  -- Contract pe durată nedeterminată
            admin_id
        )
        RETURNING id
    )
    -- Adaugă ambii co-proprietari la contract
    INSERT INTO contracte_proprietari (contract_id, user_id)
    SELECT id, admin_id FROM new_contract
    UNION ALL
    SELECT id, user_id FROM new_contract;

END $$;

-- ================================================================
-- PARTE 7: VERIFICĂRI FINALE
-- ================================================================

-- Afișează statistici pentru verificare
SELECT
    'SETUP COMPLET!' AS status,
    (SELECT COUNT(*) FROM users) AS total_users,
    (SELECT COUNT(*) FROM imobile) AS total_imobile,
    (SELECT COUNT(*) FROM contracte) AS total_contracte,
    (SELECT COUNT(*) FROM imobile_proprietari) AS total_coproprietari;

-- Verifică utilizatorii creați
SELECT
    '👤 UTILIZATORI CREAȚI:' AS info,
    email,
    nume,
    role,
    CASE WHEN active THEN '✅ Activ' ELSE '❌ Inactiv' END AS status
FROM users
ORDER BY role DESC, nume;

-- Verifică imobilele și co-proprietarii
SELECT
    '🏠 IMOBILE ȘI CO-PROPRIETARI:' AS info,
    i.nume AS imobil,
    u.nume AS proprietar,
    ip.procent_proprietate AS procent
FROM imobile i
JOIN imobile_proprietari ip ON i.id = ip.imobil_id
JOIN users u ON ip.user_id = u.id
ORDER BY i.nume, u.nume;

-- Verifică contractele
SELECT
    '📄 CONTRACTE:' AS info,
    c.nr_contract,
    c.locatar,
    i.nume AS imobil,
    c.chirie_lunara || ' ' || c.moneda AS chirie,
    c.data_inceput,
    COALESCE(c.data_sfarsit::TEXT, 'Nedeterminat') AS data_sfarsit
FROM contracte c
JOIN imobile i ON c.imobil_id = i.id
ORDER BY c.data_inceput DESC;

-- ================================================================
-- FINALIZARE
-- ================================================================

-- Mesaj de confirmare
SELECT
    '✅ DATABASE SETUP COMPLET!' AS status,
    'Acum poți conecta aplicația Streamlit cu aceste credențiale Supabase.' AS next_step,
    'Cont admin: admin@proprieto.ro / admin123' AS credentials,
    '⚠️ SCHIMBĂ PAROLA după primul login!' AS warning;
