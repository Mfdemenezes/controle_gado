"""
API REST para Sistema de Controle de Gado de Corte
FastAPI + PostgreSQL
"""

from fastapi import FastAPI, Body, HTTPException, Depends, status, Header
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, timedelta, date
import psycopg2
from psycopg2.extras import RealDictCursor
import secrets
import hashlib
import os
from dotenv import load_dotenv

load_dotenv()

# Configuração do FastAPI com customização
app = FastAPI(
    title="🐮 Controle de Gado API",
    description="""## Sistema de Gestão de Rebanho Bovino - Gado de Corte

API REST completa para controle de gado de corte com funcionalidades avançadas.

### 📊 Recursos Principais

* **Autenticação JWT** - Sistema seguro com tokens
* **Gestão de Animais** - Cadastro completo do rebanho
* **Pesagens** - Histórico com cálculo automático de GMD (Ganho Médio Diário)
* **Sanidade** - Vacinas, vermífugos e tratamentos
* **Movimentações** - Controle de pastos e lotes
* **Relatórios** - Performance e análises do rebanho

### 🔐 Como Usar

1. Faça login em `/api/auth/login` para obter o token
2. Clique em **Authorize** 🔒 (topo da página)
3. Cole o token retornado
4. Teste os endpoints!

### 📝 Histórico de Versões

**v1.0.0** (29/Out/2025)
- ✅ Sistema de autenticação com JWT
- ✅ CRUD completo de animais
- ✅ Registro de pesagens com cálculo de GMD
- ✅ Controle de sanidade (vacinas, vermífugos)
- ✅ Movimentações entre pastos e lotes
- ✅ Relatórios de performance e resumo
- ✅ Interface PWA mobile-first
- ✅ Deploy com HTTPS via Cloudflare

**Roadmap v1.1.0**
- 🔄 Integração com WhatsApp para alertas
- 🔄 Backup automático diário
- 🔄 Exportação de relatórios (PDF/Excel)
- 🔄 Dashboard analytics avançado

---
**Desenvolvido com ❤️ usando FastAPI + PostgreSQL**
    """,
    version="1.0.0",
    contact={
        "name": "Suporte Técnico",
        "email": "admin@fazenda.com"
    },
    license_info={
        "name": "Uso Interno",
    },
    openapi_tags=[
        {"name": "🔐 Autenticação", "description": "Login e logout no sistema"},
        {"name": "🐮 Animais", "description": "Gestão completa do rebanho"},
        {"name": "⚖️ Pesagens", "description": "Registro e consulta de pesos"},
        {"name": "💉 Sanidade", "description": "Vacinas e tratamentos"},
        {"name": "📦 Movimentações", "description": "Transferências entre pastos/lotes"},
        {"name": "📍 Lotes e Pastos", "description": "Consulta de localizações"},
        {"name": "📊 Relatórios", "description": "Análises e estatísticas"},
        {"name": "⚙️ Sistema", "description": "Health check e informações"}
    ],
    swagger_ui_parameters={
        "deepLinking": True,
        "displayRequestDuration": True,
        "filter": True,
        "syntaxHighlight.theme": "monokai"
    }
)

# CORS para permitir acesso do mobile
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, especificar domínios
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# CSS Customizado Verde Musgo
def custom_swagger_ui_html():
    return """
    <link rel="stylesheet" type="text/css" href="/docs/swagger-ui.css">
    <style>
        /* Tema Verde Musgo para Gado de Corte */
        .swagger-ui .topbar { 
            background: linear-gradient(135deg, #556B2F 0%, #6B8E23 100%) !important;
            border-bottom: 4px solid #4a5e24 !important;
        }
        .swagger-ui .info .title small {
            background: #6B8E23 !important;
            color: white !important;
            padding: 2px 8px !important;
            border-radius: 4px !important;
            font-size: 14px !important;
        }
        .swagger-ui .info .title {
            color: #556B2F !important;
            font-size: 36px !important;
            font-weight: bold !important;
        }
        .swagger-ui .btn.authorize {
            background-color: #6B8E23 !important;
            border-color: #556B2F !important;
        }
        .swagger-ui .btn.execute {
            background-color: #556B2F !important;
        }
        .swagger-ui .btn.execute:hover {
            background-color: #6B8E23 !important;
        }
        .swagger-ui .opblock.opblock-post {
            background: rgba(107, 142, 35, 0.12) !important;
            border-color: #6B8E23 !important;
        }
        .swagger-ui .opblock.opblock-post .opblock-summary-method {
            background: #6B8E23 !important;
        }
        .swagger-ui .opblock.opblock-get {
            background: rgba(85, 107, 47, 0.08) !important;
            border-color: #556B2F !important;
        }
        .swagger-ui .opblock.opblock-get .opblock-summary-method {
            background: #556B2F !important;
        }
        .swagger-ui .scheme-container {
            background: #f5f8f0 !important;
            border: 1px solid #d0d8c0 !important;
        }
        .swagger-ui a { color: #556B2F !important; }
        .swagger-ui .opblock-tag { border-bottom: 2px solid #556B2F !important; }
    </style>
    """

app.add_route("/swagger-custom-css", lambda: HTMLResponse(content=custom_swagger_ui_html()), include_in_schema=False)



security = HTTPBearer()

# Configurações do banco de dados
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', '5432'),
    'database': os.getenv('DB_NAME', 'controle_gado'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', 'postgres')
}

# ==================== MODELOS PYDANTIC ====================

class LoginRequest(BaseModel):
    email: str
    senha: str

class LoginResponse(BaseModel):
    token: str
    usuario: dict
    expires_at: str

class UsuarioCreate(BaseModel):
    nome: str
    email: str
    senha: str
    nivel_acesso: str = "operador"  # admin, gerente ou operador

class UsuarioUpdate(BaseModel):
    nome: Optional[str] = None
    email: Optional[str] = None
    senha: Optional[str] = None
    nivel_acesso: Optional[str] = None
    ativo: Optional[bool] = None

class AnimalCreate(BaseModel):
    brinco: str
    nome: Optional[str] = None
    sexo: str = Field(..., pattern="^[MF]$")
    raca: Optional[str] = None
    data_nascimento: Optional[str] = None
    peso_nascimento: Optional[float] = None
    peso_atual: Optional[float] = None
    lote: Optional[str] = None
    pasto: Optional[str] = None
    origem: Optional[str] = None
    valor_compra: Optional[float] = None
    observacoes: Optional[str] = None

class AnimalUpdate(BaseModel):
    brinco: Optional[str] = None
    nome: Optional[str] = None
    sexo: Optional[str] = None
    data_nascimento: Optional[str] = None
    raca_id: Optional[int] = None
    peso_atual: Optional[float] = None
    lote_id: Optional[int] = None
    pasto_id: Optional[int] = None
    lote: Optional[str] = None
    pasto: Optional[str] = None
    status: Optional[str] = None
    observacoes: Optional[str] = None

class PesagemCreate(BaseModel):
    animal_id: int
    peso: float
    data_pesagem: Optional[str] = None
    condicao_corporal: Optional[int] = Field(None, ge=1, le=5)
    observacoes: Optional[str] = None

class SanidadeCreate(BaseModel):
    animal_id: int
    tipo: str
    produto: str
    dose: Optional[str] = None
    aplicador: Optional[str] = None
    data_aplicacao: Optional[str] = None
    proxima_aplicacao: Optional[str] = None
    custo: Optional[float] = None
    observacoes: Optional[str] = None

