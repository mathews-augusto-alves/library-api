FROM python:3.13-slim

# Definir diretório de trabalho
WORKDIR /app

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copiar arquivos de dependências
COPY pyproject.toml poetry.lock ./

# Instalar Poetry
RUN pip install poetry

# Configurar Poetry para não criar ambiente virtual
RUN poetry config virtualenvs.create false

# Copiar código da aplicação ANTES de instalar
COPY src/ ./src/

# Agora instalar dependências E o projeto atual
RUN poetry install --no-interaction --no-ansi

# Copiar arquivos de configuração (se existirem)
COPY .env* ./

# Expor porta
EXPOSE 8000

# Comando para executar a aplicação
CMD ["poetry", "run", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"] 