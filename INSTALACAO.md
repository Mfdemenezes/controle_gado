# 🚀 Guia de Instalação Rápida - Controle de Gado

## Opção 1: Docker (Recomendado - Mais Fácil)

### Pré-requisitos
- Docker e Docker Compose instalados

### Passos

1. **Clone/Baixe os arquivos**
```bash
mkdir controle-gado && cd controle-gado
# Coloque todos os arquivos nesta pasta
```

2. **Configure as variáveis de ambiente**
```bash
cp .env.example .env
nano .env  # Edite as senhas
```

3. **Inicie todos os serviços**
```bash
docker-compose up -d
```

4. **Aguarde os containers iniciarem (~30 segundos)**
```bash
docker-compose ps  # Verifique status
```

5. **Acesse o sistema**
- **App Web:** http://localhost
- **API Docs:** http://localhost/docs
- **N8N:** http://localhost:5678
- **PgAdmin:** http://localhost:5050

6. **Crie o primeiro usuário**
```bash
# Gere o hash da senha
docker exec -it gado_api python3 -c "import hashlib; print(hashlib.sha256('admin123'.encode()).hexdigest())"

# Copie o hash e execute:
docker exec -it gado_postgres psql -U postgres -d controle_gado -c \
"INSERT INTO usuarios (nome, email, senha_hash, nivel_acesso) VALUES ('Admin', 'admin@fazenda.com', 'COLE_O_HASH_AQUI', 'admin');"
```

7. **Faça login**
- Email: `admin@fazenda.com`
- Senha: `admin123`

### Comandos Úteis

```bash
# Ver logs
docker-compose logs -f api

# Parar tudo
docker-compose down

# Backup do banco
docker exec gado_postgres pg_dump -U postgres controle_gado > backup.sql

# Restaurar backup
docker exec -i gado_postgres psql -U postgres controle_gado < backup.sql
```

---

## Opção 2: Instalação Manual (Servidor Linux)

### 1. Instale PostgreSQL

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install postgresql postgresql-contrib

# Inicie o serviço
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

### 2. Configure o Banco

```bash
# Acesse como postgres
sudo -u postgres psql

# Execute no psql:
CREATE DATABASE controle_gado;
CREATE USER gado_user WITH PASSWORD 'senha_forte_aqui';
GRANT ALL PRIVILEGES ON DATABASE controle_gado TO gado_user;
\q

# Execute o schema
sudo -u postgres psql -d controle_gado -f postgres_schema.sql
```

### 3. Instale Python e dependências

```bash
# Instale Python 3.9+
sudo apt install python3 python3-pip python3-venv

# Crie ambiente virtual
python3 -m venv venv
source venv/bin/activate

# Instale dependências
pip install -r requirements.txt
```

### 4. Configure o .env

```bash
cp .env.example .env
nano .env

# Configure:
DB_HOST=localhost
DB_PORT=5432
DB_NAME=controle_gado
DB_USER=gado_user
DB_PASSWORD=senha_forte_aqui
```

### 5. Crie usuário admin

```bash
# Gere hash
python3 -c "import hashlib; senha='admin123'; print(hashlib.sha256(senha.encode()).hexdigest())"

# Insira no banco (substitua HASH)
sudo -u postgres psql -d controle_gado -c \
"INSERT INTO usuarios (nome, email, senha_hash, nivel_acesso) VALUES ('Admin', 'admin@fazenda.com', 'HASH_AQUI', 'admin');"
```

### 6. Inicie a API

```bash
# Modo desenvolvimento
python api_gado.py

# Ou com uvicorn
uvicorn api_gado:app --host 0.0.0.0 --port 8000

# Para produção (com gunicorn)
pip install gunicorn
gunicorn api_gado:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### 7. Configure Nginx (Opcional)

```bash
sudo apt install nginx

# Copie a config
sudo cp nginx.conf /etc/nginx/sites-available/gado
sudo ln -s /etc/nginx/sites-available/gado /etc/nginx/sites-enabled/

# Copie o HTML
sudo mkdir -p /var/www/gado
sudo cp mobile_app.html /var/www/gado/index.html

# Edite o mobile_app.html e altere a URL da API
sudo nano /var/www/gado/index.html
# Linha ~770: const API_URL = 'http://SEU_IP:8000/api';

# Reinicie nginx
sudo systemctl restart nginx
```

### 8. Configure systemd (Manter API rodando)

```bash
sudo nano /etc/systemd/system/gado-api.service
```

Cole:
```ini
[Unit]
Description=Gado API
After=network.target postgresql.service

[Service]
Type=simple
User=seu_usuario
WorkingDirectory=/caminho/para/controle-gado
Environment="PATH=/caminho/para/controle-gado/venv/bin"
ExecStart=/caminho/para/controle-gado/venv/bin/uvicorn api_gado:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# Ative o serviço
sudo systemctl daemon-reload
sudo systemctl start gado-api
sudo systemctl enable gado-api