class MovimentacaoCreate(BaseModel):
    animal_id: int
    tipo: str
    origem: Optional[str] = None
    destino: Optional[str] = None
    motivo: Optional[str] = None
    responsavel: Optional[str] = None
    data_movimentacao: Optional[str] = None

# ==================== FUNÇÕES DE BANCO DE DADOS ====================

def get_db_connection():
    """Cria conexão com o banco de dados"""
    try:
        conn = psycopg2.connect(**DB_CONFIG, cursor_factory=RealDictCursor)
        return conn
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao conectar no banco: {str(e)}")

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verifica se o token é válido"""
    token = credentials.credentials

    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        cur.execute("""
            SELECT s.*, u.nome, u.email, u.nivel_acesso
            FROM sessoes s
            INNER JOIN usuarios u ON s.usuario_id = u.id
            WHERE s.token = %s 
            AND s.expires_at > NOW()
            AND u.ativo = TRUE
        """, (token,))
        
        sessao = cur.fetchone()
        
        if not sessao:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido ou expirado"
            )
        
        return dict(sessao)
    
    finally:
        cur.close()
        conn.close()

# ==================== FUNÇÕES DE CONTROLE DE ACESSO ====================

def require_admin(user_data: dict):
    """Verifica se o usuário é admin"""
    if user_data.get('nivel_acesso') != 'admin':
        raise HTTPException(status_code=403, detail="Acesso negado. Apenas administradores.")

def require_admin_or_gerente(user_data: dict):
    """Verifica se o usuário é admin ou gerente"""
    if user_data.get('nivel_acesso') not in ['admin', 'gerente']:
        raise HTTPException(status_code=403, detail="Acesso negado. Apenas administradores e gerentes.")

def can_delete(user_data: dict):
    """Verifica se pode deletar (admin ou gerente)"""
    return user_data.get('nivel_acesso') in ['admin', 'gerente']

def can_edit(user_data: dict):
    """Verifica se pode editar (admin ou gerente)"""
    return user_data.get('nivel_acesso') in ['admin', 'gerente']

# ==================== ENDPOINTS DE AUTENTICAÇÃO ====================

@app.post("/api/auth/login", tags=["🔐 Autenticação"], response_model=LoginResponse)
def login(credentials: LoginRequest):
    """Endpoint de login"""
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        # Busca usuário
        cur.execute("""
            SELECT id, nome, email, senha_hash, nivel_acesso, ativo
            FROM usuarios
            WHERE email = %s
        """, (credentials.email,))
        
        usuario = cur.fetchone()
        
        if not usuario or not usuario['ativo']:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciais inválidas"
            )
        
        # Verifica senha (em produção usar bcrypt)
        senha_hash = hashlib.sha256(credentials.senha.encode()).hexdigest()
        
        if usuario['senha_hash'] != senha_hash:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciais inválidas"
            )
        
        # Gera token
        token = secrets.token_urlsafe(32)
        expires_at = datetime.now() + timedelta(days=30)
        
        # Salva sessão
        cur.execute("""
            INSERT INTO sessoes (usuario_id, token, expires_at)
            VALUES (%s, %s, %s)
            RETURNING id
        """, (usuario['id'], token, expires_at))
        
        conn.commit()
        
        # Atualiza último acesso
        cur.execute("""
            UPDATE usuarios 
            SET ultimo_acesso = NOW() 
            WHERE id = %s
        """, (usuario['id'],))
        
        conn.commit()
        
        return {
            "token": token,
            "usuario": {
                "id": usuario['id'],
                "nome": usuario['nome'],
                "email": usuario['email'],
                "nivel_acesso": usuario['nivel_acesso']
            },
            "expires_at": expires_at.isoformat()
        }
    
    finally:
        cur.close()
        conn.close()

@app.post("/api/auth/logout", tags=["🔐 Autenticação"])
def logout(user_data: dict = Depends(verify_token)):
    """Endpoint de logout"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("""
            DELETE FROM sessoes 
            WHERE usuario_id = %s
        """, (user_data['usuario_id'],))
        
        conn.commit()
        
        return {"message": "Logout realizado com sucesso"}
    
    finally:
        cur.close()
        conn.close()

# ==================== ENDPOINTS DE USUÁRIOS ====================

@app.get("/api/usuarios", tags=["👥 Usuários"])
def listar_usuarios(user_data: dict = Depends(verify_token)):
    """Lista todos os usuários (apenas admin)"""
    if user_data.get('nivel_acesso') != 'admin':
        raise HTTPException(status_code=403, detail="Acesso negado. Apenas administradores.")

    conn = get_db_connection()
    cur = conn.cursor()

    try:
        cur.execute("""
            SELECT id, nome, email, nivel_acesso, ativo,
                   created_at, ultimo_acesso
            FROM usuarios
            ORDER BY nome
        """)
        usuarios = cur.fetchall()
        return [dict(u) for u in usuarios]

    finally:
        cur.close()
        conn.close()

@app.post("/api/usuarios", tags=["👥 Usuários"])
def criar_usuario(usuario: UsuarioCreate, user_data: dict = Depends(verify_token)):
    """Cria novo usuário (apenas admin)"""
    if user_data.get('nivel_acesso') != 'admin':
        raise HTTPException(status_code=403, detail="Acesso negado. Apenas administradores.")

    conn = get_db_connection()
    cur = conn.cursor()

    try:
        # Verifica se email já existe
        cur.execute("SELECT id FROM usuarios WHERE email = %s", (usuario.email,))
        if cur.fetchone():
            raise HTTPException(status_code=400, detail="Email já cadastrado")

        # Hash da senha
        senha_hash = hashlib.sha256(usuario.senha.encode()).hexdigest()

        # Insere usuário
        cur.execute("""
            INSERT INTO usuarios (nome, email, senha_hash, nivel_acesso, ativo)
            VALUES (%s, %s, %s, %s, true)
            RETURNING id, nome, email, nivel_acesso, ativo, created_at
        """, (usuario.nome, usuario.email, senha_hash, usuario.nivel_acesso))

        novo_usuario = cur.fetchone()
        conn.commit()

        return dict(novo_usuario)

    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))

    finally:
        cur.close()
        conn.close()

@app.put("/api/usuarios/{usuario_id}", tags=["👥 Usuários"])
def atualizar_usuario(
    usuario_id: int,
    usuario: UsuarioUpdate,
    user_data: dict = Depends(verify_token)
):
    """Atualiza usuário (admin pode editar qualquer um, usuário comum apenas a si mesmo)"""
    # Admin pode editar qualquer um, usuário comum só pode editar a si mesmo
    if user_data.get('nivel_acesso') != 'admin' and user_data.get('usuario_id') != usuario_id:
        raise HTTPException(status_code=403, detail="Acesso negado")

    conn = get_db_connection()
    cur = conn.cursor()

    try:
        updates = []
        params = []

        for field, value in usuario.dict(exclude_unset=True).items():
            if value is not None:
                if field == 'senha':
                    # Hash da nova senha
                    senha_hash = hashlib.sha256(value.encode()).hexdigest()
                    updates.append("senha_hash = %s")
                    params.append(senha_hash)
                elif field == 'nivel_acesso' or field == 'ativo':
                    # Apenas admin pode alterar nivel_acesso e ativo
                    if user_data.get('nivel_acesso') != 'admin':
                        continue
                    updates.append(f"{field} = %s")
                    params.append(value)
                else:
                    updates.append(f"{field} = %s")
                    params.append(value)

        if not updates:
            raise HTTPException(status_code=400, detail="Nenhum campo para atualizar")

        params.append(usuario_id)
        query = f"UPDATE usuarios SET {', '.join(updates)} WHERE id = %s"

        cur.execute(query, params)
        conn.commit()

        if cur.rowcount == 0:
            raise HTTPException(status_code=404, detail="Usuário não encontrado")

        return {"message": "Usuário atualizado com sucesso"}

    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))

    finally:
        cur.close()
        conn.close()

@app.delete("/api/usuarios/{usuario_id}", tags=["👥 Usuários"])
def desativar_usuario(usuario_id: int, user_data: dict = Depends(verify_token)):
    """Desativa usuário (apenas admin)"""
    if user_data.get('nivel_acesso') != 'admin':
        raise HTTPException(status_code=403, detail="Acesso negado. Apenas administradores.")

    # Não pode desativar a si mesmo
    if user_data.get('usuario_id') == usuario_id:
        raise HTTPException(status_code=400, detail="Você não pode desativar sua própria conta")

    conn = get_db_connection()
    cur = conn.cursor()

    try:
        cur.execute("""
            UPDATE usuarios
            SET ativo = false
            WHERE id = %s
        """, (usuario_id,))

        conn.commit()

        if cur.rowcount == 0:
            raise HTTPException(status_code=404, detail="Usuário não encontrado")

        return {"message": "Usuário desativado com sucesso"}

    finally:
        cur.close()
        conn.close()

# ==================== ENDPOINTS DE ANIMAIS ====================

@app.get("/api/animais", tags=["🐮 Animais"])
def listar_animais(
    status: Optional[str] = "ativo",
    lote: Optional[str] = None,
    pasto: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    user_data: dict = Depends(verify_token)
):
    """Lista animais com filtros"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        query = "SELECT * FROM vw_rebanho_ativo WHERE 1=1"
        params = []
        
        if status:
            query += " AND status = %s"
            params.append(status)
        
        if lote:
            query += " AND lote = %s"
            params.append(lote)
        
        if pasto:
            query += " AND pasto = %s"
            params.append(pasto)
        
        query += " ORDER BY brinco LIMIT %s OFFSET %s"
        params.extend([limit, offset])
        
        cur.execute(query, params)
        animais = cur.fetchall()
        
        return {
            "total": len(animais),
            "data": [dict(animal) for animal in animais]
        }
    
    finally:
        cur.close()
        conn.close()

