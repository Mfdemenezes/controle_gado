# 🐮 Sistema de Controle de Gado de Corte

Sistema completo para gestão de rebanho bovino com banco PostgreSQL, API REST, interface web mobile e automações via N8N.

## 📋 Índice

- [Características](#características)
- [Tecnologias](#tecnologias)
- [Instalação](#instalação)
- [Configuração](#configuração)
- [Uso](#uso)
- [API](#api)
- [N8N Workflows](#n8n-workflows)
- [Mobile/Web App](#mobileweb-app)

## ✨ Características

### Gestão Completa do Rebanho
- ✅ Cadastro completo de animais
- ✅ Controle de pesagens com GMD (Ganho Médio Diário)
- ✅ Gestão de sanidade (vacinas, vermífugos, medicamentos)
- ✅ Controle reprodutivo
- ✅ Movimentação entre pastos e lotes
- ✅ Registro de vendas e despesas
- ✅ Relatórios gerenciais

### Tecnologia
- 🗄️ **PostgreSQL** - Banco de dados robusto
- 🚀 **FastAPI** - API REST moderna e rápida
- 📱 **PWA** - Interface web que funciona como app no celular
- 🤖 **N8N** - Automações e relatórios automatizados
- 📊 **Dashboards** - Visualização de dados em tempo real

## 🛠️ Tecnologias

- **Backend:** Python 3.9+, FastAPI
- **Banco de Dados:** PostgreSQL 13+
- **Frontend:** HTML5, CSS3, JavaScript (Vanilla)
- **Automação:** N8N
- **Autenticação:** JWT (JSON Web Tokens)

## 📦 Instalação

### 1. Pré-requisitos

```bash
# PostgreSQL
sudo apt-get install postgresql postgresql-contrib

# Python 3.9+
sudo apt-get install python3 python3-pip python3-venv

# N8N (opcional, para automações)
npm install -g n8n
```

### 2. Clone ou baixe os arquivos do sistema

```bash
mkdir controle-gado
cd controle-gado

# Copie todos os arquivos fornecidos para esta pasta
```

### 3. Configure o PostgreSQL

```bash
# Acesse o PostgreSQL
sudo -u postgres psql

# Crie o banco de dados
CREATE DATABASE controle_gado;

# Crie um usuário (opcional)
CREATE USER gado_user WITH PASSWORD 'sua_senha_forte';
GRANT ALL PRIVILEGES ON DATABASE controle_gado TO gado_user;

# Saia do PostgreSQL
\q

# Execute o schema
psql -U postgres -d controle_gado -f postgres_schema.sql
```

### 4. Configure o Python

```bash
# Crie um ambiente virtual
python3 -m venv venv

# Ative o ambiente virtual
source venv/bin/activate  # Linux/Mac
# OU
venv\Scripts\activate  # Windows

# Instale as dependências
pip install -r requirements.txt
```

### 5. Configure as variáveis de ambiente

```bash
# Copie o arquivo de exemplo
cp .env.example .env

# Edite o arquivo .env com suas configurações
nano .env
```

Edite os valores no arquivo `.env`:

```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=controle_gado
DB_USER=postgres
DB_PASSWORD=sua_senha_postgresql

API_SECRET_KEY=gere_uma_chave_aleatoria_aqui
```

### 6. Crie um usuário admin

```bash
# Acesse o PostgreSQL
psql -U postgres -d controle_gado

# Gere o hash da senha (use Python)
python3 -c "import hashlib; print(hashlib.sha256('sua_senha'.encode()).hexdigest())"

# Insira o usuário (substitua HASH_GERADO pelo hash acima)
INSERT INTO usuarios (nome, email, senha_hash, nivel_acesso)
VALUES ('Administrador', 'admin@fazenda.com', 'HASH_GERADO', 'admin');
```

## 🚀 Uso

### Iniciar a API

```bash
# Ative o ambiente virtual
source venv/bin/activate

# Inicie a API
python api_gado.py

# Ou com uvicorn diretamente
uvicorn api_gado:app --reload --host 0.0.0.0 --port 8000
```

A API estará disponível em: `http://localhost:8000`

Documentação automática: `http://localhost:8000/docs`

### Acessar a Interface Web/Mobile

1. **Desenvolvimento:**
   - Abra o arquivo `mobile_app.html` em um navegador
   - Ou sirva via servidor HTTP:

```bash
# Python
python3 -m http.server 8080

# Acesse: http://localhost:8080/mobile_app.html
```

2. **Produção:**
   - Hospede os arquivos HTML em um servidor web (Nginx, Apache)
   - Configure HTTPS para funcionalidades PWA completas
   - Atualize a URL da API no arquivo `mobile_app.html` (variável `API_URL`)

### Adicionar à Tela Inicial (Mobile)

**Android (Chrome):**
1. Acesse o site pelo Chrome
2. Toque no menu (⋮)
3. Selecione "Adicionar à tela inicial"
4. Confirme

**iOS (Safari):**
1. Acesse o site pelo Safari
2. Toque no botão compartilhar
3. Selecione "Adicionar à Tela de Início"
4. Confirme

## 📡 API

### Autenticação

```bash
# Login
POST /api/auth/login
Body: {"email": "admin@fazenda.com", "senha": "sua_senha"}

# Resposta
{
  "token": "token_jwt_aqui",
  "usuario": {...},
  "expires_at": "2024-12-31T23:59:59"
}

# Use o token em todas as requisições
Authorization: Bearer {token}
```

### Principais Endpoints

#### Animais

```bash
# Listar animais
GET /api/animais?status=ativo&lote=L1&limit=100

# Buscar por ID
GET /api/animais/123

# Buscar por brinco
GET /api/animais/brinco/A001

# Cadastrar animal
POST /api/animais
Body: {
  "brinco": "A001",
  "nome": "Mimoso",
  "sexo": "M",
  "peso_atual": 450.5,
  "raca": "Nelore",
  ...
}

# Atualizar animal
PUT /api/animais/123
Body: {"peso_atual": 480.0, "lote": "L2"}
```

#### Pesagens

```bash
# Listar pesagens de um animal
GET /api/pesagens/123

# Registrar pesagem
POST /api/pesagens
Body: {
  "animal_id": 123,
  "peso": 480.5,
  "data_pesagem": "2024-01-15",
  "condicao_corporal": 4
}
```

#### Sanidade

```bash
# Registrar aplicação
POST /api/sanidade
Body: {
  "animal_id": 123,
  "tipo": "vacina",
  "produto": "Vacina Aftosa",
  "proxima_aplicacao": "2024-07-15"
}

# Próximas aplicações
GET /api/sanidade/proximas?dias=30
```

#### Relatórios

```bash
# Resumo do rebanho
GET /api/relatorios/resumo

# Performance (GMD)
GET /api/relatorios/performance?limit=50
```

### Documentação Completa

Acesse `http://localhost:8000/docs` para ver todos os endpoints com exemplos interativos (Swagger UI).

## 🤖 N8N Workflows

### Instalação do N8N

```bash
# Instalar globalmente
npm install -g n8n

# Ou com Docker
docker run -it --rm \
  --name n8n \
  -p 5678:5678 \
  -v ~/.n8n:/home/node/.n8n \
  n8nio/n8n
```

### Configurar Workflow

1. Acesse o N8N: `http://localhost:5678`
2. Importe o workflow: `n8n_workflow_relatorio_diario.json`
3. Configure as credenciais:
   - **PostgreSQL:** Configure conexão com o banco
   - **Email/WhatsApp:** Configure conforme necessário
4. Ative o workflow

### Workflows Disponíveis

#### 1. Relatório Diário
- **Frequência:** Diariamente às 8h
- **Função:** Envia resumo do rebanho e próximas aplicações
- **Canais:** Email, WhatsApp

#### 2. Alertas de Sanidade
- **Frequência:** Diariamente
- **Função:** Notifica aplicações vencidas ou próximas
- **Ação:** Envia lista de animais que precisam de atenção

#### 3. Backup Automático
- **Frequência:** Semanalmente
- **Função:** Faz backup do banco de dados
- **Ação:** Salva backup e envia por email

### Criar Novos Workflows

O N8N permite criar automações personalizadas:

```
Trigger (Schedule/Webhook)
  ↓
PostgreSQL (Query)
  ↓
Function (Processar dados)
  ↓
Email/WhatsApp/Telegram (Notificar)
```

Exemplos de automações úteis:
- Alertas de animais com baixo GMD
- Relatório semanal de vendas
- Notificação de animais próximos ao peso de abate
- Integração com planilhas Google Sheets
- Sincronização com outros sistemas

## 📱 Mobile/Web App

### Funcionalidades

#### Tela Inicial (Dashboard)
- Total de animais, machos e fêmeas
- Peso médio do rebanho
- Próximas aplicações de sanidade

#### Rebanho
- Lista completa de animais
- Busca por brinco ou nome
- Visualização de detalhes

#### Cadastro
- Formulário completo para novos animais
- Validação de dados
- Campos obrigatórios e opcionais

#### Pesagem
- Busca rápida de animal por brinco
- Registro de peso e condição corporal
- Atualização automática do peso atual

### Personalização

O arquivo `mobile_app.html` pode ser customizado:

```javascript
// Alterar URL da API (linha ~770)
const API_URL = 'https://sua-api.com/api';

// Alterar cores (no CSS, linhas ~20-30)
:root {
    --primary-color: #2c5530;  // Cor principal
    --secondary-color: #5a8f3d;  // Cor secundária
}
```

## 🔒 Segurança

### Recomendações

1. **Senhas Fortes:** Use senhas complexas para banco e usuários
2. **HTTPS:** Configure SSL/TLS em produção
3. **Firewall:** Proteja as portas do banco e API
4. **Backups:** Configure backups automáticos regulares
5. **Atualizações:** Mantenha dependências atualizadas

### Trocar Senha de Usuário

```sql
-- Gere o hash da nova senha
-- Python: hashlib.sha256('nova_senha'.encode()).hexdigest()

UPDATE usuarios 
SET senha_hash = 'NOVO_HASH_AQUI'
WHERE email = 'usuario@email.com';
```

## 🐛 Troubleshooting

### Erro de Conexão com PostgreSQL

```bash
# Verifique se o PostgreSQL está rodando
sudo systemctl status postgresql

# Inicie se necessário
sudo systemctl start postgresql

# Verifique as configurações em /etc/postgresql/.../postgresql.conf
listen_addresses = 'localhost'
port = 5432
```

### Erro de CORS na API

Se tiver problemas de CORS ao acessar de diferentes origens:

```python
# Em api_gado.py, ajuste o CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://seu-dominio.com"],  # Especifique os domínios
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### App não funciona offline (PWA)

1. Configure um Service Worker adequado
2. Hospede em HTTPS
3. Adicione o arquivo `manifest.json`

## 📊 Estrutura do Banco de Dados

### Tabelas Principais

- **animais** - Dados cadastrais dos animais
- **pesagens** - Histórico de pesagens
- **sanidade** - Vacinas e medicamentos
- **reproducao** - Controle reprodutivo
- **movimentacoes** - Troca de pastos/lotes
- **vendas** - Registro de vendas
- **despesas** - Controle financeiro
- **pastos** - Cadastro de pastos
- **lotes** - Cadastro de lotes
- **usuarios** - Usuários do sistema

### Views Úteis

- **vw_rebanho_ativo** - Animais ativos com última pesagem
- **vw_performance_animais** - Cálculo de GMD
- **vw_resumo_rebanho** - Estatísticas gerais
- **vw_aplicacoes_proximas** - Sanidade programada

## 📝 Licença

Este sistema foi desenvolvido para uso em propriedades rurais. Sinta-se livre para adaptar conforme sua necessidade.

## 🤝 Suporte

Para dúvidas ou problemas:
1. Verifique a documentação da API em `/docs`
2. Consulte os logs da aplicação
3. Revise as configurações do `.env`

## 🚀 Próximos Passos

Sugestões de melhorias:
- [ ] Integração com balanças eletrônicas
- [ ] Leitura de brincos RFID
- [ ] Geração de gráficos e relatórios PDF
- [ ] Sincronização offline (PWA completo)
- [ ] Gestão de múltiplas fazendas
- [ ] Módulo financeiro avançado
- [ ] Integração com ERP/contabilidade

---

**Desenvolvido para otimizar a gestão de rebanhos bovinos** 🐮
