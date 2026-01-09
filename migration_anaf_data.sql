-- ================================================================
-- PROPRIETO ANAF 2026 - Migration for ANAF D212 Compliance
-- Adds all required fields for Romanian tax declaration
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
-- PARTE 1: EXTINDERE TABEL USERS (Proprietar/Locator)
-- ================================================================

-- Adaugă date de identificare pentru Proprietar
ALTER TABLE users ADD COLUMN IF NOT EXISTS cnp TEXT;
ALTER TABLE users ADD COLUMN IF NOT EXISTS telefon TEXT;
ALTER TABLE users ADD COLUMN IF NOT EXISTS judet TEXT;
ALTER TABLE users ADD COLUMN IF NOT EXISTS localitate TEXT;
ALTER TABLE users ADD COLUMN IF NOT EXISTS strada TEXT;
ALTER TABLE users ADD COLUMN IF NOT EXISTS numar TEXT;
ALTER TABLE users ADD COLUMN IF NOT EXISTS bloc TEXT;
ALTER TABLE users ADD COLUMN IF NOT EXISTS scara TEXT;
ALTER TABLE users ADD COLUMN IF NOT EXISTS etaj TEXT;
ALTER TABLE users ADD COLUMN IF NOT EXISTS apartament TEXT;
ALTER TABLE users ADD COLUMN IF NOT EXISTS cod_postal TEXT;

-- Adaugă constrângeri pentru CNP (opțional - 13 cifre)
ALTER TABLE users ADD CONSTRAINT cnp_length CHECK (cnp IS NULL OR LENGTH(cnp) = 13);
ALTER TABLE users ADD CONSTRAINT cnp_numeric CHECK (cnp IS NULL OR cnp ~ '^[0-9]+$');

-- Index pentru căutări rapide după CNP
CREATE INDEX IF NOT EXISTS idx_users_cnp ON users(cnp);

-- ================================================================
-- PARTE 2: EXTINDERE TABEL IMOBILE
-- ================================================================

-- Adaugă adresă detaliată pentru imobil
ALTER TABLE imobile ADD COLUMN IF NOT EXISTS judet TEXT;
ALTER TABLE imobile ADD COLUMN IF NOT EXISTS localitate TEXT;
ALTER TABLE imobile ADD COLUMN IF NOT EXISTS strada TEXT;
ALTER TABLE imobile ADD COLUMN IF NOT EXISTS numar TEXT;
ALTER TABLE imobile ADD COLUMN IF NOT EXISTS bloc TEXT;
ALTER TABLE imobile ADD COLUMN IF NOT EXISTS scara TEXT;
ALTER TABLE imobile ADD COLUMN IF NOT EXISTS etaj TEXT;
ALTER TABLE imobile ADD COLUMN IF NOT EXISTS apartament TEXT;
ALTER TABLE imobile ADD COLUMN IF NOT EXISTS cod_postal TEXT;
ALTER TABLE imobile ADD COLUMN IF NOT EXISTS numar_camere INTEGER;

-- Adaugă constrângere pentru număr de camere
ALTER TABLE imobile ADD CONSTRAINT numar_camere_pozitiv CHECK (numar_camere IS NULL OR numar_camere > 0);

-- Index pentru căutări după localitate
CREATE INDEX IF NOT EXISTS idx_imobile_localitate ON imobile(localitate);

-- ================================================================
-- PARTE 3: EXTINDERE TABEL CONTRACTE
-- ================================================================

-- Adaugă date complete despre Locatar
ALTER TABLE contracte ADD COLUMN IF NOT EXISTS locatar_tip TEXT CHECK (locatar_tip IN ('persoana_fizica', 'persoana_juridica'));
ALTER TABLE contracte ADD COLUMN IF NOT EXISTS locatar_email TEXT;
ALTER TABLE contracte ADD COLUMN IF NOT EXISTS locatar_telefon TEXT;
ALTER TABLE contracte ADD COLUMN IF NOT EXISTS locatar_adresa TEXT;

-- Adaugă date despre contract
ALTER TABLE contracte ADD COLUMN IF NOT EXISTS data_contract DATE;
ALTER TABLE contracte ADD COLUMN IF NOT EXISTS numar_camere_inchiriate INTEGER;
ALTER TABLE contracte ADD COLUMN IF NOT EXISTS frecventa_plata TEXT CHECK (frecventa_plata IN ('lunar', 'trimestrial', 'semestrial', 'anual'));