@app.get("/api/animais/{animal_id}", tags=["🐮 Animais"])
def buscar_animal(animal_id: int, user_data: dict = Depends(verify_token)):
    """Busca animal por ID"""
    conn = get_db_connection()
    cur = conn.cursor()

    try:
        # Buscar direto da tabela animais para pegar todos os campos
        cur.execute("""
            SELECT a.*,
                   r.nome as raca_nome,
                   l.nome as lote_nome,
                   p.nome as pasto_nome,
                   EXTRACT(YEAR FROM AGE(CURRENT_DATE, a.data_nascimento)) as idade_anos,
                   EXTRACT(MONTH FROM AGE(CURRENT_DATE, a.data_nascimento)) %% 12 as idade_meses,
                   (SELECT peso FROM pesagens WHERE animal_id = a.id ORDER BY data_pesagem DESC LIMIT 1) as ultimo_peso,
                   (SELECT data_pesagem FROM pesagens WHERE animal_id = a.id ORDER BY data_pesagem DESC LIMIT 1) as data_ultimo_peso
            FROM animais a
            LEFT JOIN racas r ON a.raca_id = r.id
            LEFT JOIN lotes l ON a.lote_id = l.id
            LEFT JOIN pastos p ON a.pasto_id = p.id
            WHERE a.id = %s
        """, (animal_id,))
        animal = cur.fetchone()

        if not animal:
            raise HTTPException(status_code=404, detail="Animal não encontrado")

        return dict(animal)

    finally:
        cur.close()
        conn.close()

@app.get("/api/animais/brinco/{brinco}", tags=["🐮 Animais"])
def buscar_animal_por_brinco(brinco: str, user_data: dict = Depends(verify_token)):
    """Busca animal por número do brinco"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("SELECT * FROM vw_rebanho_ativo WHERE brinco = %s", (brinco,))
        animal = cur.fetchone()
        
        if not animal:
            raise HTTPException(status_code=404, detail="Animal não encontrado")
        
        return dict(animal)
    
    finally:
        cur.close()
        conn.close()

@app.post("/api/animais", tags=["🐮 Animais"], status_code=status.HTTP_201_CREATED)
def cadastrar_animal(animal: AnimalCreate, user_data: dict = Depends(verify_token)):
    """Cadastra novo animal"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("""
            INSERT INTO animais (
                brinco, nome, sexo, raca, data_nascimento, peso_nascimento,
                peso_atual, lote, pasto, origem, valor_compra, observacoes
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (
            animal.brinco, animal.nome, animal.sexo, animal.raca,
            animal.data_nascimento, animal.peso_nascimento, animal.peso_atual,
            animal.lote, animal.pasto, animal.origem, animal.valor_compra,
            animal.observacoes
        ))
        
        animal_id = cur.fetchone()['id']
        conn.commit()

        # Registra pesagem inicial (somente se peso_atual foi informado)
        if animal.peso_atual is not None:
            cur.execute("""
                INSERT INTO pesagens (animal_id, peso, observacoes)
                VALUES (%s, %s, %s)
            """, (animal_id, animal.peso_atual, 'Pesagem inicial - cadastro'))
            conn.commit()

        return {"id": animal_id, "message": "Animal cadastrado com sucesso"}
    
    except psycopg2.IntegrityError as e:
        conn.rollback()
        if 'unique' in str(e).lower():
            raise HTTPException(status_code=400, detail="Brinco já cadastrado")
        raise HTTPException(status_code=400, detail=str(e))
    
    finally:
        cur.close()
        conn.close()

@app.put("/api/animais/{animal_id}", tags=["🐮 Animais"])
def atualizar_animal(
    animal_id: int,
    animal: AnimalUpdate,
    user_data: dict = Depends(verify_token)
):
    """Atualiza dados do animal"""
    conn = get_db_connection()
    cur = conn.cursor()

    try:
        # Verificar estrutura da tabela (executar uma vez)
        cur.execute("""
            SELECT column_name, data_type
            FROM information_schema.columns
            WHERE table_name = 'animais'
            AND column_name IN ('raca_id', 'lote_id', 'pasto_id')
            ORDER BY column_name
        """)
        colunas = cur.fetchall()
        print(f"DEBUG: Colunas na tabela: {colunas}")

        # Log dos dados recebidos
        print(f"DEBUG: Atualizando animal {animal_id}")
        print(f"DEBUG: Dados recebidos: {animal.dict(exclude_unset=True)}")

        # Monta query dinâmica com campos não nulos
        updates = []
        params = []

        for field, value in animal.dict(exclude_unset=True).items():
            if value is not None:
                updates.append(f"{field} = %s")
                params.append(value)

        if not updates:
            raise HTTPException(status_code=400, detail="Nenhum campo para atualizar")

        params.append(animal_id)
        query = f"UPDATE animais SET {', '.join(updates)} WHERE id = %s"

        print(f"DEBUG: Query: {query}")
        print(f"DEBUG: Params: {params}")

        cur.execute(query, params)
        conn.commit()

        print(f"DEBUG: Rows affected: {cur.rowcount}")
        
        if cur.rowcount == 0:
            raise HTTPException(status_code=404, detail="Animal não encontrado")
        
        return {"message": "Animal atualizado com sucesso"}
    
    finally:
        cur.close()

