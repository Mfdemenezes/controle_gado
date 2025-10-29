#!/bin/bash

# Script de Instalação Automática - Sistema de Controle de Gado
# Uso: chmod +x setup.sh && ./setup.sh

set -e  # Para em caso de erro

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # Sem cor

# Banner
echo -e "${GREEN}"
echo "╔═══════════════════════════════════════════════════════════╗"
echo "║                                                           ║"
echo "║           SISTEMA DE CONTROLE DE GADO                    ║"
echo "║           Instalação Automática                          ║"
echo "║                                                           ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Funções auxiliares
print_step() {
    echo -e "\n${BLUE}➜ $1${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

# Verificar se é root
if [ "$EUID" -eq 0 ]; then 
    print_warning "Não execute este script como root (sudo)"
    echo "Execute: ./setup.sh"
    exit 1
fi

# Menu de escolha
echo -e "\n${YELLOW}Escolha o método de instalação:${NC}"
echo "1) Docker (Recomendado - Mais fácil)"
echo "2) Manual (Servidor Linux)"
echo "3) Apenas configurar PostgreSQL existente"
echo "4) Sair"
echo ""
read -p "Opção [1-4]: " INSTALL_METHOD

case $INSTALL_METHOD in
    1)
        INSTALL_TYPE="docker"
        ;;
    2)
        INSTALL_TYPE="manual"
        ;;
    3)
        INSTALL_TYPE="config"
        ;;
    4)
        echo "Saindo..."
        exit 0
        ;;
    *)
        print_error "Opção inválida"
        exit 1
        ;;
esac

# ==================== INSTALAÇÃO DOCKER ====================
if [ "$INSTALL_TYPE" = "docker" ]; then
    print_step "Instalação via Docker"
    
    # Verificar Docker
    if ! command -v docker &> /dev/null; then
        print_warning "Docker não encontrado. Instalando..."
        
        # Instalar Docker
        curl -fsSL https://get.docker.com -o get-docker.sh
        sudo sh get-docker.sh
        sudo usermod -aG docker $USER
        rm get-docker.sh
        
        print_success "Docker instalado"
        print_warning "IMPORTANTE: Execute 'newgrp docker' ou faça logout/login para aplicar permissões"
    else
        print_success "Docker já instalado"
    fi
    
    # Verificar Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        print_warning "Docker Compose não encontrado. Instalando..."
        
        sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
        sudo chmod +x /usr/local/bin/docker-compose
        
        print_success "Docker Compose instalado"
    else
        print_success "Docker Compose já instalado"
    fi
    
    # Configurar .env
    print_step "Configurando variáveis de ambiente"
    
    if [ ! -f .env ]; then
        cp .env.example .env
        
        # Gerar senha aleatória
        DB_PASSWORD=$(openssl rand -base64 16)
        API_SECRET=$(openssl rand -hex 32)
        
        # Atualizar .env
        sed -i "s/DB_PASSWORD=.*/DB_PASSWORD=$DB_PASSWORD/" .env
        sed -i "s/API_SECRET_KEY=.*/API_SECRET_KEY=$API_SECRET/" .env
        
        print_success "Arquivo .env criado com senhas aleatórias"
        print_warning "Senhas salvas em: .env (NÃO compartilhe este arquivo)"
    else
        print_success "Arquivo .env já existe"
    fi
    
    # Iniciar containers
    print_step "Iniciando containers Docker..."
    
    docker-compose up -d
    
    print_success "Containers iniciados"
    
    # Aguardar PostgreSQL ficar pronto
    print_step "Aguardando PostgreSQL inicializar..."
    sleep 10
    
    # Criar usuário admin
    print_step "Criando usuário administrador"
    
    echo ""
    read -p "Email do admin [admin@fazenda.com]: " ADMIN_EMAIL
    ADMIN_EMAIL=${ADMIN_EMAIL:-admin@fazenda.com}
    
    read -sp "Senha do admin: " ADMIN_PASSWORD
    echo ""
    
    if [ -z "$ADMIN_PASSWORD" ]; then
        ADMIN_PASSWORD="admin123"
        print_warning "Usando senha padrão: admin123 (ALTERE DEPOIS!)"
    fi
    
    # Gerar hash da senha
    PASSWORD_HASH=$(echo -n "$ADMIN_PASSWORD" | sha256sum | cut -d' ' -f1)
    
    # Inserir usuário
    docker exec -i gado_postgres psql -U postgres -d controle_gado <<EOF
