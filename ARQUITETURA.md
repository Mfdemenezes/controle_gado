# 🏗️ ARQUITETURA DO SISTEMA - Controle de Gado

## 📐 Visão Geral da Arquitetura

```
┌─────────────────────────────────────────────────────────────────┐
│                         CAMADA DE ACESSO                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │   Celular    │  │  Computador  │  │    Tablet    │          │
│  │  (Android/   │  │   Desktop    │  │    (iOS/     │          │
│  │    iOS)      │  │  (Browser)   │  │   Android)   │          │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘          │
│         │                  │                  │                   │
│         └──────────────────┼──────────────────┘                   │
│                            │                                       │
└────────────────────────────┼───────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      CAMADA DE APRESENTAÇÃO                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌────────────────────────────────────────────────────────┐     │
│  │              PWA - Progressive Web App                  │     │
│  │              (mobile_app.html)                         │     │
│  ├────────────────────────────────────────────────────────┤     │
│  │  • Interface Responsiva                                │     │
│  │  • Instalável como App Nativo                         │     │
│  │  • Service Worker (Offline)                           │     │
│  │  • Local Storage (Cache)                              │     │
│  └────────────────────────────────────────────────────────┘     │
│                                                                   │
└────────────────────────────┬─────────────────────────────────────┘
                             │
                             │ HTTPS/REST
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      CAMADA DE SERVIDOR WEB                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌────────────────────────────────────────────────────────┐     │
│  │                   NGINX (Proxy Reverso)                │     │
│  ├────────────────────────────────────────────────────────┤     │
│  │  • Servir arquivos estáticos (HTML/CSS/JS)            │     │
│  │  • Proxy para API (/api/*)                            │     │
│  │  • SSL/TLS Termination                                │     │
│  │  • Load Balancing (se necessário)                     │     │
│  │  • Compressão GZIP                                    │     │
│  │  • Cache de estáticos                                 │     │
│  └───────────────────┬────────────────────────────────────┘     │
│                      │                                            │
└──────────────────────┼────────────────────────────────────────────┘
                       │
                       │
                       ▼
┌─────────────────────────────────────────────────────────────────┐
│                     CAMADA DE APLICAÇÃO (API)                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌────────────────────────────────────────────────────────┐     │
│  │              FastAPI (Python 3.9+)                     │     │
│  │              (api_gado.py)                             │     │
│  ├────────────────────────────────────────────────────────┤     │
│  │                                                         │     │
│  │  ┌──────────────────────────────────────────────┐     │     │
│  │  │         MÓDULOS DA API                        │     │     │
│  │  ├──────────────────────────────────────────────┤     │     │
│  │  │  • Autenticação JWT                          │     │     │
│  │  │  • Gestão de Animais                         │     │     │
│  │  │  • Controle de Pesagens                      │     │     │
│  │  │  • Gestão de Sanidade                        │     │     │
│  │  │  • Controle Reprodutivo                      │     │     │
│  │  │  • Movimentações                             │     │     │
│  │  │  • Vendas e Despesas                         │     │     │
│  │  │  • Relatórios e Analytics                    │     │     │
│  │  └──────────────────────────────────────────────┘     │     │
│  │                                                         │     │
│  │  ┌──────────────────────────────────────────────┐     │     │
│  │  │         MIDDLEWARES                           │     │     │
│  │  ├──────────────────────────────────────────────┤     │     │
│  │  │  • CORS (Cross-Origin)                       │     │     │
│  │  │  • Rate Limiting                             │     │     │
│  │  │  • Logging                                   │     │     │
│  │  │  • Error Handling                            │     │     │
│  │  └──────────────────────────────────────────────┘     │     │
│  │                                                         │     │
│  └────────────────────┬────────────────────────────────────┘     │
│                       │                                           │
└───────────────────────┼───────────────────────────────────────────┘
                        │
                        │ psycopg2
                        │
                        ▼
┌─────────────────────────────────────────────────────────────────┐
│                     CAMADA DE PERSISTÊNCIA                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌────────────────────────────────────────────────────────┐     │
│  │              PostgreSQL 15                             │     │
│  ├────────────────────────────────────────────────────────┤     │
│  │                                                         │     │
│  │  ┌──────────────────────────────────────────────┐     │     │
│  │  │  TABELAS PRINCIPAIS                          │     │     │
│  │  ├──────────────────────────────────────────────┤     │     │
│  │  │  • animais         (dados cadastrais)       │     │     │
│  │  │  • pesagens        (histórico de peso)      │     │     │
│  │  │  • sanidade        (vacinas/medicamentos)   │     │     │
│  │  │  • reproducao      (controle reprodutivo)   │     │     │
│  │  │  • movimentacoes   (pastos/lotes)          │     │     │
│  │  │  • vendas          (comercialização)        │     │     │
│  │  │  • despesas        (custos)                 │     │     │
│  │  │  • pastos          (infraestrutura)         │     │     │
│  │  │  • lotes           (agrupamentos)           │     │     │
│  │  │  • usuarios        (acesso ao sistema)      │     │     │
│  │  │  • sessoes         (autenticação)           │     │     │
│  │  └──────────────────────────────────────────────┘     │     │
│  │                                                         │     │
│  │  ┌──────────────────────────────────────────────┐     │     │
│  │  │  VIEWS E FUNÇÕES                             │     │     │
│  │  ├──────────────────────────────────────────────┤     │     │
│  │  │  • vw_rebanho_ativo                         │     │     │
│  │  │  • vw_performance_animais (GMD)             │     │     │
│  │  │  • vw_resumo_rebanho                        │     │     │
│  │  │  • vw_aplicacoes_proximas                   │     │     │
│  │  │  • calcular_gmd() (função)                  │     │     │
│  │  └──────────────────────────────────────────────┘     │     │
│  │                                                         │     │
│  └─────────────────────────────────────────────────────────┘     │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘


┌─────────────────────────────────────────────────────────────────┐
│                     CAMADA DE AUTOMAÇÃO                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌────────────────────────────────────────────────────────┐     │
│  │                      N8N Workflows                     │     │
│  ├────────────────────────────────────────────────────────┤     │
│  │                                                         │     │
│  │  ┌──────────────────────────────────────────────┐     │     │
│  │  │  Workflow 1: Relatório Diário                │     │     │
│  │  ├──────────────────────────────────────────────┤     │     │
│  │  │  Trigger: Cron (8h da manhã)                │     │     │
│  │  │  ↓                                           │     │     │
│  │  │  Query: Buscar dados do rebanho             │     │     │
│  │  │  ↓                                           │     │     │
│  │  │  Query: Próximas aplicações                 │     │     │
│  │  │  ↓                                           │     │     │
│  │  │  Function: Formatar mensagem                │     │     │
│  │  │  ↓                                           │     │     │
│  │  │  Enviar: Email + WhatsApp                   │     │     │
│  │  └──────────────────────────────────────────────┘     │     │
│  │                                                         │     │
│  │  ┌──────────────────────────────────────────────┐     │     │
│  │  │  Workflow 2: Alertas de Sanidade             │     │     │
│  │  ├──────────────────────────────────────────────┤     │     │
│  │  │  Trigger: Cron (diário)                     │     │     │
│  │  │  ↓                                           │     │     │
│  │  │  Query: Aplicações vencidas/próximas        │     │     │
│  │  │  ↓                                           │     │     │
│  │  │  IF: Tem alertas?                           │     │     │
│  │  │  ↓                                           │     │     │
│  │  │  Enviar: Notificação urgente                │     │     │
│  │  └──────────────────────────────────────────────┘     │     │
│  │                                                         │     │
│  │  ┌──────────────────────────────────────────────┐     │     │
│  │  │  Workflow 3: Backup Automático               │     │     │
│  │  ├──────────────────────────────────────────────┤     │     │
│  │  │  Trigger: Cron (semanal - domingo 2h)       │     │     │
│  │  │  ↓                                           │     │     │
│  │  │  Exec: pg_dump backup.sql                   │     │     │
│  │  │  ↓                                           │     │     │
│  │  │  Upload: Google Drive / S3                  │     │     │
│  │  │  ↓                                           │     │     │
│  │  │  Enviar: Confirmação por email              │     │     │
│  │  └──────────────────────────────────────────────┘     │     │
│  │                                                         │     │
│  └─────────────────────────────────────────────────────────┘     │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

## 🔄 Fluxo de Dados

### 1. Cadastro de Animal

```
Usuário (Mobile)
  ↓ [Preenche formulário]
  ↓ [POST /api/animais]