@app.delete("/api/animais/{animal_id}", tags=["🐮 Animais"])
async def deletar_animal(animal_id: int, user_data: dict = Depends(verify_token)):
    """Deletar animal (soft delete) - Apenas admin e gerente"""
    require_admin_or_gerente(user_data)

    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    try:
        cur.execute(
            "UPDATE animais SET status = 'inativo', updated_at = NOW() WHERE id = %s RETURNING id, brinco",
            (animal_id,)
        )
        animal = cur.fetchone()
        if not animal:
            raise HTTPException(status_code=404, detail="Animal não encontrado")
        conn.commit()
        return {"message": f"Animal {animal['brinco']} excluído com sucesso"}
    except psycopg2.Error as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cur.close()
        conn.close()


        conn.close()

# ==================== ENDPOINTS DE PESAGENS ====================

@app.get("/api/pesagens/{animal_id}", tags=["⚖️ Pesagens"])
def listar_pesagens(animal_id: int, user_data: dict = Depends(verify_token)):
    """Lista pesagens de um animal"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("""
            SELECT * FROM pesagens 
            WHERE animal_id = %s 
            ORDER BY data_pesagem DESC
        """, (animal_id,))
        
        pesagens = cur.fetchall()
        
        return {
            "total": len(pesagens),
            "data": [dict(p) for p in pesagens]
        }
    
    finally:
        cur.close()
        conn.close()

@app.post("/api/pesagens", tags=["⚖️ Pesagens"], status_code=status.HTTP_201_CREATED)
def registrar_pesagem(pesagem: PesagemCreate, user_data: dict = Depends(verify_token)):
    """Registra nova pesagem"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        data_pesagem = pesagem.data_pesagem or datetime.now().date().isoformat()
        
        cur.execute("""
            INSERT INTO pesagens (
                animal_id, peso, data_pesagem, condicao_corporal, observacoes
            ) VALUES (%s, %s, %s, %s, %s)
            RETURNING id
        """, (
            pesagem.animal_id, pesagem.peso, data_pesagem,
            pesagem.condicao_corporal, pesagem.observacoes
        ))
        
        pesagem_id = cur.fetchone()['id']
        
        # Atualiza peso atual do animal
        cur.execute("""
            UPDATE animais 
            SET peso_atual = %s 
            WHERE id = %s
        """, (pesagem.peso, pesagem.animal_id))
        
        conn.commit()
        
        return {"id": pesagem_id, "message": "Pesagem registrada com sucesso"}
    
    finally:
        cur.close()
        conn.close()


