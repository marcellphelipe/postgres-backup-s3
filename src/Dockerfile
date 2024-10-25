# Use uma imagem base do Python
FROM python:3.11-slim

# Instale as dependências do PostgreSQL
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Defina o diretório de trabalho
WORKDIR /app

# Copie os arquivos de requisitos e instale as dependências do Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copie o código do aplicativo
COPY app.py .

# Comando para executar o aplicativo
CMD ["python", "app.py"]
