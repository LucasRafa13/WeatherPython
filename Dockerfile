# Usa uma imagem base leve do Python 3.9
FROM python:3.9-slim-buster

# Define o diretório de trabalho dentro do contêiner
WORKDIR /app

# Instala as dependências do sistema necessárias:
# - libpq-dev: Necessário para a biblioteca psycopg2 (conexão Python com PostgreSQL).
# - gcc: Necessário para compilar algumas dependências Python.
# Limpa o cache apt para reduzir o tamanho final da imagem.
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copia o arquivo requirements.txt primeiro para aproveitar o cache do Docker.
COPY requirements.txt .

# Instala as dependências Python listadas em requirements.txt.
RUN pip install --no-cache-dir -r requirements.txt

# Copia todo o restante do código da aplicação para o diretório de trabalho.
COPY . .

# Expõe a porta 8000, que é a porta padrão para o servidor de desenvolvimento do Django.
EXPOSE 8000

# CMD padrão (será sobrescrito pelo docker-compose)
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