@app.put("/api/pesagens/{pesagem_id}", tags=["⚖️ Pesagens"])
def atualizar_pesagem(
    pesagem_id: int,
    peso: Optional[float] = Body(None),
    data_pesagem: Optional[str] = Body(None),
    condicao_corporal: Optional[int] = Body(None),
    observacoes: Optional[str] = Body(None),
    user_data: dict = Depends(verify_token)
):
    """Atualiza pesagem existente"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # Verifica se a pesagem existe
        cur.execute("SELECT * FROM pesagens WHERE id = %s", (pesagem_id,))
        pesagem_antiga = cur.fetchone()
        
        if not pesagem_antiga:
            raise HTTPException(status_code=404, detail="Pesagem não encontrada")
        
        # Monta campos para atualizar
        campos = []
        valores = []
        
        if peso is not None:
            campos.append("peso = %s")
            valores.append(peso)
        if data_pesagem is not None:
            campos.append("data_pesagem = %s")
            valores.append(data_pesagem)
        if condicao_corporal is not None:
            campos.append("condicao_corporal = %s")
            valores.append(condicao_corporal)
        if observacoes is not None:
            campos.append("observacoes = %s")
            valores.append(observacoes)
        
        if not campos:
            raise HTTPException(status_code=400, detail="Nenhum campo para atualizar")
        
        valores.append(pesagem_id)
        sql = f"UPDATE pesagens SET {', '.join(campos)} WHERE id = %s RETURNING *"
        cur.execute(sql, valores)
        
        pesagem_atualizada = cur.fetchone()
        
        # Se peso foi alterado, atualiza peso_atual do animal
        if peso is not None:
            cur.execute("""
                UPDATE animais 
                SET peso_atual = %s 
                WHERE id = %s
            """, (peso, pesagem_antiga['animal_id']))
        
        conn.commit()
        return dict(pesagem_atualizada)
    
    finally:
        cur.close()
        conn.close()

@app.delete("/api/pesagens/{pesagem_id}", tags=["⚖️ Pesagens"])
def deletar_pesagem(pesagem_id: int, user_data: dict = Depends(verify_token)):
    """Deleta pesagem - Apenas admin e gerente"""
    require_admin_or_gerente(user_data)

    conn = get_db_connection()
    cur = conn.cursor()

    try:
        # Verifica se existe
        cur.execute("SELECT * FROM pesagens WHERE id = %s", (pesagem_id,))
        if not cur.fetchone():
            raise HTTPException(status_code=404, detail="Pesagem não encontrada")
        
        cur.execute("DELETE FROM pesagens WHERE id = %s", (pesagem_id,))
        conn.commit()
        
        return {"message": "Pesagem deletada com sucesso"}
    
    finally:
        cur.close()
        conn.close()


# ==================== ENDPOINTS DE SANIDADE ====================

@app.post("/api/sanidade", tags=["💉 Sanidade"], status_code=status.HTTP_201_CREATED)
def registrar_sanidade(sanidade: SanidadeCreate, user_data: dict = Depends(verify_token)):
    """Registra aplicação de sanidade"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        data_aplicacao = sanidade.data_aplicacao or datetime.now().date().isoformat()
        
        cur.execute("""
            INSERT INTO sanidade (
                animal_id, tipo, produto, dose, aplicador,
                data_aplicacao, proxima_aplicacao, custo, observacoes
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (
            sanidade.animal_id, sanidade.tipo, sanidade.produto, sanidade.dose,
            sanidade.aplicador, data_aplicacao, sanidade.proxima_aplicacao,
            sanidade.custo, sanidade.observacoes
        ))
        
        sanidade_id = cur.fetchone()['id']
        conn.commit()
        
        return {"id": sanidade_id, "message": "Sanidade registrada com sucesso"}
    
    finally:
        cur.close()
        conn.close()

@app.get("/api/sanidade/proximas", tags=["💉 Sanidade"])
def listar_proximas_aplicacoes(dias: int = 30, user_data: dict = Depends(verify_token)):
    """Lista próximas aplicações programadas"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("""
            SELECT * FROM vw_aplicacoes_proximas 
            WHERE dias_restantes <= %s
            ORDER BY proxima_aplicacao
        """, (dias,))
        
        aplicacoes = cur.fetchall()
        
        return {
            "total": len(aplicacoes),
            "data": [dict(a) for a in aplicacoes]
        }
    
    finally:
        cur.close()
        conn.close()

# ==================== ENDPOINTS DE RELATÓRIOS ====================

@app.get("/api/relatorios/resumo", tags=["📊 Relatórios"])
def relatorio_resumo(user_data: dict = Depends(verify_token)):
    """Relatório resumo do rebanho"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("SELECT * FROM vw_resumo_rebanho")
        resumo = cur.fetchone()
        
        return dict(resumo) if resumo else {}
    
    finally:
        cur.close()
        conn.close()

@app.get("/api/relatorios/performance", tags=["📊 Relatórios"])
def relatorio_performance(limit: int = 50, user_data: dict = Depends(verify_token)):
    """Relatório de performance (GMD)"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("""
            SELECT * FROM vw_performance_animais 
            ORDER BY gmd DESC 
            LIMIT %s
        """, (limit,))
        
        performance = cur.fetchall()
        
        return {
            "total": len(performance),
            "data": [dict(p) for p in performance]
        }
    
    finally:
        cur.close()
        conn.close()

# ==================== ENDPOINTS DE MOVIMENTAÇÕES ====================

@app.post("/api/movimentacoes", tags=["📦 Movimentações"], status_code=status.HTTP_201_CREATED)
def registrar_movimentacao(
    movimentacao: MovimentacaoCreate,
    user_data: dict = Depends(verify_token)
):
    """Registra movimentação de animal"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        data_mov = movimentacao.data_movimentacao or datetime.now().date().isoformat()
        
        cur.execute("""
            INSERT INTO movimentacoes (
                animal_id, tipo, origem, destino, motivo, responsavel, data_movimentacao
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (
            movimentacao.animal_id, movimentacao.tipo, movimentacao.origem,
            movimentacao.destino, movimentacao.motivo, movimentacao.responsavel,
            data_mov
        ))
        
        mov_id = cur.fetchone()['id']
        
        # Atualiza pasto/lote do animal se aplicável
        if movimentacao.tipo == 'troca_pasto' and movimentacao.destino:
            cur.execute("""
                UPDATE animais 
                SET pasto = %s 
                WHERE id = %s
            """, (movimentacao.destino, movimentacao.animal_id))
        
        elif movimentacao.tipo == 'troca_lote' and movimentacao.destino:
            cur.execute("""
                UPDATE animais 
                SET lote = %s 
                WHERE id = %s
            """, (movimentacao.destino, movimentacao.animal_id))
        
        conn.commit()
        
        return {"id": mov_id, "message": "Movimentação registrada com sucesso"}
    
    finally:
        cur.close()
        conn.close()

# ==================== ENDPOINTS AUXILIARES ====================

@app.get("/api/lotes", tags=["📍 Lotes e Pastos"])
def listar_lotes(user_data: dict = Depends(verify_token)):
    """Lista todos os lotes"""
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        cur.execute("""
            SELECT l.*, COUNT(a.id) as total_animais
            FROM lotes l
            LEFT JOIN animais a ON l.nome = a.lote AND a.status = 'ativo'
            WHERE l.status = 'ativo'
            GROUP BY l.id
            ORDER BY l.nome
        """)
        
        lotes = cur.fetchall()
        
        return {
            "total": len(lotes),
            "data": [dict(l) for l in lotes]
        }
    
    finally:
        cur.close()
        conn.close()

@app.get("/api/pastos", tags=["📍 Lotes e Pastos"])
def listar_pastos(user_data: dict = Depends(verify_token)):
    """Lista todos os pastos"""
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        cur.execute("""
            SELECT p.*, COUNT(a.id) as total_animais
            FROM pastos p
            LEFT JOIN animais a ON p.nome = a.pasto AND a.status = 'ativo'
            WHERE p.status != 'encerrado'
            GROUP BY p.id
            ORDER BY p.nome
        """)
        
        pastos = cur.fetchall()
        
        return {
            "total": len(pastos),
            "data": [dict(p) for p in pastos]
        }
    
    finally:
        cur.close()
        conn.close()



# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# NOVOS ENDPOINTS v2.0 - SISTEMA REPRODUTIVO
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# ============================================================
# RAÇAS
# ============================================================

@app.get("/api/racas", tags=["🧬 Raças"])
async def listar_racas(ativo: Optional[bool] = None, user_data: dict = Depends(verify_token)):
    """Listar todas as raças"""
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    try:
        if ativo is None:
            cur.execute("SELECT * FROM racas WHERE ativo = true ORDER BY nome")
        else:
            cur.execute("SELECT * FROM racas WHERE ativo = %s ORDER BY nome", (ativo,))
        racas = cur.fetchall()
        return [dict(r) for r in racas]
    finally:
        cur.close()
        conn.close()

@app.get("/api/racas/{raca_id}", tags=["🧬 Raças"])
async def obter_raca(raca_id: int, user_data: dict = Depends(verify_token)):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    try:
        cur.execute("SELECT * FROM racas WHERE id = %s", (raca_id,))
        raca = cur.fetchone()
        if not raca:
            raise HTTPException(status_code=404, detail="Raça não encontrada")
        return dict(raca)
    finally:
        cur.close()
        conn.close()

@app.post("/api/racas", tags=["🧬 Raças"], status_code=status.HTTP_201_CREATED)
async def criar_raca(nome: str = Body(...), descricao: Optional[str] = Body(None), origem: Optional[str] = Body(None), user_data: dict = Depends(verify_token)):
    """Cadastrar nova raça (ou reativar se já existir inativa)"""
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    try:
        # Verificar se já existe uma raça com este nome (ativa ou inativa)
        cur.execute("SELECT * FROM racas WHERE nome = %s", (nome,))
        raca_existente = cur.fetchone()

        if raca_existente:
            # Se existe mas está inativa, reativa
            if not raca_existente['ativo']:
                cur.execute(
                    "UPDATE racas SET ativo = true, descricao = %s, origem = %s, updated_at = NOW() WHERE id = %s RETURNING *",
                    (descricao, origem, raca_existente['id'])
                )
                raca = cur.fetchone()
                conn.commit()
                return dict(raca)
            else:
                # Se já existe e está ativa, retorna erro
                raise HTTPException(status_code=400, detail=f"Raça '{nome}' já está cadastrada e ativa")

        # Se não existe, cria nova
        cur.execute(
            "INSERT INTO racas (nome, descricao, origem) VALUES (%s, %s, %s) RETURNING *",
            (nome, descricao, origem)
        )
        raca = cur.fetchone()
        conn.commit()
        return dict(raca)
    except HTTPException:
        raise
    except psycopg2.Error as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cur.close()
        conn.close()

# ============================================================
# LOTES
# ============================================================

# Endpoint duplicado removido - usar apenas o endpoint GET /api/lotes da linha 763

@app.post("/api/lotes-v2", tags=["📍 Lotes e Pastos"], status_code=status.HTTP_201_CREATED)
async def criar_lote(nome: str = Body(...), descricao: Optional[str] = Body(None), 
                     capacidade: Optional[int] = None):
    """Cadastrar novo lote"""
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO lotes (nome, descricao, capacidade)
            VALUES (%s, %s, %s)
            RETURNING id, nome, descricao, capacidade, ativo, created_at
        """, (nome, descricao, capacidade))
        lote = cur.fetchone()
        conn.commit()
        return {"id": lote[0], "nome": lote[1], "descricao": lote[2],
                "capacidade": lote[3], "ativo": lote[4], "created_at": lote[5]}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cur.close()
        conn.close()

# ============================================================
# PASTOS
# ============================================================
# Endpoint duplicado removido - usar apenas o endpoint GET /api/pastos da linha 790

@app.post("/api/pastos-v2", tags=["📍 Lotes e Pastos"], status_code=status.HTTP_201_CREATED)
async def criar_pasto(nome: str = Body(...), area_hectares: Optional[float] = None,
                      tipo: Optional[str] = None, descricao: Optional[str] = None):
    """Cadastrar novo pasto"""
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO pastos (nome, area_hectares, tipo, descricao)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id, nome, area_hectares, tipo, descricao, ativo, created_at
        """, (nome, area_hectares, tipo, descricao))
        pasto = cur.fetchone()
        conn.commit()
        return {"id": pasto[0], "nome": pasto[1], "area_hectares": float(pasto[2]) if pasto[2] else None,
                "tipo": pasto[3], "descricao": pasto[4], "ativo": pasto[5], "created_at": pasto[6]}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cur.close()
        conn.close()

# ============================================================
# TOUROS
# ============================================================

@app.get("/api/touros", tags=["🐂 Touros"])
async def listar_touros(ativo: Optional[bool] = None):
    """Listar touros/reprodutores cadastrados"""
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    try:
        query = """
            SELECT t.id, t.brinco, t.nome, r.nome as raca, t.data_nascimento,
                   t.registro, t.ativo, t.observacoes
            FROM touros t
            LEFT JOIN racas r ON t.raca_id = r.id
        """
        if ativo is None:
            query += " WHERE t.ativo = true"
        else:
            query += f" WHERE t.ativo = {ativo}"
        query += " ORDER BY t.brinco"

        cur.execute(query)
        touros = cur.fetchall()
        return [dict(t) for t in touros]
    finally:
        cur.close()
        conn.close()

@app.post("/api/touros", tags=["🐂 Touros"], status_code=status.HTTP_201_CREATED)
async def criar_touro(brinco: str = Body(...), nome: Optional[str] = Body(None), raca_id: Optional[int] = Body(None), registro: Optional[str] = Body(None), linhagem: Optional[str] = Body(None), user_data: dict = Depends(verify_token)):
    """Cadastrar novo touro"""
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    try:
        cur.execute(
            "INSERT INTO touros (brinco, nome, raca_id, registro, linhagem) VALUES (%s, %s, %s, %s, %s) RETURNING *",
            (brinco, nome, raca_id, registro, linhagem)
        )
        touro = cur.fetchone()
        conn.commit()
        return dict(touro)
    except psycopg2.Error as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cur.close()
        conn.close()

# ============================================================
# CATEGORIAS
# ============================================================

@app.get("/api/categorias", tags=["📋 Categorias"])
async def listar_categorias():
    """Listar categorias de animais (bezerro, novilha, etc)"""
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    try:
        cur.execute("""
            SELECT id, nome, sexo, idade_min_meses, idade_max_meses, descricao, ordem
            FROM categorias
            ORDER BY ordem
        """)
        cats = cur.fetchall()
        return cats
    finally:
        cur.close()
        conn.close()


# ============================================================
# ENDPOINTS DE EDIÇÃO (PUT/DELETE)
# ============================================================

@app.put("/api/racas/{raca_id}", tags=["🧬 Raças"])
async def atualizar_raca(raca_id: int, nome: Optional[str] = Body(None),
                         descricao: Optional[str] = Body(None),
                         origem: Optional[str] = Body(None),
                         ativo: Optional[bool] = Body(None)):
    """Atualizar raça existente"""
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    try:
        updates = []
        params = []
        if nome is not None:
            updates.append("nome = %s")
            params.append(nome)
        if descricao is not None:
            updates.append("descricao = %s")
            params.append(descricao)
        if origem is not None:
            updates.append("origem = %s")
            params.append(origem)
        if ativo is not None:
            updates.append("ativo = %s")
            params.append(ativo)
        
        if not updates:
            raise HTTPException(400, detail="Nenhum campo para atualizar")
        
        params.append(raca_id)
        query = f"UPDATE racas SET {', '.join(updates)}, updated_at = CURRENT_TIMESTAMP WHERE id = %s RETURNING *"
        cur.execute(query, params)
        raca = cur.fetchone()
        
        if not raca:
            raise HTTPException(404, detail="Raça não encontrada")
        
        conn.commit()
        return dict(raca)
    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(400, detail={"error": str(e), "type": "database_error"})
    finally:
        cur.close()
        conn.close()

@app.delete("/api/racas/{raca_id}", tags=["🧬 Raças"])
async def desativar_raca(raca_id: int, user_data: dict = Depends(verify_token)):
    """Desativar raça (soft delete) - Apenas admin e gerente"""
    require_admin_or_gerente(user_data)

    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("UPDATE racas SET ativo = false WHERE id = %s RETURNING id", (raca_id,))
        if not cur.fetchone():
            raise HTTPException(404, detail="Raça não encontrada")
        conn.commit()
        return {"message": "Raça desativada com sucesso"}
    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(400, detail={"error": str(e)})
    finally:
        cur.close()
        conn.close()


@app.get("/api/touros/{touro_id}", tags=["🐂 Touros"])
async def obter_touro(touro_id: int, user_data: dict = Depends(verify_token)):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    try:
        cur.execute("SELECT * FROM touros WHERE id = %s", (touro_id,))
        touro = cur.fetchone()
        if not touro:
            raise HTTPException(status_code=404, detail="Touro não encontrado")
        return dict(touro)
    finally:
        cur.close()
        conn.close()

@app.put("/api/touros/{touro_id}", tags=["🐂 Touros"])
async def atualizar_touro(touro_id: int, nome: Optional[str] = Body(None),
                          raca_id: Optional[int] = Body(None),
                          ativo: Optional[bool] = Body(None),
                          observacoes: Optional[str] = Body(None)):
    """Atualizar touro existente"""
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    try:
        updates = []
        params = []
        if nome is not None:
            updates.append("nome = %s")
            params.append(nome)
        if raca_id is not None:
            updates.append("raca_id = %s")
            params.append(raca_id)
        if ativo is not None:
            updates.append("ativo = %s")
            params.append(ativo)
        if observacoes is not None:
            updates.append("observacoes = %s")
            params.append(observacoes)
        
        if not updates:
            raise HTTPException(400, detail="Nenhum campo para atualizar")
        
        params.append(touro_id)
        query = f"UPDATE touros SET {', '.join(updates)}, updated_at = CURRENT_TIMESTAMP WHERE id = %s RETURNING *"
        cur.execute(query, params)
        touro = cur.fetchone()
        
        if not touro:
            raise HTTPException(404, detail="Touro não encontrado")
        
        conn.commit()
        return dict(touro)
    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(400, detail={"error": str(e)})
    finally:
        cur.close()
        conn.close()


# ============================================================
# EVENTOS REPRODUTIVOS
# ============================================================

@app.post("/api/eventos-reprodutivos", tags=["👶 Reprodução"], status_code=status.HTTP_201_CREATED)
async def criar_evento_reprodutivo(
    animal_id: int = Body(...),
    tipo_evento: str = Body(...),
    data_evento: date = Body(...),
    touro_id: Optional[int] = Body(None),
    bezerra_id: Optional[int] = Body(None),
    natimorto: bool = Body(False),
    observacoes: Optional[str] = Body(None),
    user_data: dict = Depends(verify_token)
):
    """Registrar evento reprodutivo (IA, parto, diagnóstico, etc)"""
    usuario_id = user_data['usuario_id']
    
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO eventos_reprodutivos
            (animal_id, tipo_evento, data_evento, touro_id, bezerra_id, natimorto, observacoes, usuario_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id, animal_id, tipo_evento, data_evento, data_prevista, touro_id, bezerra_id, natimorto, observacoes, created_at
        """, (animal_id, tipo_evento, data_evento, touro_id, bezerra_id, natimorto, observacoes, usuario_id))
        
        evento = cur.fetchone()
        conn.commit()

        return {
            "id": evento['id'],
            "animal_id": evento['animal_id'],
            "tipo_evento": evento['tipo_evento'],
            "data_evento": evento['data_evento'],
            "data_prevista": evento['data_prevista'],
            "touro_id": evento['touro_id'],
            "bezerra_id": evento['bezerra_id'],
            "natimorto": evento['natimorto'],
            "observacoes": evento['observacoes'],
            "created_at": evento['created_at']
        }
    except Exception as e:
        conn.rollback()
        import traceback
        error_detail = f"{type(e).__name__}: {str(e)}"
        print(f"DEBUG EXCEPTION: {error_detail}")
        print(f"DEBUG TRACEBACK:\\n{traceback.format_exc()}")
        raise HTTPException(status_code=400, detail=error_detail)
    finally:
        cur.close()
        conn.close()