INSERT INTO usuarios (nome, email, senha_hash, nivel_acesso)
VALUES ('Administrador', '$ADMIN_EMAIL', '$PASSWORD_HASH', 'admin')
ON CONFLICT (email) DO NOTHING;
EOF
    
    print_success "Usuário admin criado"
    
    # Mostrar informações
    echo ""
    echo -e "${GREEN}╔═══════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║           INSTALAÇÃO CONCLUÍDA COM SUCESSO!              ║${NC}"
    echo -e "${GREEN}╚═══════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${YELLOW}Acesse o sistema:${NC}"
    echo "  • Interface Web: http://localhost"
    echo "  • API Docs: http://localhost/docs"
    echo "  • N8N: http://localhost:5678"
    echo "  • PgAdmin: http://localhost:5050"
    echo ""
    echo -e "${YELLOW}Login:${NC}"
    echo "  • Email: $ADMIN_EMAIL"
    echo "  • Senha: $ADMIN_PASSWORD"
    echo ""
    echo -e "${YELLOW}IP local (para celular na mesma rede):${NC}"
    ip addr show | grep -oP '(?<=inet\s)\d+(\.\d+){3}' | grep -v '127.0.0.1'
    echo ""
    echo -e "${YELLOW}Comandos úteis:${NC}"
    echo "  • Ver logs: docker-compose logs -f"
    echo "  • Parar: docker-compose stop"
    echo "  • Reiniciar: docker-compose restart"
    echo "  • Backup: docker exec gado_postgres pg_dump -U postgres controle_gado > backup.sql"
    echo ""

# ==================== INSTALAÇÃO MANUAL ====================
elif [ "$INSTALL_TYPE" = "manual" ]; then
    print_step "Instalação Manual"
    
    # Detectar sistema
    if [ -f /etc/debian_version ]; then
        OS="debian"
        print_success "Sistema: Debian/Ubuntu"
    elif [ -f /etc/redhat-release ]; then
        OS="redhat"
        print_success "Sistema: RedHat/CentOS"
    else
        print_error "Sistema operacional não suportado"
        exit 1
    fi
    
    # Instalar PostgreSQL
    print_step "Instalando PostgreSQL..."
    
    if [ "$OS" = "debian" ]; then
        sudo apt update
        sudo apt install -y postgresql postgresql-contrib python3 python3-pip python3-venv nginx
    else
        sudo yum install -y postgresql postgresql-server python3 python3-pip nginx
        sudo postgresql-setup initdb
    fi
    
    sudo systemctl start postgresql
    sudo systemctl enable postgresql
    
    print_success "PostgreSQL instalado"
    
    # Criar banco de dados
    print_step "Configurando banco de dados"
    
    read -p "Nome do banco [controle_gado]: " DB_NAME
    DB_NAME=${DB_NAME:-controle_gado}
    
    read -p "Usuário do banco [gado_user]: " DB_USER
    DB_USER=${DB_USER:-gado_user}
    
    read -sp "Senha do banco: " DB_PASSWORD
    echo ""
    
    if [ -z "$DB_PASSWORD" ]; then
        DB_PASSWORD=$(openssl rand -base64 16)
        print_warning "Senha gerada automaticamente: $DB_PASSWORD"
    fi
    
    sudo -u postgres psql <<EOF
CREATE DATABASE $DB_NAME;
CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';
GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;
\q
EOF
    
    # Executar schema
    sudo -u postgres psql -d $DB_NAME -f postgres_schema.sql
    
    print_success "Banco de dados configurado"
    
    # Configurar Python
    print_step "Configurando ambiente Python"
    
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    
    print_success "Ambiente Python configurado"
    
    # Criar .env
    print_step "Criando arquivo de configuração"
    
    cat > .env <<EOF
DB_HOST=localhost
DB_PORT=5432
DB_NAME=$DB_NAME
DB_USER=$DB_USER
DB_PASSWORD=$DB_PASSWORD
API_SECRET_KEY=$(openssl rand -hex 32)
EOF
    
    print_success "Arquivo .env criado"
    
    # Criar usuário admin
    print_step "Criando usuário administrador"
    
    read -p "Email do admin [admin@fazenda.com]: " ADMIN_EMAIL
    ADMIN_EMAIL=${ADMIN_EMAIL:-admin@fazenda.com}
    
    read -sp "Senha do admin: " ADMIN_PASSWORD
    echo ""
    
    PASSWORD_HASH=$(echo -n "$ADMIN_PASSWORD" | sha256sum | cut -d' ' -f1)
    
    sudo -u postgres psql -d $DB_NAME <<EOF
INSERT INTO usuarios (nome, email, senha_hash, nivel_acesso)
VALUES ('Administrador', '$ADMIN_EMAIL', '$PASSWORD_HASH', 'admin');
EOF
    
    print_success "Usuário admin criado"
    
    # Criar serviço systemd
    print_step "Configurando serviço systemd"
    
    WORK_DIR=$(pwd)
    
    sudo tee /etc/systemd/system/gado-api.service > /dev/null <<EOF
[Unit]
Description=Gado API
After=network.target postgresql.service