-- Setează valori default pentru înregistrări existente
UPDATE contracte SET locatar_tip = 'persoana_fizica' WHERE locatar_tip IS NULL;
UPDATE contracte SET frecventa_plata = 'lunar' WHERE frecventa_plata IS NULL;
UPDATE contracte SET data_contract = data_inceput WHERE data_contract IS NULL;

-- Adaugă constrângeri
ALTER TABLE contracte ADD CONSTRAINT numar_camere_inchiriate_pozitiv
    CHECK (numar_camere_inchiriate IS NULL OR numar_camere_inchiriate > 0);
ALTER TABLE contracte ADD CONSTRAINT data_contract_valida
    CHECK (data_contract IS NULL OR data_contract <= data_inceput);

-- Index pentru căutări
CREATE INDEX IF NOT EXISTS idx_contracte_locatar_email ON contracte(locatar_email);
CREATE INDEX IF NOT EXISTS idx_contracte_data_contract ON contracte(data_contract);

-- ================================================================
-- PARTE 4: FUNCȚII HELPER PENTRU VALIDĂRI
-- ================================================================

-- Funcție pentru validare CNP românesc
CREATE OR REPLACE FUNCTION validate_cnp(cnp_value TEXT)
RETURNS BOOLEAN AS $$
DECLARE
    control_sum INTEGER := 0;
    control_digit INTEGER;
    weights INTEGER[] := ARRAY[2,7,9,1,4,6,3,5,8,2,7,9];
    i INTEGER;
BEGIN
    -- Verifică lungime
    IF LENGTH(cnp_value) != 13 THEN
        RETURN FALSE;
    END IF;

    -- Verifică dacă sunt doar cifre
    IF cnp_value !~ '^[0-9]+$' THEN
        RETURN FALSE;
    END IF;

    -- Calculează suma de control
    FOR i IN 1..12 LOOP
        control_sum := control_sum + (SUBSTRING(cnp_value FROM i FOR 1)::INTEGER * weights[i]);
    END LOOP;

    control_digit := control_sum % 11;
    IF control_digit = 10 THEN
        control_digit := 1;
    END IF;

    -- Verifică cifra de control
    RETURN control_digit = SUBSTRING(cnp_value FROM 13 FOR 1)::INTEGER;
END;
$$ LANGUAGE plpgsql;

-- Funcție pentru validare CUI românesc
CREATE OR REPLACE FUNCTION validate_cui(cui_value TEXT)
RETURNS BOOLEAN AS $$
BEGIN
    -- Elimină spații și prefix RO
    cui_value := REGEXP_REPLACE(UPPER(cui_value), '[^0-9]', '', 'g');

    -- Verifică lungime (2-10 cifre)
    IF LENGTH(cui_value) < 2 OR LENGTH(cui_value) > 10 THEN
        RETURN FALSE;
    END IF;

    -- Verifică dacă sunt doar cifre
    IF cui_value !~ '^[0-9]+$' THEN
        RETURN FALSE;
    END IF;

    RETURN TRUE;
END;
$$ LANGUAGE plpgsql;

-- Funcție pentru formatare adresă completă
CREATE OR REPLACE FUNCTION format_adresa_completa(
    p_judet TEXT,
    p_localitate TEXT,
    p_strada TEXT,
    p_numar TEXT,
    p_bloc TEXT DEFAULT NULL,
    p_scara TEXT DEFAULT NULL,
    p_etaj TEXT DEFAULT NULL,
    p_apartament TEXT DEFAULT NULL,
    p_cod_postal TEXT DEFAULT NULL
)
RETURNS TEXT AS $$
DECLARE
    adresa TEXT := '';
BEGIN
    -- Strada și număr
    IF p_strada IS NOT NULL THEN
        adresa := adresa || 'Str. ' || p_strada;
    END IF;

    IF p_numar IS NOT NULL THEN
        adresa := adresa || ' nr. ' || p_numar;
    END IF;

    -- Bloc
    IF p_bloc IS NOT NULL THEN
        adresa := adresa || ', bl. ' || p_bloc;
    END IF;

    -- Scara
    IF p_scara IS NOT NULL THEN
        adresa := adresa || ', sc. ' || p_scara;
    END IF;

    -- Etaj
    IF p_etaj IS NOT NULL THEN
        adresa := adresa || ', et. ' || p_etaj;
    END IF;

    -- Apartament
    IF p_apartament IS NOT NULL THEN
        adresa := adresa || ', ap. ' || p_apartament;
    END IF;

    -- Localitate și județ
    IF p_localitate IS NOT NULL THEN
        adresa := adresa || ', ' || p_localitate;
    END IF;

    IF p_judet IS NOT NULL THEN
        adresa := adresa || ', jud. ' || p_judet;
    END IF;

    -- Cod poștal
    IF p_cod_postal IS NOT NULL THEN
        adresa := adresa || ', ' || p_cod_postal;
    END IF;

    RETURN TRIM(adresa);