@app.get("/api/eventos-reprodutivos/{animal_id}", tags=["👶 Reprodução"])
async def listar_eventos_animal(animal_id: int):
    """Listar histórico reprodutivo de um animal"""
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT er.id, er.tipo_evento, er.data_evento, er.data_prevista,
                   t.brinco as touro, b.brinco as bezerra, er.natimorto, er.observacoes, er.created_at
            FROM eventos_reprodutivos er
            LEFT JOIN touros t ON er.touro_id = t.id
            LEFT JOIN animais b ON er.bezerra_id = b.id
            WHERE er.animal_id = %s
            ORDER BY er.data_evento DESC
        """, (animal_id,))
        
        eventos = cur.fetchall()
        return [{
            "id": e['id'],
            "tipo_evento": e['tipo_evento'],
            "data_evento": e['data_evento'],
            "data_prevista": e['data_prevista'],
            "touro": e['touro'],
            "bezerra": e['bezerra'],
            "natimorto": e['natimorto'],
            "observacoes": e['observacoes'],
            "created_at": e['created_at']
        } for e in eventos]
    finally:
        cur.close()
        conn.close()


@app.put("/api/eventos-reprodutivos/{evento_id}", tags=["👶 Reprodução"])
async def atualizar_evento_reprodutivo(
    evento_id: int,
    tipo_evento: Optional[str] = Body(None),
    data_evento: Optional[date] = Body(None),
    touro_id: Optional[int] = Body(None),
    bezerra_id: Optional[int] = Body(None),
    natimorto: Optional[bool] = Body(None),
    observacoes: Optional[str] = Body(None),
    user_data: dict = Depends(verify_token)
):
    """Atualiza evento reprodutivo existente"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # Verifica se existe
        cur.execute("SELECT * FROM eventos_reprodutivos WHERE id = %s", (evento_id,))
        if not cur.fetchone():
            raise HTTPException(status_code=404, detail="Evento não encontrado")
        
        # Monta campos para atualizar
        campos = []
        valores = []
        
        if tipo_evento is not None:
            campos.append("tipo_evento = %s")
            valores.append(tipo_evento)
        if data_evento is not None:
            campos.append("data_evento = %s")
            valores.append(data_evento)
        if touro_id is not None:
            campos.append("touro_id = %s")
            valores.append(touro_id)
        if bezerra_id is not None:
            campos.append("bezerra_id = %s")
            valores.append(bezerra_id)
        if natimorto is not None:
            campos.append("natimorto = %s")
            valores.append(natimorto)
        if observacoes is not None:
            campos.append("observacoes = %s")
            valores.append(observacoes)
        
        if not campos:
            raise HTTPException(status_code=400, detail="Nenhum campo para atualizar")
        
        valores.append(evento_id)
        sql = f"UPDATE eventos_reprodutivos SET {', '.join(campos)} WHERE id = %s RETURNING *"
        cur.execute(sql, valores)
        
        evento = cur.fetchone()
        conn.commit()
        
        return {
            "id": evento['id'],
            "animal_id": evento['animal_id'],
            "tipo_evento": evento['tipo_evento'],
            "data_evento": evento['data_evento'],
            "data_prevista": evento['data_prevista'],
            "touro_id": evento['touro_id'],
            "bezerra_id": evento['bezerra_id'],
            "natimorto": evento['natimorto'],
            "observacoes": evento['observacoes'],
            "created_at": evento['created_at']
        }
    
    finally:
        cur.close()
        conn.close()

