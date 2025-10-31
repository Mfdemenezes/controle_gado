-- ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
-- CORREÇÃO: Views e Tabelas Lotes/Pastos
-- ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

-- ============================================================
-- 1. CRIAR TABELAS LOTES E PASTOS (SE NÃO EXISTIREM COM IDs)
-- ============================================================

-- Verificar e criar lotes se não existe
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'lotes') THEN
        CREATE TABLE lotes (
            id SERIAL PRIMARY KEY,
            nome VARCHAR(100) NOT NULL UNIQUE,
            descricao TEXT,
            capacidade INTEGER,
            ativo BOOLEAN DEFAULT true,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        RAISE NOTICE 'Tabela lotes criada';
    ELSE
        RAISE NOTICE 'Tabela lotes já existe';
    END IF;
END $$;

-- Verificar e criar pastos
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'pastos') THEN
        CREATE TABLE pastos (
            id SERIAL PRIMARY KEY,
            nome VARCHAR(100) NOT NULL UNIQUE,
            area_hectares NUMERIC(10,2),
            tipo VARCHAR(50),
            descricao TEXT,
            ativo BOOLEAN DEFAULT true,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        RAISE NOTICE 'Tabela pastos criada';
    ELSE
        RAISE NOTICE 'Tabela pastos já existe';
    END IF;
END $$;

-- Adicionar colunas lote_id e pasto_id na tabela animais
ALTER TABLE animais ADD COLUMN IF NOT EXISTS lote_id INTEGER REFERENCES lotes(id);
ALTER TABLE animais ADD COLUMN IF NOT EXISTS pasto_id INTEGER REFERENCES pastos(id);

-- Migrar dados antigos (se houver)
-- Inserir lotes únicos
INSERT INTO lotes (nome)
SELECT DISTINCT lote
FROM animais
WHERE lote IS NOT NULL AND lote != ''
ON CONFLICT (nome) DO NOTHING;

-- Inserir pastos únicos
INSERT INTO pastos (nome)
SELECT DISTINCT pasto
FROM animais
WHERE pasto IS NOT NULL AND pasto != ''
ON CONFLICT (nome) DO NOTHING;

-- Atualizar lote_id
UPDATE animais a
SET lote_id = l.id
FROM lotes l
WHERE a.lote = l.nome
  AND a.lote_id IS NULL;

-- Atualizar pasto_id
UPDATE animais a
SET pasto_id = p.id
FROM pastos p
WHERE a.pasto = p.nome
  AND a.pasto_id IS NULL;

-- ============================================================
-- 2. RECRIAR VIEWS CORRIGIDAS
-- ============================================================

-- View: Animais com informações completas
DROP VIEW IF EXISTS v_animais_completo CASCADE;
CREATE VIEW v_animais_completo AS
SELECT 
    a.id,
    a.brinco,
    a.nome,
    a.sexo,
    a.data_nascimento,
    EXTRACT(YEAR FROM AGE(CURRENT_DATE, a.data_nascimento)) * 12 + 
    EXTRACT(MONTH FROM AGE(CURRENT_DATE, a.data_nascimento)) as idade_meses,
    COALESCE(r.nome, a.raca) as raca,
    c.nome as categoria,
    a.peso_atual,
    COALESCE(l.nome, a.lote) as lote,
    COALESCE(p.nome, a.pasto) as pasto,
    a.status_reprodutivo,
    a.foto_url,
    mae.brinco as mae_brinco,
    t.brinco as pai_brinco,
    a.status,
    a.created_at
FROM animais a
LEFT JOIN racas r ON a.raca_id = r.id
LEFT JOIN categorias c ON a.categoria_id = c.id
LEFT JOIN lotes l ON a.lote_id = l.id
LEFT JOIN pastos p ON a.pasto_id = p.id
LEFT JOIN animais mae ON a.mae_id = mae.id
LEFT JOIN touros t ON a.pai_id = t.id;

-- View: Fêmeas em idade reprodutiva
DROP VIEW IF EXISTS v_femeas_reprodutivas CASCADE;
CREATE VIEW v_femeas_reprodutivas AS
SELECT 
    a.id,
    a.brinco,
    a.nome,
    a.sexo,
    a.data_nascimento,
    EXTRACT(YEAR FROM AGE(CURRENT_DATE, a.data_nascimento)) * 12 + 
    EXTRACT(MONTH FROM AGE(CURRENT_DATE, a.data_nascimento)) as idade_meses,
    COALESCE(r.nome, a.raca) as raca,
    c.nome as categoria,
    COALESCE(a.status_reprodutivo, 'vazia') as status_reprodutivo,
    a.peso_atual
FROM animais a
LEFT JOIN racas r ON a.raca_id = r.id
LEFT JOIN categorias c ON a.categoria_id = c.id
WHERE a.sexo = 'F' 
  AND (
    EXTRACT(YEAR FROM AGE(CURRENT_DATE, a.data_nascimento)) * 12 + 
    EXTRACT(MONTH FROM AGE(CURRENT_DATE, a.data_nascimento))
  ) >= 12
ORDER BY a.brinco;

-- View: Estatísticas reprodutivas
DROP VIEW IF EXISTS v_stats_reproducao CASCADE;
CREATE VIEW v_stats_reproducao AS
SELECT 
    COUNT(*) FILTER (WHERE status_reprodutivo = 'prenhe') as total_prenhas,
    COUNT(*) FILTER (WHERE status_reprodutivo = 'vazia') as total_vazias,
    COUNT(*) FILTER (WHERE status_reprodutivo = 'inseminada') as total_inseminadas,
    COUNT(*) FILTER (WHERE status_reprodutivo = 'a_diagnosticar') as total_a_diagnosticar,
    COUNT(*) FILTER (WHERE status_reprodutivo = 'recem_parida') as total_recem_paridas,
    COUNT(*) FILTER (WHERE sexo = 'F' AND 
        (EXTRACT(YEAR FROM AGE(CURRENT_DATE, data_nascimento)) * 12 + 
         EXTRACT(MONTH FROM AGE(CURRENT_DATE, data_nascimento))) >= 12
    ) as total_femeas_reprodutivas
FROM animais
WHERE sexo = 'F';

-- ============================================================
-- 3. ÍNDICES ADICIONAIS
-- ============================================================
CREATE INDEX IF NOT EXISTS idx_animais_lote_id ON animais(lote_id);
CREATE INDEX IF NOT EXISTS idx_animais_pasto_id ON animais(pasto_id);

-- Log
DO $$
BEGIN
    RAISE NOTICE '✅ Views e tabelas corrigidas com sucesso!';
END $$;
