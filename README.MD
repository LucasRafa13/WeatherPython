# 🗂️ Projeto Sympla Events Manager

Este projeto é uma aplicação Django que interage com a [API da Sympla](https://developers.sympla.com.br/api-doc/) para importar, armazenar e expor eventos via REST. Ele utiliza Docker e Docker Compose para facilitar o desenvolvimento e implantação.

---

## 🚀 Começando

Siga os passos abaixo para rodar o projeto localmente.

### ✅ Pré-requisitos

Certifique-se de ter as seguintes ferramentas instaladas:

- [Docker](https://docs.docker.com/get-docker/)
- Docker Compose (já incluso no Docker Desktop)
- [Git](https://git-scm.com/)

---

## 📦 Clonando o Repositório

```bash
git clone https://github.com/LucasRafa13/SymplaPython
cd sympla-python
```

---

## ⚙️ Configuração do Ambiente

Crie um arquivo `.env` na raiz do projeto com o seguinte conteúdo ou descomente o .env.example e renomeie para .env:

```env
# Variáveis para o banco de dados PostgreSQL
POSTGRES_DB=sympla
POSTGRES_USER=sympla
POSTGRES_PASSWORD=sympla

# Variáveis para a conexão do Django com o PostgreSQL (referenciam as do banco)
DATABASE_NAME=sympla
DATABASE_USER=sympla
DATABASE_PASSWORD=sympla
DATABASE_HOST=db  # O nome do serviço do banco de dados no docker-compose
DATABASE_PORT=5432

# Token da API Sympla
SYMPLA_TOKEN=seu_token_aqui
```

⚠️ **Importante:** o `.env` contém informações sensíveis e não deve ser versionado. Ele já está incluso no `.gitignore`.

---

## 🐳 Executando com Docker Compose

### 1. Construir e iniciar os containers

```bash
docker compose up --build -d
```

### 2. Aplicar migrações do banco de dados

```bash
docker compose exec web python manage.py migrate
```

### 3. Criar superusuário Django

```bash
docker compose exec web python manage.py createsuperuser
```

---

## 🌐 Acessos

- Aplicação: http://localhost:8000/
- Admin Django: http://localhost:8000/admin/
- API de eventos: http://localhost:8000/api/events/

---

## 🔁 Desenvolvimento com hot reload

O serviço web está configurado para recarregar automaticamente ao salvar arquivos Python:

```bash
docker compose logs -f web
```

---

## 🧹 Limpeza

Para parar e remover os containers, redes e volumes:

```bash
docker compose down -v
```

---
## 📄 Autor

Este projeto foi inteiramente desenvolvido por [Lucas R A Lima](https://github.com/LucasRafa13)