@app.delete("/api/eventos-reprodutivos/{evento_id}", tags=["👶 Reprodução"])
async def deletar_evento_reprodutivo(evento_id: int, user_data: dict = Depends(verify_token)):
    """Deleta evento reprodutivo - Apenas admin e gerente"""
    require_admin_or_gerente(user_data)

    conn = get_db_connection()
    cur = conn.cursor()

    try:
        # Verifica se existe
        cur.execute("SELECT * FROM eventos_reprodutivos WHERE id = %s", (evento_id,))
        if not cur.fetchone():
            raise HTTPException(status_code=404, detail="Evento não encontrado")
        
        cur.execute("DELETE FROM eventos_reprodutivos WHERE id = %s", (evento_id,))
        conn.commit()
        
        return {"message": "Evento reprodutivo deletado com sucesso"}
    
    finally:
        cur.close()
        conn.close()


# ============================================================
# ESTATÍSTICAS REPRODUTIVAS
# ============================================================

@app.get("/api/relatorios/reproducao", tags=["📊 Relatórios"])
async def stats_reproducao():
    """Estatísticas gerais de reprodução"""
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    try:
        cur.execute("SELECT * FROM v_stats_reproducao")
        stats = cur.fetchone()
        if not stats:
            return {
                "total_prenhas": 0,
                "total_vazias": 0,
                "total_inseminadas": 0,
                "total_a_diagnosticar": 0,
                "total_recem_paridas": 0,
                "total_femeas_reprodutivas": 0
            }
        return dict(stats)
    finally:
        cur.close()
        conn.close()

