-- Remover trigger primeiro
DROP TRIGGER IF EXISTS trg_animais_categoria ON animais;

-- Recriar função com tipos corretos
CREATE OR REPLACE FUNCTION fn_calcular_categoria(
    p_sexo CHAR(1),
    p_idade_meses NUMERIC
) RETURNS INTEGER AS $$
DECLARE
    v_categoria_id INTEGER;
BEGIN
    SELECT id INTO v_categoria_id
    FROM categorias
    WHERE sexo = p_sexo
      AND idade_min_meses <= p_idade_meses::INTEGER
      AND (idade_max_meses IS NULL OR idade_max_meses >= p_idade_meses::INTEGER)
    ORDER BY idade_min_meses DESC
    LIMIT 1;
    
    RETURN v_categoria_id;
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- Recriar trigger SIMPLIFICADO (sem calcular categoria automaticamente no insert)
-- Isso evita problemas quando data_nascimento é NULL
CREATE OR REPLACE FUNCTION trg_atualizar_categoria()
RETURNS TRIGGER AS $$
BEGIN
    -- Só calcular se tiver data de nascimento
    IF NEW.data_nascimento IS NOT NULL AND NEW.sexo IS NOT NULL THEN
        NEW.categoria_id := fn_calcular_categoria(
            NEW.sexo,
            EXTRACT(YEAR FROM AGE(CURRENT_DATE, NEW.data_nascimento)) * 12 + 
            EXTRACT(MONTH FROM AGE(CURRENT_DATE, NEW.data_nascimento))
        );
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_animais_categoria
    BEFORE INSERT OR UPDATE OF data_nascimento, sexo
    ON animais
    FOR EACH ROW
    EXECUTE FUNCTION trg_atualizar_categoria();

-- Log
DO $$
BEGIN
    RAISE NOTICE '✅ Função e trigger corrigidos!';
END $$;
