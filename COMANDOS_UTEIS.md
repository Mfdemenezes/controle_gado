# 🛠️ COMANDOS ÚTEIS - Sistema de Controle de Gado

## 📋 Índice
- [Docker](#docker)
- [PostgreSQL](#postgresql)
- [API](#api)
- [Backup e Restauração](#backup-e-restauração)
- [Manutenção](#manutenção)
- [Troubleshooting](#troubleshooting)
- [Monitoramento](#monitoramento)

---

## 🐳 Docker

### Gerenciamento Básico

```bash
# Iniciar todos os serviços
docker-compose up -d

# Ver logs em tempo real
docker-compose logs -f

# Ver logs de um serviço específico
docker-compose logs -f api
docker-compose logs -f postgres

# Parar todos os serviços
docker-compose stop

# Parar e remover containers
docker-compose down

# Parar, remover e limpar volumes
docker-compose down -v

# Reiniciar um serviço específico
docker-compose restart api

# Ver status dos containers
docker-compose ps

# Entrar no container
docker exec -it gado_api bash
docker exec -it gado_postgres bash
```

### Reconstruir Containers

```bash
# Rebuild após alterações no código
docker-compose up -d --build

# Rebuild de um serviço específico
docker-compose build api
docker-compose up -d api

# Forçar recriação de containers
docker-compose up -d --force-recreate
```

### Limpeza

```bash
# Remover containers parados
docker container prune

# Remover imagens não usadas
docker image prune

# Remover volumes não usados
docker volume prune

# Limpeza completa
docker system prune -a

# Ver uso de espaço
docker system df
```

---

## 🐘 PostgreSQL

### Acesso ao Banco

```bash
# Via Docker
docker exec -it gado_postgres psql -U postgres -d controle_gado

# Direto (se instalado localmente)
psql -U postgres -d controle_gado

# Com senha inline
PGPASSWORD=sua_senha psql -U postgres -d controle_gado
```

### Queries Úteis

```sql
-- Ver todas as tabelas
\dt

-- Ver estrutura de uma tabela
\d animais

-- Ver todas as views
\dv

-- Ver funções
\df

-- Total de animais ativos
SELECT COUNT(*) FROM animais WHERE status = 'ativo';

-- Resumo do rebanho
SELECT * FROM vw_resumo_rebanho;

-- Animais com melhor GMD
SELECT * FROM vw_performance_animais ORDER BY gmd DESC LIMIT 10;

-- Próximas aplicações
SELECT * FROM vw_aplicacoes_proximas WHERE dias_restantes <= 7;

-- Animais sem pesagem nos últimos 30 dias
SELECT a.brinco, a.nome, MAX(p.data_pesagem) as ultima_pesagem
FROM animais a
LEFT JOIN pesagens p ON a.id = p.animal_id
WHERE a.status = 'ativo'
GROUP BY a.id, a.brinco, a.nome
HAVING MAX(p.data_pesagem) < CURRENT_DATE - INTERVAL '30 days'
   OR MAX(p.data_pesagem) IS NULL;

-- Total investido em sanidade por mês
SELECT 
    DATE_TRUNC('month', data_aplicacao) as mes,
    SUM(custo) as total_gasto
FROM sanidade
WHERE custo IS NOT NULL
GROUP BY mes
ORDER BY mes DESC;
```

### Usuários

```bash
# Listar usuários
docker exec -it gado_postgres psql -U postgres -d controle_gado -c "SELECT id, nome, email, nivel_acesso, ativo FROM usuarios;"

# Criar novo usuário
docker exec -it gado_postgres psql -U postgres -d controle_gado -c "
INSERT INTO usuarios (nome, email, senha_hash, nivel_acesso) 
VALUES ('João Silva', 'joao@fazenda.com', '$(echo -n 'senha123' | sha256sum | cut -d' ' -f1)', 'operador');"

# Alterar senha de usuário
# 1. Gere o hash
echo -n 'nova_senha' | sha256sum | cut -d' ' -f1

# 2. Atualize no banco
docker exec -it gado_postgres psql -U postgres -d controle_gado -c "
UPDATE usuarios SET senha_hash = 'HASH_AQUI' WHERE email = 'usuario@email.com';"

# Desativar usuário
docker exec -it gado_postgres psql -U postgres -d controle_gado -c "
UPDATE usuarios SET ativo = FALSE WHERE email = 'usuario@email.com';"

# Listar sessões ativas
docker exec -it gado_postgres psql -U postgres -d controle_gado -c "
SELECT u.nome, u.email, s.dispositivo, s.created_at, s.expires_at 
FROM sessoes s 
JOIN usuarios u ON s.usuario_id = u.id 
WHERE s.expires_at > NOW();"
```

### Performance

```sql
-- Ver tamanho das tabelas
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- Estatísticas de queries lentas
SELECT 
    query,
    calls,
    total_time,
    mean_time,
    max_time
FROM pg_stat_statements
ORDER BY mean_time DESC
LIMIT 10;

-- Reindexar tabelas
REINDEX TABLE animais;
REINDEX DATABASE controle_gado;

-- Vacuum (limpeza)
VACUUM ANALYZE;
```

---

## 🚀 API

### Gerenciamento

```bash
# Iniciar API (desenvolvimento)
python api_gado.py

# Com uvicorn
uvicorn api_gado:app --reload --host 0.0.0.0 --port 8000

# Com gunicorn (produção)
gunicorn api_gado:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000

# Ver logs da API (Docker)
docker-compose logs -f api

# Reiniciar API
docker-compose restart api

# Ver processos Python rodando
ps aux | grep uvicorn
```

### Testes de API (curl)

```bash
# Health check
curl http://localhost:8000/health

# Login
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@fazenda.com","senha":"admin123"}'

# Listar animais (com token)
TOKEN="seu_token_aqui"
curl http://localhost:8000/api/animais \
  -H "Authorization: Bearer $TOKEN"

# Cadastrar animal
curl -X POST http://localhost:8000/api/animais \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "brinco": "A001",
    "nome": "Mimoso",
    "sexo": "M",
    "peso_atual": 450.5,
    "raca": "Nelore"
  }'

# Buscar animal por brinco
curl http://localhost:8000/api/animais/brinco/A001 \
  -H "Authorization: Bearer $TOKEN"

# Registrar pesagem
curl -X POST http://localhost:8000/api/pesagens \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "animal_id": 1,
    "peso": 480.5,
    "data_pesagem": "2024-01-15"
  }'

# Resumo do rebanho
curl http://localhost:8000/api/relatorios/resumo \
  -H "Authorization: Bearer $TOKEN"
```

---

## 💾 Backup e Restauração

### Backup Completo

```bash
# Backup do banco (Docker)
docker exec gado_postgres pg_dump -U postgres controle_gado > backup_$(date +%Y%m%d_%H%M%S).sql

# Backup compactado
docker exec gado_postgres pg_dump -U postgres controle_gado | gzip > backup_$(date +%Y%m%d_%H%M%S).sql.gz

# Backup apenas estrutura (sem dados)
docker exec gado_postgres pg_dump -U postgres --schema-only controle_gado > schema_backup.sql

# Backup apenas dados
docker exec gado_postgres pg_dump -U postgres --data-only controle_gado > data_backup.sql

# Backup de tabela específica
docker exec gado_postgres pg_dump -U postgres -t animais controle_gado > animais_backup.sql
```

### Restauração

```bash
# Restaurar backup completo
docker exec -i gado_postgres psql -U postgres -d controle_gado < backup.sql

# Restaurar backup compactado
gunzip -c backup.sql.gz | docker exec -i gado_postgres psql -U postgres -d controle_gado

# Criar novo banco e restaurar
docker exec -it gado_postgres psql -U postgres -c "CREATE DATABASE controle_gado_novo;"
docker exec -i gado_postgres psql -U postgres -d controle_gado_novo < backup.sql

# Restaurar tabela específica (cuidado: substitui dados)
docker exec -i gado_postgres psql -U postgres -d controle_gado < animais_backup.sql
```

### Backup Automático (Cron)

```bash
# Editar crontab
crontab -e

# Adicionar backup diário às 2h da manhã
0 2 * * * docker exec gado_postgres pg_dump -U postgres controle_gado | gzip > /caminho/backups/backup_$(date +\%Y\%m\%d).sql.gz

# Backup semanal completo (domingo às 3h)
0 3 * * 0 docker exec gado_postgres pg_dump -U postgres controle_gado > /caminho/backups/backup_semanal_$(date +\%Y\%m\%d).sql

# Limpeza de backups antigos (manter apenas últimos 30 dias)
0 4 * * * find /caminho/backups -name "backup_*.sql.gz" -mtime +30 -delete
```

### Exportar/Importar Dados (CSV)

```bash
# Exportar animais para CSV
docker exec -it gado_postgres psql -U postgres -d controle_gado -c "\COPY animais TO '/tmp/animais.csv' CSV HEADER;"
docker cp gado_postgres:/tmp/animais.csv ./animais_export.csv

# Importar CSV
docker cp animais_import.csv gado_postgres:/tmp/animais.csv
docker exec -it gado_postgres psql -U postgres -d controle_gado -c "\COPY animais FROM '/tmp/animais.csv' CSV HEADER;"
```

---

## 🔧 Manutenção

### Limpeza de Dados

```sql
-- Remover sessões expiradas
DELETE FROM sessoes WHERE expires_at < NOW();

-- Remover logs antigos (se houver tabela de logs)
DELETE FROM logs WHERE created_at < NOW() - INTERVAL '90 days';

-- Limpar animais inativos há mais de 1 ano
DELETE FROM animais 
WHERE status IN ('vendido', 'morto') 
AND data_saida < CURRENT_DATE - INTERVAL '1 year';
```

### Otimização

```bash
# Analisar e otimizar banco
docker exec -it gado_postgres psql -U postgres -d controle_gado -c "VACUUM ANALYZE;"

# Reindexar
docker exec -it gado_postgres psql -U postgres -d controle_gado -c "REINDEX DATABASE controle_gado;"

# Ver estatísticas de uso
docker exec -it gado_postgres psql -U postgres -d controle_gado -c "
SELECT 
    schemaname,
    tablename,
    n_live_tup as rows,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_stat_user_tables
ORDER BY n_live_tup DESC;"
```

### Atualização do Sistema

```bash
# 1. Fazer backup
docker exec gado_postgres pg_dump -U postgres controle_gado > backup_antes_atualizacao.sql

# 2. Parar sistema
docker-compose down

# 3. Atualizar código
git pull  # se usando git
# ou copiar novos arquivos

# 4. Rebuild containers
docker-compose build

# 5. Iniciar sistema
docker-compose up -d

# 6. Verificar logs
docker-compose logs -f

# 7. Testar API
curl http://localhost:8000/health
```

---

## 🔍 Troubleshooting

### API não inicia

```bash
# Ver logs detalhados
docker-compose logs api

# Verificar variáveis de ambiente
docker exec gado_api env | grep DB_

# Testar conexão com banco
docker exec gado_api python -c "
import psycopg2
try:
    conn = psycopg2.connect(
        host='postgres',
        port=5432,
        database='controle_gado',
        user='postgres',
        password='sua_senha'
    )
    print('Conexão OK!')
except Exception as e:
    print(f'Erro: {e}')
"

# Reiniciar serviço
docker-compose restart api
```

### Banco de dados não conecta

```bash
# Verificar se PostgreSQL está rodando
docker ps | grep postgres

# Ver logs do PostgreSQL
docker-compose logs postgres

# Testar conexão
docker exec -it gado_postgres psql -U postgres -c "SELECT version();"

# Verificar porta
docker port gado_postgres

# Reiniciar banco
docker-compose restart postgres
```

### Erro de permissão

```bash
# Verificar permissões do usuário
docker exec -it gado_postgres psql -U postgres -c "\du"

# Garantir permissões
docker exec -it gado_postgres psql -U postgres -c "
GRANT ALL PRIVILEGES ON DATABASE controle_gado TO postgres;
GRANT ALL ON ALL TABLES IN SCHEMA public TO postgres;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO postgres;
"
```

### Reset Completo

```bash
# ⚠️ CUIDADO: Isso apaga TUDO!

# 1. Backup primeiro!
docker exec gado_postgres pg_dump -U postgres controle_gado > backup_emergencia.sql

# 2. Parar e remover tudo
docker-compose down -v

# 3. Limpar volumes Docker
docker volume prune -f

# 4. Reiniciar do zero
docker-compose up -d

# 5. Recriar usuário admin
# (ver seção PostgreSQL > Usuários)
```

---

## 📊 Monitoramento

### Logs em Tempo Real

```bash
# Todos os serviços
docker-compose logs -f

# API apenas
docker-compose logs -f api | grep ERROR

# Últimas 100 linhas
docker-compose logs --tail=100 api

# Logs com timestamp
docker-compose logs -t api
```

### Estatísticas do Sistema

```bash
# Uso de CPU e memória
docker stats

# Uso específico de um container
docker stats gado_api

# Espaço em disco
df -h

# Espaço usado por Docker
docker system df

# Processos PostgreSQL
docker exec gado_postgres ps aux | grep postgres

# Conexões ativas no banco
docker exec -it gado_postgres psql -U postgres -d controle_gado -c "
SELECT 
    datname,
    count(*) as connections
FROM pg_stat_activity
GROUP BY datname;"
```

### Alertas Úteis

```sql
-- Animais sem pesagem há mais de 30 dias
SELECT COUNT(*) FROM (
    SELECT a.id
    FROM animais a
    LEFT JOIN LATERAL (
        SELECT data_pesagem
        FROM pesagens
        WHERE animal_id = a.id
        ORDER BY data_pesagem DESC
        LIMIT 1
    ) p ON true
    WHERE a.status = 'ativo'
    AND (p.data_pesagem IS NULL OR p.data_pesagem < CURRENT_DATE - 30)
) as sem_pesagem;

-- Aplicações atrasadas
SELECT COUNT(*) FROM sanidade
WHERE proxima_aplicacao < CURRENT_DATE
AND animal_id IN (SELECT id FROM animais WHERE status = 'ativo');

-- Animais com GMD abaixo de 0.5kg/dia
SELECT COUNT(*) FROM vw_performance_animais WHERE gmd < 0.5;
```

---

## 🎯 Comandos Rápidos do Dia a Dia

```bash
# Ver quantos animais ativos
docker exec -it gado_postgres psql -U postgres -d controle_gado -c "SELECT COUNT(*) FROM animais WHERE status='ativo';"

# Último animal cadastrado
docker exec -it gado_postgres psql -U postgres -d controle_gado -c "SELECT brinco, nome, created_at FROM animais ORDER BY created_at DESC LIMIT 1;"

# Peso médio do rebanho
docker exec -it gado_postgres psql -U postgres -d controle_gado -c "SELECT AVG(peso_atual) FROM animais WHERE status='ativo';"

# Próximas 5 aplicações
docker exec -it gado_postgres psql -U postgres -d controle_gado -c "SELECT * FROM vw_aplicacoes_proximas LIMIT 5;"

# Backup rápido
docker exec gado_postgres pg_dump -U postgres controle_gado | gzip > backup_$(date +%Y%m%d).sql.gz

# Reiniciar API
docker-compose restart api && docker-compose logs -f api
```

---

## 📱 Comandos Mobile/Web

```bash
# Ver quantos dispositivos conectados (sessões ativas)
docker exec -it gado_postgres psql -U postgres -d controle_gado -c "
SELECT 
    COUNT(DISTINCT dispositivo) as dispositivos,
    COUNT(*) as sessoes_ativas
FROM sessoes 
WHERE expires_at > NOW();"

# Limpar cache do navegador mobile
# No celular: Menu > Configurações > Limpar dados do site

# Reinstalar PWA
# No celular: Desinstalar app > Reabrir no navegador > Adicionar à tela inicial
```

---

**💡 Dica:** Salve os comandos mais usados em aliases no seu ~/.bashrc

```bash
# Adicione ao ~/.bashrc
alias gado-logs='docker-compose logs -f'
alias gado-restart='docker-compose restart'
alias gado-backup='docker exec gado_postgres pg_dump -U postgres controle_gado | gzip > backup_$(date +%Y%m%d).sql.gz'
alias gado-stats='docker stats gado_postgres gado_api'
alias gado-psql='docker exec -it gado_postgres psql -U postgres -d controle_gado'
```

---

**Comandos essenciais dominados! 🚀**