# Verifique status
sudo systemctl status gado-api
```

---

## Opção 3: Instalação Windows

### 1. Instale PostgreSQL

- Baixe em: https://www.postgresql.org/download/windows/
- Execute o instalador
- Anote a senha do usuário postgres

### 2. Configure o Banco

```cmd
# Abra cmd/PowerShell como administrador
cd "C:\Program Files\PostgreSQL\15\bin"

# Crie o banco
psql -U postgres
CREATE DATABASE controle_gado;
\q

# Execute o schema
psql -U postgres -d controle_gado -f C:\caminho\postgres_schema.sql
```

### 3. Instale Python

- Baixe em: https://www.python.org/downloads/
- Marque "Add Python to PATH" durante instalação

### 4. Configure o projeto

```cmd
cd C:\caminho\controle-gado

# Crie ambiente virtual
python -m venv venv
venv\Scripts\activate

# Instale dependências
pip install -r requirements.txt

# Configure .env
copy .env.example .env
notepad .env
```

### 5. Crie usuário admin

```cmd
# Gere hash
python -c "import hashlib; print(hashlib.sha256('admin123'.encode()).hexdigest())"

# Anote o hash e execute:
psql -U postgres -d controle_gado
INSERT INTO usuarios (nome, email, senha_hash, nivel_acesso) 
VALUES ('Admin', 'admin@fazenda.com', 'HASH_AQUI', 'admin');
\q
```

### 6. Inicie a API

```cmd
venv\Scripts\activate
python api_gado.py

# Acesse: http://localhost:8000/docs
```

### 7. Abra o App

- Abra o arquivo `mobile_app.html` no navegador
- Login: admin@fazenda.com / admin123

---

## 📱 Configurar no Celular

### Opção A: Rede Local (Casa/Fazenda)

1. **Descubra o IP do servidor**
```bash
# Linux/Mac
ip addr show | grep inet

# Windows
ipconfig
```

2. **Libere firewall (se necessário)**
```bash
# Linux
sudo ufw allow 8000
sudo ufw allow 80

# Windows
# Vá em Firewall > Regras de Entrada > Nova Regra > Porta 8000
```

3. **No celular:**
- Conecte na mesma rede WiFi
- Acesse: `http://IP_DO_SERVIDOR`
- Exemplo: `http://192.168.1.100`
- Adicione à tela inicial

### Opção B: Internet (Acesso de Qualquer Lugar)

**Requer servidor com IP público ou serviço de túnel**

#### Com Cloudflare Tunnel (Grátis)
```bash
# Instale cloudflared
wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64
sudo mv cloudflared-linux-amd64 /usr/local/bin/cloudflared
sudo chmod +x /usr/local/bin/cloudflared

# Crie túnel
cloudflared tunnel --url http://localhost:80

# Use a URL fornecida no celular
```

#### Com ngrok (Grátis para testes)
```bash
# Instale
wget https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.tgz
tar xvzf ngrok-v3-stable-linux-amd64.tgz
sudo mv ngrok /usr/local/bin/

# Execute
ngrok http 80

# Use a URL fornecida
```

---

## ✅ Checklist Pós-Instalação

- [ ] Banco de dados criado e schema executado
- [ ] Usuário admin cadastrado
- [ ] API iniciando sem erros
- [ ] Consegue acessar /docs
- [ ] Login funcionando no app web
- [ ] Consegue cadastrar animal
- [ ] Consegue registrar pesagem
- [ ] Relatórios carregando
- [ ] Backup configurado (cron/task)

---

## 🆘 Problemas Comuns

### Erro: "Connection refused" ao acessar API
- Verifique se a API está rodando: `curl http://localhost:8000/health`
- Veja logs: `docker-compose logs api` ou verifique terminal

### Erro: "Could not connect to database"
- Verifique PostgreSQL: `sudo systemctl status postgresql`
- Teste conexão: `psql -U postgres -d controle_gado`
- Confira credenciais no .env

### App não carrega no celular
- Verifique se está na mesma rede
- Teste o IP: `ping IP_SERVIDOR`
- Confira firewall
- Edite URL da API no mobile_app.html

### Erro 401 Unauthorized
- Token expirado - faça login novamente
- Verifique se JWT_SECRET está configurado

---

## 📞 Suporte

Em caso de dúvidas:
1. Verifique logs da aplicação
2. Teste endpoints na documentação (/docs)
3. Revise configurações do .env
4. Confira portas usadas: 8000 (API), 5432 (Postgres), 80 (Web)

**Sistema funcionando?** Comece cadastrando seus primeiros animais! 🐮