[Service]
Type=simple
User=$USER
WorkingDirectory=$WORK_DIR
Environment="PATH=$WORK_DIR/venv/bin"
ExecStart=$WORK_DIR/venv/bin/uvicorn api_gado:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
EOF
    
    sudo systemctl daemon-reload
    sudo systemctl start gado-api
    sudo systemctl enable gado-api
    
    print_success "Serviço configurado"
    
    # Configurar Nginx
    print_step "Configurando Nginx"
    
    sudo mkdir -p /var/www/gado
    sudo cp mobile_app.html /var/www/gado/index.html
    sudo cp manifest.json /var/www/gado/
    sudo cp sw.js /var/www/gado/
    
    # Editar URL da API no HTML
    IP_LOCAL=$(ip addr show | grep -oP '(?<=inet\s)\d+(\.\d+){3}' | grep -v '127.0.0.1' | head -1)
    sudo sed -i "s|http://localhost:8000/api|http://$IP_LOCAL:8000/api|g" /var/www/gado/index.html
    
    sudo cp nginx.conf /etc/nginx/sites-available/gado
    sudo ln -sf /etc/nginx/sites-available/gado /etc/nginx/sites-enabled/
    sudo rm -f /etc/nginx/sites-enabled/default
    
    sudo nginx -t
    sudo systemctl restart nginx
    
    print_success "Nginx configurado"
    
    # Firewall
    print_step "Configurando firewall"
    
    if command -v ufw &> /dev/null; then
        sudo ufw allow 80/tcp
        sudo ufw allow 443/tcp
        sudo ufw allow 8000/tcp
        print_success "Firewall configurado (UFW)"
    elif command -v firewall-cmd &> /dev/null; then
        sudo firewall-cmd --permanent --add-port=80/tcp
        sudo firewall-cmd --permanent --add-port=443/tcp
        sudo firewall-cmd --permanent --add-port=8000/tcp
        sudo firewall-cmd --reload
        print_success "Firewall configurado (firewalld)"
    fi
    
    # Mostrar informações
    echo ""
    echo -e "${GREEN}╔═══════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║           INSTALAÇÃO CONCLUÍDA COM SUCESSO!              ║${NC}"
    echo -e "${GREEN}╚═══════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${YELLOW}Acesse o sistema:${NC}"
    echo "  • Interface Web: http://$IP_LOCAL"
    echo "  • API: http://$IP_LOCAL:8000"
    echo "  • API Docs: http://$IP_LOCAL:8000/docs"
    echo ""
    echo -e "${YELLOW}Login:${NC}"
    echo "  • Email: $ADMIN_EMAIL"
    echo "  • Senha: [a que você configurou]"
    echo ""
    echo -e "${YELLOW}Comandos úteis:${NC}"
    echo "  • Ver logs API: sudo journalctl -u gado-api -f"
    echo "  • Reiniciar API: sudo systemctl restart gado-api"
    echo "  • Status: sudo systemctl status gado-api"
    echo "  • Backup: pg_dump -U $DB_USER -d $DB_NAME > backup.sql"
    echo ""

# ==================== APENAS CONFIGURAÇÃO ====================
elif [ "$INSTALL_TYPE" = "config" ]; then
    print_step "Configuração de banco existente"
    
    read -p "Host do PostgreSQL [localhost]: " DB_HOST
    DB_HOST=${DB_HOST:-localhost}
    
    read -p "Porta [5432]: " DB_PORT
    DB_PORT=${DB_PORT:-5432}
    
    read -p "Nome do banco: " DB_NAME
    read -p "Usuário: " DB_USER
    read -sp "Senha: " DB_PASSWORD
    echo ""
    
    # Criar .env
    cat > .env <<EOF
DB_HOST=$DB_HOST
DB_PORT=$DB_PORT
DB_NAME=$DB_NAME
DB_USER=$DB_USER
DB_PASSWORD=$DB_PASSWORD
API_SECRET_KEY=$(openssl rand -hex 32)
EOF
    
    print_success "Arquivo .env criado"
    
    # Testar conexão
    print_step "Testando conexão..."
    
    if PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -c '\q' 2>/dev/null; then
        print_success "Conexão bem-sucedida"
        
        # Executar schema
        read -p "Deseja executar o schema SQL? (s/n): " RUN_SCHEMA
        if [ "$RUN_SCHEMA" = "s" ]; then
            PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -f postgres_schema.sql
            print_success "Schema executado"
        fi
    else
        print_error "Falha na conexão. Verifique as credenciais."
        exit 1
    fi
fi

echo ""
print_success "Setup concluído!"
echo ""
echo -e "${BLUE}Próximos passos:${NC}"
echo "1. Acesse o sistema pelo navegador"
echo "2. Faça login com as credenciais criadas"
echo "3. Cadastre seus animais"
echo "4. Configure relatórios automáticos no N8N"
echo "5. Instale no celular (veja GUIA_CELULAR.md)"
echo ""
