-- ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
-- MIGRAÇÃO v2.0 - Sistema Reprodutivo Completo
-- ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

-- ============================================================
-- 1. TABELA: racas
-- ============================================================
CREATE TABLE IF NOT EXISTS racas (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL UNIQUE,
    descricao TEXT,
    origem VARCHAR(100),
    caracteristicas TEXT,
    ativo BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE racas IS 'Raças de gado bovino';
COMMENT ON COLUMN racas.nome IS 'Nome da raça (ex: Nelore, Angus, Brahman)';
COMMENT ON COLUMN racas.origem IS 'País/região de origem';

-- ============================================================
-- 2. TABELA: categorias (idades)
-- ============================================================
CREATE TABLE IF NOT EXISTS categorias (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(50) NOT NULL UNIQUE,
    sexo CHAR(1) NOT NULL CHECK (sexo IN ('M', 'F')),
    idade_min_meses INTEGER NOT NULL,
    idade_max_meses INTEGER,
    descricao TEXT,
    ordem INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE categorias IS 'Categorias de animais por idade e sexo';
COMMENT ON COLUMN categorias.nome IS 'Ex: Bezerro, Bezerra, Garrote, Novilha, Touro, Vaca';

-- Inserir categorias padrão
INSERT INTO categorias (nome, sexo, idade_min_meses, idade_max_meses, descricao, ordem) VALUES
('Bezerro', 'M', 0, 12, 'Macho de 0 a 12 meses', 1),
('Bezerra', 'F', 0, 12, 'Fêmea de 0 a 12 meses', 2),
('Garrote', 'M', 12, 24, 'Macho de 12 a 24 meses', 3),
('Novilha', 'F', 12, 36, 'Fêmea de 12 a 36 meses (pré-primeira cria)', 4),
('Touro', 'M', 24, NULL, 'Macho adulto acima de 24 meses', 5),
('Vaca', 'F', 36, NULL, 'Fêmea adulta acima de 36 meses ou com cria', 6)
ON CONFLICT (nome) DO NOTHING;

-- ============================================================
-- 3. TABELA: touros (reprodutores)
-- ============================================================
CREATE TABLE IF NOT EXISTS touros (
    id SERIAL PRIMARY KEY,
    brinco VARCHAR(50) UNIQUE NOT NULL,
    nome VARCHAR(100),
    raca_id INTEGER REFERENCES racas(id),
    data_nascimento DATE,
    registro VARCHAR(100),
    linhagem TEXT,
    ativo BOOLEAN DEFAULT true,
    observacoes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE touros IS 'Cadastro de touros/reprodutores para IA';
COMMENT ON COLUMN touros.registro IS 'Registro genealógico';
COMMENT ON COLUMN touros.linhagem IS 'Informações de linhagem/pedigree';

-- ============================================================
-- 4. ATUALIZAR TABELA: animais (adicionar novos campos)
-- ============================================================

-- Adicionar colunas se não existirem
ALTER TABLE animais ADD COLUMN IF NOT EXISTS raca_id INTEGER REFERENCES racas(id);
ALTER TABLE animais ADD COLUMN IF NOT EXISTS categoria_id INTEGER REFERENCES categorias(id);
ALTER TABLE animais ADD COLUMN IF NOT EXISTS data_nascimento DATE;
ALTER TABLE animais ADD COLUMN IF NOT EXISTS idade_meses INTEGER GENERATED ALWAYS AS (
    EXTRACT(YEAR FROM AGE(CURRENT_DATE, data_nascimento)) * 12 + 
    EXTRACT(MONTH FROM AGE(CURRENT_DATE, data_nascimento))
) STORED;
ALTER TABLE animais ADD COLUMN IF NOT EXISTS status_reprodutivo VARCHAR(30);
ALTER TABLE animais ADD COLUMN IF NOT EXISTS mae_id INTEGER REFERENCES animais(id);
ALTER TABLE animais ADD COLUMN IF NOT EXISTS pai_id INTEGER REFERENCES touros(id);
ALTER TABLE animais ADD COLUMN IF NOT EXISTS foto_url VARCHAR(500);

COMMENT ON COLUMN animais.status_reprodutivo IS 'vazia, inseminada, a_diagnosticar, prenhe, recem_parida, nao_aplicavel';
COMMENT ON COLUMN animais.idade_meses IS 'Idade calculada automaticamente em meses';

-- Índices para performance
CREATE INDEX IF NOT EXISTS idx_animais_raca ON animais(raca_id);
CREATE INDEX IF NOT EXISTS idx_animais_categoria ON animais(categoria_id);
CREATE INDEX IF NOT EXISTS idx_animais_status_reprod ON animais(status_reprodutivo);
CREATE INDEX IF NOT EXISTS idx_animais_data_nasc ON animais(data_nascimento);

-- ============================================================
-- 5. TABELA: eventos_reprodutivos
-- ============================================================
CREATE TABLE IF NOT EXISTS eventos_reprodutivos (
    id SERIAL PRIMARY KEY,
    animal_id INTEGER NOT NULL REFERENCES animais(id) ON DELETE CASCADE,
    tipo_evento VARCHAR(30) NOT NULL CHECK (tipo_evento IN (
        'inseminacao',
        'diagnostico_positivo',
        'diagnostico_negativo',
        'parto',
        'aborto',
        'cio'
    )),
    data_evento DATE NOT NULL,
    data_prevista DATE,
    touro_id INTEGER REFERENCES touros(id),
    bezerra_id INTEGER REFERENCES animais(id),
    natimorto BOOLEAN DEFAULT false,
    observacoes TEXT,
    usuario_id INTEGER REFERENCES usuarios(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE eventos_reprodutivos IS 'Histórico completo de eventos reprodutivos';
COMMENT ON COLUMN eventos_reprodutivos.tipo_evento IS 'Tipo: inseminacao, diagnostico, parto, aborto, cio';
COMMENT ON COLUMN eventos_reprodutivos.data_prevista IS 'Data prevista de parto (calculada)';
COMMENT ON COLUMN eventos_reprodutivos.bezerra_id IS 'ID do bezerro nascido (se aplicável)';

-- Índices
CREATE INDEX IF NOT EXISTS idx_eventos_animal ON eventos_reprodutivos(animal_id);
CREATE INDEX IF NOT EXISTS idx_eventos_tipo ON eventos_reprodutivos(tipo_evento);
CREATE INDEX IF NOT EXISTS idx_eventos_data ON eventos_reprodutivos(data_evento);

-- ============================================================
-- 6. VIEWS ÚTEIS
-- ============================================================

-- View: Animais com informações completas
CREATE OR REPLACE VIEW v_animais_completo AS
SELECT 
    a.id,
    a.brinco,
    a.nome,
    a.sexo,
    a.data_nascimento,
    a.idade_meses,
    r.nome as raca,
    c.nome as categoria,
    a.peso_atual,
    l.nome as lote,
    p.nome as pasto,
    a.status_reprodutivo,
    a.foto_url,
    mae.brinco as mae_brinco,
    t.brinco as pai_brinco,
    a.created_at
FROM animais a
LEFT JOIN racas r ON a.raca_id = r.id
LEFT JOIN categorias c ON a.categoria_id = c.id
LEFT JOIN lotes l ON a.lote_id = l.id
LEFT JOIN pastos p ON a.pasto_id = p.id
LEFT JOIN animais mae ON a.mae_id = mae.id
LEFT JOIN touros t ON a.pai_id = t.id;

-- View: Fêmeas em idade reprodutiva
CREATE OR REPLACE VIEW v_femeas_reprodutivas AS
SELECT 
    a.*,
    r.nome as raca,
    c.nome as categoria,
    COALESCE(a.status_reprodutivo, 'vazia') as status_atual
FROM animais a
LEFT JOIN racas r ON a.raca_id = r.id
LEFT JOIN categorias c ON a.categoria_id = c.id
WHERE a.sexo = 'F' 
  AND a.idade_meses >= 12
ORDER BY a.brinco;

-- View: Próximos eventos (partos, diagnósticos)
CREATE OR REPLACE VIEW v_proximos_eventos AS
SELECT 
    er.id,
    a.brinco,
    a.nome,
    er.tipo_evento,
    er.data_evento,
    er.data_prevista,
    er.data_prevista - CURRENT_DATE as dias_restantes,
    t.brinco as touro
FROM eventos_reprodutivos er
JOIN animais a ON er.animal_id = a.id
LEFT JOIN touros t ON er.touro_id = t.id
WHERE er.data_prevista IS NOT NULL
  AND er.data_prevista >= CURRENT_DATE
ORDER BY er.data_prevista;

-- View: Estatísticas reprodutivas
CREATE OR REPLACE VIEW v_stats_reproducao AS
SELECT 
    COUNT(*) FILTER (WHERE status_reprodutivo = 'prenhe') as total_prenhas,
    COUNT(*) FILTER (WHERE status_reprodutivo = 'vazia') as total_vazias,
    COUNT(*) FILTER (WHERE status_reprodutivo = 'inseminada') as total_inseminadas,
    COUNT(*) FILTER (WHERE status_reprodutivo = 'a_diagnosticar') as total_a_diagnosticar,
    COUNT(*) FILTER (WHERE status_reprodutivo = 'recem_parida') as total_recem_paridas,
    COUNT(*) FILTER (WHERE sexo = 'F' AND idade_meses >= 12) as total_femeas_reprodutivas
FROM animais
WHERE sexo = 'F';

-- ============================================================
-- 7. FUNÇÕES ÚTEIS
-- ============================================================

-- Função: Calcular categoria por idade
CREATE OR REPLACE FUNCTION fn_calcular_categoria(
    p_sexo CHAR(1),
    p_idade_meses INTEGER
) RETURNS INTEGER AS $$
DECLARE
    v_categoria_id INTEGER;
BEGIN
    SELECT id INTO v_categoria_id
    FROM categorias
    WHERE sexo = p_sexo
      AND idade_min_meses <= p_idade_meses
      AND (idade_max_meses IS NULL OR idade_max_meses >= p_idade_meses)
    ORDER BY idade_min_meses DESC
    LIMIT 1;
    
    RETURN v_categoria_id;
END;
$$ LANGUAGE plpgsql;

-- Função: Calcular data prevista de parto
CREATE OR REPLACE FUNCTION fn_data_prevista_parto(
    p_data_ia DATE
) RETURNS DATE AS $$
BEGIN
    -- Gestação bovina: 283 dias em média
    RETURN p_data_ia + INTERVAL '283 days';
END;
$$ LANGUAGE plpgsql;

-- Função: Calcular data de diagnóstico
CREATE OR REPLACE FUNCTION fn_data_diagnostico(
    p_data_ia DATE
) RETURNS DATE AS $$
BEGIN
    -- Diagnóstico: 45 dias após IA
    RETURN p_data_ia + INTERVAL '45 days';
END;
$$ LANGUAGE plpgsql;

-- ============================================================
-- 8. TRIGGERS
-- ============================================================

-- Trigger: Atualizar categoria automaticamente ao inserir/atualizar animal
CREATE OR REPLACE FUNCTION trg_atualizar_categoria()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.data_nascimento IS NOT NULL THEN
        NEW.categoria_id := fn_calcular_categoria(
            NEW.sexo,
            EXTRACT(YEAR FROM AGE(CURRENT_DATE, NEW.data_nascimento)) * 12 + 
            EXTRACT(MONTH FROM AGE(CURRENT_DATE, NEW.data_nascimento))
        );
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_animais_categoria ON animais;
CREATE TRIGGER trg_animais_categoria
    BEFORE INSERT OR UPDATE OF data_nascimento, sexo
    ON animais
    FOR EACH ROW
    EXECUTE FUNCTION trg_atualizar_categoria();

-- Trigger: Ao registrar IA, calcular data prevista de parto
CREATE OR REPLACE FUNCTION trg_calcular_datas_ia()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.tipo_evento = 'inseminacao' THEN
        NEW.data_prevista := fn_data_prevista_parto(NEW.data_evento);
        
        -- Atualizar status do animal
        UPDATE animais 
        SET status_reprodutivo = 'inseminada'
        WHERE id = NEW.animal_id;
    END IF;
    
    IF NEW.tipo_evento = 'diagnostico_positivo' THEN
        UPDATE animais 
        SET status_reprodutivo = 'prenhe'
        WHERE id = NEW.animal_id;
    END IF;
    
    IF NEW.tipo_evento = 'diagnostico_negativo' THEN
        UPDATE animais 
        SET status_reprodutivo = 'vazia'
        WHERE id = NEW.animal_id;
    END IF;
    
    IF NEW.tipo_evento = 'parto' THEN
        UPDATE animais 
        SET status_reprodutivo = 'recem_parida'
        WHERE id = NEW.animal_id;
        
        -- Se não for natimorto e bezerra_id está preenchido, atualizar mãe do bezerro
        IF NOT NEW.natimorto AND NEW.bezerra_id IS NOT NULL THEN
            UPDATE animais
            SET mae_id = NEW.animal_id
            WHERE id = NEW.bezerra_id;
        END IF;
    END IF;
    
    IF NEW.tipo_evento = 'aborto' THEN
        UPDATE animais 
        SET status_reprodutivo = 'vazia'
        WHERE id = NEW.animal_id;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_eventos_reproducao ON eventos_reprodutivos;
CREATE TRIGGER trg_eventos_reproducao
    BEFORE INSERT
    ON eventos_reprodutivos
    FOR EACH ROW
    EXECUTE FUNCTION trg_calcular_datas_ia();

-- ============================================================
-- 9. GRANTS (permissões)
-- ============================================================

-- Garantir que o usuário da aplicação tem acesso
GRANT ALL ON ALL TABLES IN SCHEMA public TO postgres;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO postgres;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO postgres;

-- ============================================================
-- FIM DA MIGRAÇÃO v2.0
-- ============================================================

-- Log de sucesso
DO $$
BEGIN
    RAISE NOTICE '✅ Migração v2.0 - Sistema Reprodutivo Completo instalado com sucesso!';
    RAISE NOTICE '';
    RAISE NOTICE '📊 Tabelas criadas:';
    RAISE NOTICE '   - racas';
    RAISE NOTICE '   - categorias (6 categorias pré-cadastradas)';
    RAISE NOTICE '   - touros';
    RAISE NOTICE '   - eventos_reprodutivos';
    RAISE NOTICE '   - animais (atualizada com novos campos)';
    RAISE NOTICE '';
    RAISE NOTICE '📈 Views criadas:';
    RAISE NOTICE '   - v_animais_completo';
    RAISE NOTICE '   - v_femeas_reprodutivas';
    RAISE NOTICE '   - v_proximos_eventos';
    RAISE NOTICE '   - v_stats_reproducao';
    RAISE NOTICE '';
    RAISE NOTICE '⚡ Triggers e funções ativados!';
END $$;
