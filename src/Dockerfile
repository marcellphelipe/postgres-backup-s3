# Use a imagem oficial do PostgreSQL 16
FROM postgres:16

# Instale as dependências necessárias
RUN apt-get update && apt-get install -y \
    python3 \
    python3-venv \
    python3-pip \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Defina o diretório de trabalho
WORKDIR /app

# Copie os arquivos de requisitos e instale as dependências do Python
COPY requirements.txt .

# Crie um ambiente virtual
RUN python3 -m venv /opt/venv

# Ative o ambiente virtual e instale as bibliotecas Python necessárias
RUN /opt/venv/bin/pip install --no-cache-dir -r requirements.txt

# Copie o código do aplicativo
COPY app.py .

# Comando para executar o aplicativo
CMD ["python", "app.py"]