FastAPI
  ↓ [Valida JWT]
  ↓ [Valida dados]
  ↓ [INSERT INTO animais]
PostgreSQL
  ↓ [Retorna ID]
  ↓ [INSERT INTO pesagens (peso inicial)]
  ↓ [Commit transaction]
FastAPI
  ↓ [Retorna sucesso]
Mobile
  ↓ [Exibe confirmação]
```

### 2. Registro de Pesagem

```
Usuário (Mobile)
  ↓ [Busca animal por brinco]
  ↓ [GET /api/animais/brinco/{brinco}]
FastAPI
  ↓ [SELECT FROM animais]
PostgreSQL
  ↓ [Retorna dados]
Mobile
  ↓ [Exibe dados do animal]
  ↓ [Usuário insere novo peso]
  ↓ [POST /api/pesagens]
FastAPI
  ↓ [INSERT INTO pesagens]
  ↓ [UPDATE animais SET peso_atual]
  ↓ [Calcula GMD]
PostgreSQL
  ↓ [Retorna sucesso + GMD]
Mobile
  ↓ [Exibe confirmação + GMD]
```

### 3. Relatório Automático

```
N8N (Cron: 8h)
  ↓ [Trigger: Schedule]
  ↓ [Query: vw_resumo_rebanho]
PostgreSQL
  ↓ [Retorna estatísticas]
  ↓ [Query: vw_aplicacoes_proximas]
  ↓ [Retorna próximas aplicações]