END;
$$ LANGUAGE plpgsql;

-- ================================================================
-- PARTE 5: VIEW-URI PENTRU RAPORTARE ANAF
-- ================================================================

-- View pentru contracte cu toate datele ANAF
CREATE OR REPLACE VIEW view_contracte_anaf AS
SELECT
    c.id AS contract_id,
    c.nr_contract,
    c.data_contract,
    c.data_inceput,
    c.data_sfarsit,

    -- Date Proprietar (Locator)
    u.nume AS proprietar_nume,
    u.cnp AS proprietar_cnp,
    u.email AS proprietar_email,
    u.telefon AS proprietar_telefon,
    format_adresa_completa(
        u.judet, u.localitate, u.strada, u.numar,
        u.bloc, u.scara, u.etaj, u.apartament, u.cod_postal
    ) AS proprietar_adresa,

    -- Date Locatar
    c.locatar AS locatar_nume,
    c.locatar_tip,
    c.cnp_cui AS locatar_cnp_cui,
    c.locatar_email,
    c.locatar_telefon,
    c.locatar_adresa,

    -- Date Imobil
    i.nume AS imobil_nume,
    format_adresa_completa(
        i.judet, i.localitate, i.strada, i.numar,
        i.bloc, i.scara, i.etaj, i.apartament, i.cod_postal
    ) AS imobil_adresa,
    i.numar_camere AS imobil_camere_total,
    c.numar_camere_inchiriate,

    -- Date Financiare
    c.chirie_lunara,
    c.moneda,
    c.frecventa_plata,

    -- Calcul automat chirie anuală
    CASE
        WHEN c.frecventa_plata = 'lunar' THEN c.chirie_lunara * 12
        WHEN c.frecventa_plata = 'trimestrial' THEN c.chirie_lunara * 4
        WHEN c.frecventa_plata = 'semestrial' THEN c.chirie_lunara * 2
        WHEN c.frecventa_plata = 'anual' THEN c.chirie_lunara
        ELSE c.chirie_lunara * 12
    END AS venit_anual_brut

FROM contracte c
JOIN users u ON c.user_id = u.id
JOIN imobile i ON c.imobil_id = i.id
ORDER BY c.data_inceput DESC;

-- ================================================================
-- PARTE 6: VERIFICĂRI FINALE
-- ================================================================

-- Verifică coloanele noi din users
SELECT
    '✅ USERS - Coloane noi adăugate:' AS status,
    COUNT(*) FILTER (WHERE cnp IS NOT NULL) AS users_cu_cnp,
    COUNT(*) FILTER (WHERE telefon IS NOT NULL) AS users_cu_telefon,
    COUNT(*) FILTER (WHERE judet IS NOT NULL) AS users_cu_adresa
FROM users;

-- Verifică coloanele noi din imobile
SELECT
    '✅ IMOBILE - Coloane noi adăugate:' AS status,
    COUNT(*) FILTER (WHERE judet IS NOT NULL) AS imobile_cu_adresa_detaliata,
    COUNT(*) FILTER (WHERE numar_camere IS NOT NULL) AS imobile_cu_nr_camere
FROM imobile;

-- Verifică coloanele noi din contracte
SELECT
    '✅ CONTRACTE - Coloane noi adăugate:' AS status,
    COUNT(*) FILTER (WHERE locatar_tip IS NOT NULL) AS contracte_cu_tip_locatar,
    COUNT(*) FILTER (WHERE data_contract IS NOT NULL) AS contracte_cu_data_contract,
    COUNT(*) FILTER (WHERE frecventa_plata IS NOT NULL) AS contracte_cu_frecventa
FROM contracte;

-- Mesaj final
SELECT
    '✅ MIGRATION COMPLETĂ!' AS status,
    'Toate coloanele necesare pentru ANAF D212 au fost adăugate.' AS message,
    'Următorul pas: actualizează formularele în aplicația Streamlit.' AS next_step;
