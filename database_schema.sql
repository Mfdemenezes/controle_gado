-- Schema para Sistema de Controle de Gado de Corte

-- Tabela de Animais
CREATE TABLE IF NOT EXISTS animais (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    brinco VARCHAR(50) UNIQUE NOT NULL,
    nome VARCHAR(100),
    sexo VARCHAR(1) CHECK(sexo IN ('M', 'F')),
    raca VARCHAR(100),
    data_nascimento DATE,
    peso_nascimento DECIMAL(10,2),
    peso_atual DECIMAL(10,2),
    status VARCHAR(50) CHECK(status IN ('ativo', 'vendido', 'morto', 'transferido')),
    lote VARCHAR(50),
    pasto VARCHAR(50),
    pai_id INTEGER,
    mae_id INTEGER,
    observacoes TEXT,
    data_entrada DATE NOT NULL,
    data_saida DATE,
    valor_compra DECIMAL(10,2),
    origem VARCHAR(200),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (pai_id) REFERENCES animais(id),
    FOREIGN KEY (mae_id) REFERENCES animais(id)
);

-- Tabela de Pesagens
CREATE TABLE IF NOT EXISTS pesagens (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    animal_id INTEGER NOT NULL,
    data_pesagem DATE NOT NULL,
    peso DECIMAL(10,2) NOT NULL,
    ganho_peso DECIMAL(10,2),
    gmd DECIMAL(10,3), -- Ganho Médio Diário
    condicao_corporal INTEGER CHECK(condicao_corporal BETWEEN 1 AND 5),
    observacoes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (animal_id) REFERENCES animais(id)
);

-- Tabela de Sanidade (Vacinas, Medicamentos, etc)
CREATE TABLE IF NOT EXISTS sanidade (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    animal_id INTEGER NOT NULL,
    data_aplicacao DATE NOT NULL,
    tipo VARCHAR(50) CHECK(tipo IN ('vacina', 'vermifugo', 'antibiotico', 'carrapaticida', 'outro')),
    produto VARCHAR(200) NOT NULL,
    dose VARCHAR(50),
    aplicador VARCHAR(100),
    proxima_aplicacao DATE,
    observacoes TEXT,
    custo DECIMAL(10,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (animal_id) REFERENCES animais(id)
);

-- Tabela de Reprodução
CREATE TABLE IF NOT EXISTS reproducao (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    femea_id INTEGER NOT NULL,
    macho_id INTEGER,
    tipo_cobertura VARCHAR(50) CHECK(tipo_cobertura IN ('monta natural', 'inseminacao', 'transferencia embriao')),
    data_cobertura DATE NOT NULL,
    data_diagnostico DATE,
    resultado VARCHAR(50) CHECK(resultado IN ('prenha', 'vazia', 'aguardando')),
    data_prevista_parto DATE,
    data_parto DATE,
    cria_id INTEGER,
    observacoes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (femea_id) REFERENCES animais(id),
    FOREIGN KEY (macho_id) REFERENCES animais(id),
    FOREIGN KEY (cria_id) REFERENCES animais(id)
);

-- Tabela de Movimentações (Troca de Pasto/Lote)
CREATE TABLE IF NOT EXISTS movimentacoes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    animal_id INTEGER NOT NULL,
    data_movimentacao DATE NOT NULL,
    tipo VARCHAR(50) CHECK(tipo IN ('troca_pasto', 'troca_lote', 'entrada', 'saida')),
    origem VARCHAR(100),
    destino VARCHAR(100),
    motivo TEXT,
    responsavel VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (animal_id) REFERENCES animais(id)
);

-- Tabela de Vendas
CREATE TABLE IF NOT EXISTS vendas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    animal_id INTEGER NOT NULL,
    data_venda DATE NOT NULL,
    comprador VARCHAR(200),
    peso_venda DECIMAL(10,2),
    valor_arroba DECIMAL(10,2),
    valor_total DECIMAL(10,2),
    forma_pagamento VARCHAR(50),
    observacoes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (animal_id) REFERENCES animais(id)
);

-- Tabela de Despesas
CREATE TABLE IF NOT EXISTS despesas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    data_despesa DATE NOT NULL,
    categoria VARCHAR(100) NOT NULL,
    descricao TEXT,
    valor DECIMAL(10,2) NOT NULL,
    animal_id INTEGER,
    lote VARCHAR(50),
    fornecedor VARCHAR(200),
    forma_pagamento VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (animal_id) REFERENCES animais(id)
);

-- Tabela de Pastos
CREATE TABLE IF NOT EXISTS pastos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome VARCHAR(100) UNIQUE NOT NULL,
    area_hectares DECIMAL(10,2),
    tipo_capim VARCHAR(100),
    capacidade_animais INTEGER,
    status VARCHAR(50) CHECK(status IN ('disponivel', 'ocupado', 'reforma', 'descanso')),
    data_ultimo_manejo DATE,
    observacoes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de Lotes
CREATE TABLE IF NOT EXISTS lotes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome VARCHAR(100) UNIQUE NOT NULL,
    descricao TEXT,
    data_formacao DATE,
    finalidade VARCHAR(100),
    status VARCHAR(50) CHECK(status IN ('ativo', 'encerrado')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índices para melhor performance
CREATE INDEX IF NOT EXISTS idx_animais_brinco ON animais(brinco);
CREATE INDEX IF NOT EXISTS idx_animais_status ON animais(status);
CREATE INDEX IF NOT EXISTS idx_animais_lote ON animais(lote);
CREATE INDEX IF NOT EXISTS idx_pesagens_animal ON pesagens(animal_id);
CREATE INDEX IF NOT EXISTS idx_pesagens_data ON pesagens(data_pesagem);
CREATE INDEX IF NOT EXISTS idx_sanidade_animal ON sanidade(animal_id);
CREATE INDEX IF NOT EXISTS idx_reproducao_femea ON reproducao(femea_id);
CREATE INDEX IF NOT EXISTS idx_movimentacoes_animal ON movimentacoes(animal_id);
CREATE INDEX IF NOT EXISTS idx_vendas_animal ON vendas(animal_id);

-- Views úteis para relatórios
CREATE VIEW IF NOT EXISTS vw_rebanho_ativo AS
SELECT 
    a.*,
    p.peso as ultimo_peso,
    p.data_pesagem as data_ultimo_peso,
    CAST((julianday('now') - julianday(a.data_nascimento)) / 365.25 AS INTEGER) as idade_anos
FROM animais a
LEFT JOIN (
    SELECT animal_id, peso, data_pesagem,
           ROW_NUMBER() OVER (PARTITION BY animal_id ORDER BY data_pesagem DESC) as rn
    FROM pesagens
) p ON a.id = p.animal_id AND p.rn = 1
WHERE a.status = 'ativo';

CREATE VIEW IF NOT EXISTS vw_performance_animais AS
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
    ROUND((p2.peso - p1.peso) / (julianday(p2.data_pesagem) - julianday(p1.data_pesagem)), 3) as gmd
FROM animais a
INNER JOIN (
    SELECT animal_id, peso, data_pesagem,
           ROW_NUMBER() OVER (PARTITION BY animal_id ORDER BY data_pesagem ASC) as rn
    FROM pesagens
) p1 ON a.id = p1.animal_id AND p1.rn = 1
INNER JOIN (
    SELECT animal_id, peso, data_pesagem,
           ROW_NUMBER() OVER (PARTITION BY animal_id ORDER BY data_pesagem DESC) as rn
    FROM pesagens
) p2 ON a.id = p2.animal_id AND p2.rn = 1
WHERE a.status = 'ativo';
