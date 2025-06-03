# Usa uma imagem base leve do Python 3.9
FROM python:3.9-slim-buster

# Define o diretório de trabalho dentro do contêiner.
# Todos os comandos subsequentes (COPY, RUN, CMD) serão executados a partir deste diretório.
WORKDIR /app

# Instala as dependências do sistema operacional necessárias:
# - netcat-traditional: Usado pelo script 'wait-for-it.sh' para verificar a disponibilidade do banco de dados.
# - libpq-dev: Necessário para a biblioteca 'psycopg2' (conector Python para PostgreSQL) poder ser compilada e instalada.
# - gcc: Compilador C, também necessário para 'psycopg2'.
# 'rm -rf /var/lib/apt/lists/*' limpa o cache do apt para manter a imagem Docker pequena.
RUN apt-get update && apt-get install -y --no-install-recommends \
    netcat-traditional \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copia o arquivo 'requirements.txt' para o contêiner.
# Fazemos isso antes de copiar o restante do código para aproveitar o cache do Docker.
# Se suas dependências Python não mudarem, esta etapa não será reconstruída em futuras builds.
COPY requirements.txt .

# Instala as dependências Python listadas em 'requirements.txt'.
# É CRUCIAL que 'Django' e 'psycopg2-binary' (ou 'psycopg2') estejam neste arquivo.
# '--no-cache-dir' evita a criação de cache de pacotes, o que reduz o tamanho final da imagem.
RUN pip install --no-cache-dir -r requirements.txt

# Copia todo o restante do código da sua aplicação para o diretório de trabalho '/app' no contêiner.
# Isso inclui seu 'manage.py', suas apps Django, seu arquivo 'settings.py', etc.
# É essencial que seu 'manage.py' esteja na mesma pasta que este Dockerfile localmente.
COPY . .

# Copia o script 'wait-for-it.sh' para um local no PATH do contêiner e o torna executável.
# Este script é usado para garantir que o banco de dados esteja completamente pronto antes da aplicação iniciar.
COPY wait-for-it.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/wait-for-it.sh

# Expõe a porta 8000. Esta é a porta padrão que o servidor de desenvolvimento do Django usa.
# Certifique-se de que esta porta corresponde à porta mapeada no seu 'docker-compose.yml'.
EXPOSE 8000

# Define o comando que será executado quando o contêiner for iniciado.
# 1. 'wait-for-it.sh db 5432': Executa o script que espera pelo serviço 'db' (PostgreSQL) na porta 5432.
#    - 'db' e '5432' são passados como ARGUMENTOS SEPARADOS, o que é essencial para o 'wait-for-it.sh' funcionar corretamente.
# 2. '--': Este delimitador indica que os argumentos que seguem são para o comando subsequente, e não para o 'wait-for-it.sh'.
# 3. 'python manage.py runserver 0.0.0.0:8000': O comando que inicia o servidor de desenvolvimento do Django.
#    - '0.0.0.0': Faz com que o servidor Django ouça em todas as interfaces de rede dentro do contêiner, tornando-o acessível via a porta mapeada do Docker.
#    - '8000': A porta em que o Django irá rodar.
CMD wait-for-it.sh db 5432 -- python manage.py runserver 0.0.0.0:8000