@app.get("/api/relatorios/proximos-eventos", tags=["📊 Relatórios"])
async def proximos_eventos(dias: int = 30):
    """Próximos eventos (partos, diagnósticos) nos próximos N dias"""
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT id, brinco, nome, tipo_evento, data_evento, data_prevista, dias_restantes, touro
            FROM v_proximos_eventos
            WHERE dias_restantes <= %s
            ORDER BY data_prevista
        """, (dias,))
        
        eventos = cur.fetchall()
        return [{
            "id": e[0],
            "brinco": e[1],
            "nome": e[2],
            "tipo_evento": e[3],
            "data_evento": e[4],
            "data_prevista": e[5],
            "dias_restantes": e[6],
            "touro": e[7]
        } for e in eventos]
    finally:
        cur.close()
        conn.close()

@app.get("/api/femeas-reprodutivas", tags=["👶 Reprodução"])
async def listar_femeas_reprodutivas():
    """Listar todas as fêmeas em idade reprodutiva"""
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT * FROM v_femeas_reprodutivas ORDER BY brinco")
        femeas = cur.fetchall()
        return [{
            "id": f[0],
            "brinco": f[1],
            "nome": f[2],
            "sexo": f[3],
            "data_nascimento": f[4],
            "idade_meses": f[5],
            "raca": f[6],
            "categoria": f[7],
            "status_reprodutivo": f[8],
            "peso_atual": float(f[9]) if f[9] else None
        } for f in femeas]
    finally:
        cur.close()
        conn.close()



@app.get("/", tags=["⚙️ Sistema"])
def root():
    """Endpoint raiz"""
    return {
        "app": "API Controle de Gado",
        "version": "1.0.0",
        "status": "online",
        "docs": "/docs"
    }


# ===== LOTES - CRUD COMPLETO =====
@app.post("/api/lotes", tags=["📍 Lotes e Pastos"], status_code=status.HTTP_201_CREATED)
async def criar_lote(nome: str = Body(...), descricao: Optional[str] = Body(None), user_data: dict = Depends(verify_token)):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    try:
        cur.execute(
            "INSERT INTO lotes (nome, descricao) VALUES (%s, %s) RETURNING id, nome, descricao, status",
            (nome, descricao)
        )
        lote = cur.fetchone()
        conn.commit()
        return dict(lote)
    except psycopg2.Error as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cur.close()
        conn.close()

@app.get("/api/lotes/{lote_id}", tags=["📍 Lotes e Pastos"])
async def obter_lote(lote_id: int, user_data: dict = Depends(verify_token)):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    try:
        cur.execute("SELECT * FROM lotes WHERE id = %s", (lote_id,))
        lote = cur.fetchone()
        if not lote:
            raise HTTPException(status_code=404, detail="Lote não encontrado")
        return dict(lote)
    finally:
        cur.close()
        conn.close()

@app.put("/api/lotes/{lote_id}", tags=["📍 Lotes e Pastos"])
async def atualizar_lote(lote_id: int, nome: Optional[str] = Body(None), descricao: Optional[str] = Body(None), user_data: dict = Depends(verify_token)):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    try:
        updates = []
        params = []
        if nome is not None:
            updates.append("nome = %s")
            params.append(nome)
        if descricao is not None:
            updates.append("descricao = %s")
            params.append(descricao)
        
        if not updates:
            raise HTTPException(status_code=400, detail="Nenhum campo para atualizar")
        
        params.append(lote_id)
        query = f"UPDATE lotes SET {', '.join(updates)} WHERE id = %s RETURNING *"
        cur.execute(query, params)
        lote = cur.fetchone()
        if not lote:
            raise HTTPException(status_code=404, detail="Lote não encontrado")
        conn.commit()
        return dict(lote)
    except psycopg2.Error as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cur.close()
        conn.close()

@app.delete("/api/lotes/{lote_id}", tags=["📍 Lotes e Pastos"])
async def deletar_lote(lote_id: int, user_data: dict = Depends(verify_token)):
    """Deletar lote - Apenas admin e gerente"""
    require_admin_or_gerente(user_data)

    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("UPDATE lotes SET status = 'encerrado' WHERE id = %s RETURNING id", (lote_id,))
        if cur.rowcount == 0:
            raise HTTPException(status_code=404, detail="Lote não encontrado")
        conn.commit()
        return {"message": "Lote excluído com sucesso"}
    except psycopg2.Error as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cur.close()
        conn.close()

# ===== PASTOS - CRUD COMPLETO =====
@app.post("/api/pastos", tags=["📍 Lotes e Pastos"], status_code=status.HTTP_201_CREATED)
async def criar_pasto(nome: str = Body(...), area_hectares: Optional[float] = Body(None), tipo_capim: Optional[str] = Body(None), observacoes: Optional[str] = Body(None), user_data: dict = Depends(verify_token)):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    try:
        cur.execute(
            "INSERT INTO pastos (nome, area_hectares, tipo_capim, observacoes) VALUES (%s, %s, %s, %s) RETURNING *",
            (nome, area_hectares, tipo_capim, observacoes)
        )
        pasto = cur.fetchone()
        conn.commit()
        return dict(pasto)
    except psycopg2.Error as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cur.close()
        conn.close()

@app.get("/api/pastos/{pasto_id}", tags=["📍 Lotes e Pastos"])
async def obter_pasto(pasto_id: int, user_data: dict = Depends(verify_token)):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    try:
        cur.execute("SELECT * FROM pastos WHERE id = %s", (pasto_id,))
        pasto = cur.fetchone()
        if not pasto:
            raise HTTPException(status_code=404, detail="Pasto não encontrado")
        return dict(pasto)
    finally:
        cur.close()
        conn.close()

@app.put("/api/pastos/{pasto_id}", tags=["📍 Lotes e Pastos"])
async def atualizar_pasto(pasto_id: int, nome: Optional[str] = Body(None), area_hectares: Optional[float] = Body(None), tipo_capim: Optional[str] = Body(None), observacoes: Optional[str] = Body(None), user_data: dict = Depends(verify_token)):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    try:
        updates = []
        params = []
        if nome is not None:
            updates.append("nome = %s")
            params.append(nome)
        if area_hectares is not None:
            updates.append("area_hectares = %s")
            params.append(area_hectares)
        if tipo_capim is not None:
            updates.append("tipo_capim = %s")
            params.append(tipo_capim)
        if observacoes is not None:
            updates.append("observacoes = %s")
            params.append(observacoes)
        
        if not updates:
            raise HTTPException(status_code=400, detail="Nenhum campo para atualizar")
        
        params.append(pasto_id)
        query = f"UPDATE pastos SET {', '.join(updates)} WHERE id = %s RETURNING *"
        cur.execute(query, params)
        pasto = cur.fetchone()
        if not pasto:
            raise HTTPException(status_code=404, detail="Pasto não encontrado")
        conn.commit()
        return dict(pasto)
    except psycopg2.Error as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cur.close()
        conn.close()

@app.delete("/api/pastos/{pasto_id}", tags=["📍 Lotes e Pastos"])
async def deletar_pasto(pasto_id: int, user_data: dict = Depends(verify_token)):
    """Desativar pasto (soft delete) - Apenas admin e gerente"""
    require_admin_or_gerente(user_data)

    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("UPDATE pastos SET status = 'encerrado' WHERE id = %s RETURNING id", (pasto_id,))
        if not cur.fetchone():
            raise HTTPException(404, detail="Pasto não encontrado")
        conn.commit()
        return {"message": "Pasto excluído com sucesso"}
    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(400, detail={"error": str(e)})
    finally:
        cur.close()
        conn.close()

@app.delete("/api/touros/{touro_id}", tags=["🐂 Touros"])
async def deletar_touro(touro_id: int, user_data: dict = Depends(verify_token)):
    """Deletar touro - Apenas admin e gerente"""
    require_admin_or_gerente(user_data)

    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("UPDATE touros SET ativo = false WHERE id = %s RETURNING id", (touro_id,))
        if cur.rowcount == 0:
            raise HTTPException(status_code=404, detail="Touro não encontrado")
        conn.commit()
        return {"message": "Touro excluído com sucesso"}
    except psycopg2.Error as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cur.close()
        conn.close()

@app.get("/health", tags=["⚙️ Sistema"])
def health_check():
    """Health check"""
    try:
        conn = get_db_connection()
        conn.close()
        return {"status": "healthy", "database": "connected"}
    except:
        return {"status": "unhealthy", "database": "disconnected"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
