-- Schema PostgreSQL para Sistema de Controle de Gado de Corte

-- Extensões úteis
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Tabela de Animais
CREATE TABLE IF NOT EXISTS animais (
    id SERIAL PRIMARY KEY,
    brinco VARCHAR(50) UNIQUE NOT NULL,
    nome VARCHAR(100),
    sexo CHAR(1) CHECK(sexo IN ('M', 'F')),
    raca VARCHAR(100),
    data_nascimento DATE,
    peso_nascimento NUMERIC(10,2),
    peso_atual NUMERIC(10,2),
    status VARCHAR(50) CHECK(status IN ('ativo', 'vendido', 'morto', 'transferido', 'inativo')) DEFAULT 'ativo',
    lote VARCHAR(50),
    pasto VARCHAR(50),
    pai_id INTEGER REFERENCES animais(id),
    mae_id INTEGER REFERENCES animais(id),
    observacoes TEXT,
    data_entrada DATE NOT NULL DEFAULT CURRENT_DATE,
    data_saida DATE,
    valor_compra NUMERIC(10,2),
    origem VARCHAR(200),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de Pesagens
CREATE TABLE IF NOT EXISTS pesagens (
    id SERIAL PRIMARY KEY,
    animal_id INTEGER NOT NULL REFERENCES animais(id) ON DELETE CASCADE,
    data_pesagem DATE NOT NULL DEFAULT CURRENT_DATE,
    peso NUMERIC(10,2) NOT NULL,
    ganho_peso NUMERIC(10,2),
    gmd NUMERIC(10,3), -- Ganho Médio Diário
    condicao_corporal INTEGER CHECK(condicao_corporal BETWEEN 1 AND 5),
    observacoes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de Sanidade (Vacinas, Medicamentos, etc)
CREATE TABLE IF NOT EXISTS sanidade (
    id SERIAL PRIMARY KEY,
    animal_id INTEGER NOT NULL REFERENCES animais(id) ON DELETE CASCADE,
    data_aplicacao DATE NOT NULL DEFAULT CURRENT_DATE,
    tipo VARCHAR(50) CHECK(tipo IN ('vacina', 'vermifugo', 'antibiotico', 'carrapaticida', 'outro')),
    produto VARCHAR(200) NOT NULL,
    dose VARCHAR(50),
    aplicador VARCHAR(100),
    proxima_aplicacao DATE,
    observacoes TEXT,
    custo NUMERIC(10,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de Reprodução
CREATE TABLE IF NOT EXISTS reproducao (
    id SERIAL PRIMARY KEY,
    femea_id INTEGER NOT NULL REFERENCES animais(id) ON DELETE CASCADE,
    macho_id INTEGER REFERENCES animais(id),
    tipo_cobertura VARCHAR(50) CHECK(tipo_cobertura IN ('monta natural', 'inseminacao', 'transferencia embriao')),
    data_cobertura DATE NOT NULL,
    data_diagnostico DATE,
    resultado VARCHAR(50) CHECK(resultado IN ('prenha', 'vazia', 'aguardando')) DEFAULT 'aguardando',
    data_prevista_parto DATE,
    data_parto DATE,
    cria_id INTEGER REFERENCES animais(id),
    observacoes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de Movimentações (Troca de Pasto/Lote)
CREATE TABLE IF NOT EXISTS movimentacoes (
    id SERIAL PRIMARY KEY,
    animal_id INTEGER NOT NULL REFERENCES animais(id) ON DELETE CASCADE,
    data_movimentacao DATE NOT NULL DEFAULT CURRENT_DATE,
    tipo VARCHAR(50) CHECK(tipo IN ('troca_pasto', 'troca_lote', 'entrada', 'saida')),
    origem VARCHAR(100),
    destino VARCHAR(100),
    motivo TEXT,
    responsavel VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de Vendas
CREATE TABLE IF NOT EXISTS vendas (
    id SERIAL PRIMARY KEY,
    animal_id INTEGER NOT NULL REFERENCES animais(id),
    data_venda DATE NOT NULL,
    comprador VARCHAR(200),
    peso_venda NUMERIC(10,2),
    valor_arroba NUMERIC(10,2),
    valor_total NUMERIC(10,2),
    forma_pagamento VARCHAR(50),
    observacoes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de Despesas
CREATE TABLE IF NOT EXISTS despesas (
    id SERIAL PRIMARY KEY,
    data_despesa DATE NOT NULL DEFAULT CURRENT_DATE,
    categoria VARCHAR(100) NOT NULL,
    descricao TEXT,
    valor NUMERIC(10,2) NOT NULL,
    animal_id INTEGER REFERENCES animais(id),
    lote VARCHAR(50),
    fornecedor VARCHAR(200),
    forma_pagamento VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de Pastos
CREATE TABLE IF NOT EXISTS pastos (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) UNIQUE NOT NULL,
    area_hectares NUMERIC(10,2),
    tipo_capim VARCHAR(100),
    capacidade_animais INTEGER,
    status VARCHAR(50) CHECK(status IN ('disponivel', 'ocupado', 'reforma', 'descanso', 'encerrado')) DEFAULT 'disponivel',
    data_ultimo_manejo DATE,
    observacoes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de Lotes
CREATE TABLE IF NOT EXISTS lotes (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) UNIQUE NOT NULL,
    descricao TEXT,
    data_formacao DATE DEFAULT CURRENT_DATE,
    finalidade VARCHAR(100),
    status VARCHAR(50) CHECK(status IN ('ativo', 'encerrado')) DEFAULT 'ativo',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de Usuários (para controle de acesso mobile)
CREATE TABLE IF NOT EXISTS usuarios (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    senha_hash VARCHAR(255) NOT NULL,
    telefone VARCHAR(20),
    nivel_acesso VARCHAR(20) CHECK(nivel_acesso IN ('admin', 'gerente', 'operador')) DEFAULT 'operador',
    ativo BOOLEAN DEFAULT TRUE,
    ultimo_acesso TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de Sessões/Tokens (para autenticação mobile)
CREATE TABLE IF NOT EXISTS sessoes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    usuario_id INTEGER NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
    token VARCHAR(255) UNIQUE NOT NULL,
    dispositivo VARCHAR(100),
    ip_address VARCHAR(45),
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índices para melhor performance
CREATE INDEX IF NOT EXISTS idx_animais_brinco ON animais(brinco);
CREATE INDEX IF NOT EXISTS idx_animais_status ON animais(status);
CREATE INDEX IF NOT EXISTS idx_animais_lote ON animais(lote);
CREATE INDEX IF NOT EXISTS idx_animais_pasto ON animais(pasto);
CREATE INDEX IF NOT EXISTS idx_pesagens_animal ON pesagens(animal_id);
CREATE INDEX IF NOT EXISTS idx_pesagens_data ON pesagens(data_pesagem DESC);
CREATE INDEX IF NOT EXISTS idx_sanidade_animal ON sanidade(animal_id);
CREATE INDEX IF NOT EXISTS idx_sanidade_proxima ON sanidade(proxima_aplicacao) WHERE proxima_aplicacao IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_reproducao_femea ON reproducao(femea_id);
CREATE INDEX IF NOT EXISTS idx_reproducao_resultado ON reproducao(resultado);
CREATE INDEX IF NOT EXISTS idx_movimentacoes_animal ON movimentacoes(animal_id);
CREATE INDEX IF NOT EXISTS idx_vendas_animal ON vendas(animal_id);
CREATE INDEX IF NOT EXISTS idx_vendas_data ON vendas(data_venda DESC);
CREATE INDEX IF NOT EXISTS idx_usuarios_email ON usuarios(email);
CREATE INDEX IF NOT EXISTS idx_sessoes_token ON sessoes(token);
CREATE INDEX IF NOT EXISTS idx_sessoes_usuario ON sessoes(usuario_id);

-- Trigger para atualizar updated_at automaticamente
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_animais_updated_at BEFORE UPDATE ON animais
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_usuarios_updated_at BEFORE UPDATE ON usuarios
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Views úteis para relatórios
CREATE OR REPLACE VIEW vw_rebanho_ativo AS
SELECT 
    a.*,
    p.peso as ultimo_peso,
    p.data_pesagem as data_ultimo_peso,
    EXTRACT(YEAR FROM AGE(CURRENT_DATE, a.data_nascimento)) as idade_anos,
    EXTRACT(MONTH FROM AGE(CURRENT_DATE, a.data_nascimento)) as idade_meses
FROM animais a
LEFT JOIN LATERAL (
    SELECT peso, data_pesagem
    FROM pesagens
    WHERE animal_id = a.id
    ORDER BY data_pesagem DESC
    LIMIT 1
) p ON true
WHERE a.status = 'ativo';

CREATE OR REPLACE VIEW vw_performance_animais AS
SELECT 
    a.id,
    a.brinco,
    a.nome,
    a.raca,
    a.sexo,
    a.lote,
    p1.peso as peso_inicial,
    p1.data_pesagem as data_pesagem_inicial,
    p2.peso as peso_final,
    p2.data_pesagem as data_pesagem_final,
    (p2.peso - p1.peso) as ganho_total,
    ROUND((p2.peso - p1.peso) / NULLIF(p2.data_pesagem - p1.data_pesagem, 0), 3) as gmd,
    (p2.data_pesagem - p1.data_pesagem) as dias_periodo
FROM animais a
INNER JOIN LATERAL (
    SELECT peso, data_pesagem
    FROM pesagens
    WHERE animal_id = a.id
    ORDER BY data_pesagem ASC
    LIMIT 1
) p1 ON true
INNER JOIN LATERAL (
    SELECT peso, data_pesagem
    FROM pesagens
    WHERE animal_id = a.id
    ORDER BY data_pesagem DESC
    LIMIT 1
) p2 ON true
WHERE a.status = 'ativo'
AND p1.data_pesagem < p2.data_pesagem;

CREATE OR REPLACE VIEW vw_resumo_rebanho AS
SELECT 
    COUNT(*) as total_animais,
    COUNT(*) FILTER (WHERE sexo = 'M') as total_machos,
    COUNT(*) FILTER (WHERE sexo = 'F') as total_femeas,
    AVG(peso_atual) as peso_medio,
    SUM(peso_atual) as peso_total,
    MIN(peso_atual) as peso_minimo,
    MAX(peso_atual) as peso_maximo
FROM animais
WHERE status = 'ativo';

CREATE OR REPLACE VIEW vw_aplicacoes_proximas AS
SELECT 
    s.id,
    s.animal_id,
    a.brinco,
    a.nome,
    s.tipo,
    s.produto,
    s.proxima_aplicacao,
    (s.proxima_aplicacao - CURRENT_DATE) as dias_restantes
FROM sanidade s
INNER JOIN animais a ON s.animal_id = a.id
WHERE s.proxima_aplicacao IS NOT NULL
AND s.proxima_aplicacao >= CURRENT_DATE
AND a.status = 'ativo'
ORDER BY s.proxima_aplicacao;

-- Função para calcular GMD de um animal
CREATE OR REPLACE FUNCTION calcular_gmd(p_animal_id INTEGER)
RETURNS NUMERIC AS $$
DECLARE
    v_gmd NUMERIC;
BEGIN
    SELECT 
        ROUND((p2.peso - p1.peso) / NULLIF(p2.data_pesagem - p1.data_pesagem, 0), 3)
    INTO v_gmd
    FROM (
        SELECT peso, data_pesagem
        FROM pesagens
        WHERE animal_id = p_animal_id
        ORDER BY data_pesagem ASC
        LIMIT 1
    ) p1
    CROSS JOIN (
        SELECT peso, data_pesagem
        FROM pesagens
        WHERE animal_id = p_animal_id
        ORDER BY data_pesagem DESC
        LIMIT 1
    ) p2
    WHERE p1.data_pesagem < p2.data_pesagem;
    
    RETURN v_gmd;
END;
$$ LANGUAGE plpgsql;

-- Inserir usuário admin padrão (senha: admin123)
-- Nota: Em produção, usar hash bcrypt adequado
INSERT INTO usuarios (nome, email, senha_hash, nivel_acesso)
VALUES ('Administrador', 'admin@fazenda.com', '$2b$10$YourHashHere', 'admin')
ON CONFLICT (email) DO NOTHING;

-- Comentários nas tabelas
COMMENT ON TABLE animais IS 'Tabela principal com dados dos animais do rebanho';
COMMENT ON TABLE pesagens IS 'Histórico de pesagens dos animais';
COMMENT ON TABLE sanidade IS 'Registro de vacinas, vermífugos e medicamentos';
COMMENT ON TABLE reproducao IS 'Controle reprodutivo do rebanho';
COMMENT ON TABLE movimentacoes IS 'Histórico de movimentação entre pastos e lotes';
COMMENT ON TABLE vendas IS 'Registro de vendas de animais';
COMMENT ON TABLE despesas IS 'Controle de despesas da fazenda';
COMMENT ON TABLE pastos IS 'Cadastro de pastos disponíveis';
COMMENT ON TABLE lotes IS 'Cadastro de lotes de animais';
COMMENT ON TABLE usuarios IS 'Usuários do sistema';
COMMENT ON TABLE sessoes IS 'Controle de sessões e tokens de autenticação';
