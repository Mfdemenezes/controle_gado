"""
Customização visual para Swagger UI
"""

SWAGGER_UI_PARAMETERS = {
    "deepLinking": True,
    "displayRequestDuration": True,
    "docExpansion": "none",
    "filter": True,
    "showCommonExtensions": True,
    "syntaxHighlight.theme": "monokai"
}

CUSTOM_CSS = """
/* Tema customizado para o Swagger UI */
.swagger-ui .topbar { 
    background-color: #2c5530; 
    border-bottom: 3px solid #4a8a4f;
}

.swagger-ui .info .title {
    color: #2c5530;
    font-size: 36px;
    font-weight: bold;
}

.swagger-ui .info .description {
    font-size: 16px;
    line-height: 1.6;
}

.swagger-ui .opblock.opblock-post {
    background: rgba(76, 175, 80, .1);
    border-color: #4CAF50;
}

.swagger-ui .opblock.opblock-get {
    background: rgba(33, 150, 243, .1);
    border-color: #2196F3;
}

.swagger-ui .opblock.opblock-put {
    background: rgba(255, 152, 0, .1);
    border-color: #FF9800;
}

.swagger-ui .opblock.opblock-delete {
    background: rgba(244, 67, 54, .1);
    border-color: #F44336;
}

.swagger-ui .btn.execute {
    background-color: #4CAF50;
    border-color: #4CAF50;
}

.swagger-ui .btn.execute:hover {
    background-color: #45a049;
}

.swagger-ui .scheme-container {
    background: #f5f5f5;
    box-shadow: 0 2px 4px rgba(0,0,0,.1);
}
"""

API_DESCRIPTION = """
## 🐮 Sistema de Controle de Gado de Corte

API REST completa para gerenciamento de rebanho bovino com funcionalidades de:

### 📊 Funcionalidades Principais

* **Autenticação** - Sistema de login com tokens JWT
* **Gestão de Animais** - Cadastro completo com brinco, raça, peso, lote
* **Controle de Pesagens** - Registro histórico com cálculo automático de GMD
* **Sanidade** - Gestão de vacinas, vermífugos e medicamentos
* **Reprodução** - Controle de cio, cobertura e gestação
* **Movimentações** - Transferência entre pastos e lotes
* **Relatórios** - Performance individual e resumo do rebanho

### 🔐 Autenticação

Todas as rotas (exceto `/health` e `/`) requerem autenticação via Bearer Token.

**Para obter o token:**
1. Faça login em `/api/auth/login` com email e senha
2. Copie o `token` retornado
3. Clique em **Authorize** (cadeado) no topo
4. Cole o token e clique em **Authorize**

### 📝 Exemplos de Uso

Veja os exemplos em cada endpoint. Todos os campos obrigatórios estão marcados com *.

---

**Desenvolvido com FastAPI + PostgreSQL**  
Versão: 1.0.0
"""

TAGS_METADATA = [
    {
        "name": "Autenticação",
        "description": "Endpoints para login e logout no sistema"
    },
    {
        "name": "Animais",
        "description": "Gestão completa do rebanho - cadastro, consulta, edição"
    },
    {
        "name": "Pesagens",
        "description": "Registro e consulta de pesagens com cálculo de GMD"
    },
    {
        "name": "Sanidade",
        "description": "Controle de vacinas, vermífugos e tratamentos"
    },
    {
        "name": "Movimentações",
        "description": "Transferências entre pastos e lotes"
    },
    {
        "name": "Lotes e Pastos",
        "description": "Consulta de lotes e pastos cadastrados"
    },
    {
        "name": "Relatórios",
        "description": "Resumos e análises de performance do rebanho"
    },
    {
        "name": "Sistema",
        "description": "Health check e informações do sistema"
    }
]
