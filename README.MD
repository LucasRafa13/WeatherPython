# 🌦️ Projeto Weather Records Manager

Este projeto é uma aplicação Django que consome dados da [WeatherAPI](https://www.weatherapi.com/) e os armazena em banco de dados. Ele expõe endpoints para cadastro e listagem de registros meteorológicos. O projeto é totalmente dockerizado para facilitar o uso local e em produção.

---

## 🚀 Começando

### ✅ Pré-requisitos

Certifique-se de ter as seguintes ferramentas instaladas:

- [Docker](https://docs.docker.com/get-docker/)
- Docker Compose
- [Git](https://git-scm.com/)

---

## 📦 Clonando o Repositório

```bash
git clone https://github.com/seu-usuario/weatherapi-python.git
cd weatherapi-python
```

---

## ⚙️ Configuração do Ambiente

Crie um arquivo `.env` na raiz do projeto com o seguinte conteúdo:

```env
# Variáveis do banco de dados PostgreSQL
POSTGRES_DB=weather
POSTGRES_USER=weather_user
POSTGRES_PASSWORD=weather_pass

# Configuração do Django
DATABASE_NAME=weather
DATABASE_USER=weather_user
DATABASE_PASSWORD=weather_pass
DATABASE_HOST=db
DATABASE_PORT=5432

# Chave da API WeatherAPI
WEATHER_API_KEY=sua_chave_aqui
```

⚠️ **Importante:** o arquivo `.env` contém dados sensíveis e já está listado no `.gitignore`.

---

## 🐳 Executando com Docker Compose

### 1. Suba os containers

```bash
docker compose up --build -d
```

### 2. Aplique as migrações

```bash
docker compose exec web python manage.py migrate
```

### 3. Crie um superusuário

```bash
docker compose exec web python manage.py createsuperuser
```

---

## 🌐 Endpoints Disponíveis

- Cadastro manual: [http://localhost:8000/](http://localhost:8000/)
- Listar dados meteorológicos: [http://localhost:8000/api/weather-records/](http://localhost:8000/api/weather-records/)

---

## 🔁 Desenvolvimento com Hot Reload

Para ver os logs em tempo real:

```bash
docker compose logs -f web
```

---

## 🧹 Limpeza

Para remover containers e volumes criados:

```bash
docker compose down -v
```

---

## 📄 Autor


Este Foi desenvolvido por [https://github.com/LucasRafa13](https://github.com/LucasRafa13)