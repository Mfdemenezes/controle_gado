FROM python:3.11-slim

# Definir diretório de trabalho
WORKDIR /app

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements
COPY requirements.txt .

# Instalar dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código da aplicação
COPY api_gado.py .
COPY .env* ./

# Expor porta
EXPOSE 8000

# Comando de inicialização
CMD ["uvicorn", "api_gado:app", "--host", "0.0.0.0", "--port", "8000"]