N8N
  ↓ [Function: Formatar mensagem]
  ↓ [Enviar Email]
SMTP
  ↓ [Email enviado]
  ↓ [Enviar WhatsApp]
WhatsApp API
  ↓ [Mensagem enviada]
```

## 🔐 Fluxo de Autenticação

```
1. Login
   Mobile → POST /api/auth/login
   API → Verifica credenciais no PostgreSQL
   API → Gera JWT token
   API → Salva sessão na tabela 'sessoes'
   API → Retorna token + dados do usuário
   Mobile → Armazena token no LocalStorage

2. Requisições Autenticadas
   Mobile → GET /api/animais
   Headers: Authorization: Bearer {token}
   API → Verifica token na tabela 'sessoes'
   API → Valida expiração
   API → Executa query
   API → Retorna dados

3. Logout
   Mobile → POST /api/auth/logout
   API → Remove sessão do banco
   Mobile → Remove token do LocalStorage
```

## 📦 Deployment com Docker

```
docker-compose up
  ↓
  ├─→ [Container: postgres]
  │   ├─ Inicializa banco
  │   ├─ Executa schema SQL
  │   └─ Aguarda conexões (porta 5432)
  │
  ├─→ [Container: api]
  │   ├─ Aguarda postgres estar healthy
  │   ├─ Instala dependências Python
  │   ├─ Inicia FastAPI/Uvicorn
  │   └─ Escuta na porta 8000
  │
  ├─→ [Container: nginx]
  │   ├─ Aguarda api estar rodando
  │   ├─ Serve arquivos estáticos (port 80)
  │   └─ Proxy reverso para API
  │
  └─→ [Container: n8n]
      ├─ Aguarda postgres estar healthy
      ├─ Conecta ao banco
      ├─ Importa workflows
      └─ Escuta na porta 5678

Sistema completo rodando! ✅
```

## 🌐 Topologia de Rede

```
Internet
  │
  ↓
┌──────────────────────────────┐
│      Firewall/Router         │
│  Porta 80 (HTTP)             │
│  Porta 443 (HTTPS)           │
└──────────────────────────────┘
  │
  ↓
┌──────────────────────────────┐
│         Nginx                │
│  :80 → Frontend (HTML)       │
│  :80/api → Proxy → API       │
└──────────────────────────────┘
  │
  ├─→ [FastAPI :8000]
  │     │
  │     └─→ [PostgreSQL :5432]
  │
  └─→ [N8N :5678]
        │
        └─→ [PostgreSQL :5432]
```

## 📊 Estrutura de Dados (Diagrama ER Simplificado)

```
usuarios ───┐
            │
            ├─→ sessoes (1:N)
            │
            └─→ [usa sistema]


animais ─────┬─→ pesagens (1:N)
  │          │
  │          ├─→ sanidade (1:N)
  │          │
  │          ├─→ movimentacoes (1:N)
  │          │
  │          ├─→ vendas (1:1)
  │          │
  │          └─→ reproducao (1:N)
  │
  ├─→ pai_id (FK → animais)
  │
  └─→ mae_id (FK → animais)


lotes ───→ animais.lote (1:N)

pastos ──→ animais.pasto (1:N)

despesas → animal_id (N:1)
```

## 🛡️ Camadas de Segurança

```
1. Rede
   ├─ Firewall (portas específicas)
   ├─ SSL/TLS (HTTPS)
   └─ Rate Limiting

2. Aplicação
   ├─ JWT Authentication
   ├─ Password Hashing (SHA256)
   ├─ Input Validation (Pydantic)
   ├─ SQL Injection Protection (Parametrized Queries)
   └─ CORS Configuration

3. Banco de Dados
   ├─ User Permissions
   ├─ Connection Pooling
   └─ Encrypted Connections

4. Infraestrutura
   ├─ Container Isolation (Docker)
   ├─ Environment Variables (.env)
   ├─ Backup Automático
   └─ Logs Centralizados
```

## 📈 Escalabilidade

### Vertical (Mesma Máquina)
```
1 usuário  → 1 container  → 1GB RAM
10 usuários → 1 container  → 2GB RAM
50 usuários → 1 container  → 4GB RAM
```

### Horizontal (Múltiplas Máquinas)
```
Load Balancer
  │
  ├─→ API Instance 1
  ├─→ API Instance 2
  └─→ API Instance 3
       │
       └─→ PostgreSQL (Master/Replica)
```

## 🔄 Ciclo de Vida dos Dados

```
1. ENTRADA
   Usuário → Interface → API → Banco

2. PROCESSAMENTO
   Banco → Views → Cálculos (GMD, médias)

3. ANÁLISE
   Banco → API → Relatórios → Usuário

4. AUTOMAÇÃO
   Banco → N8N → Notificações → Usuário

5. BACKUP
   Banco → pg_dump → Storage → Segurança
```

---

**Arquitetura Moderna, Escalável e Segura** 🏗️
