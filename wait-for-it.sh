#!/bin/bash
# wait-for-it.sh

set -e

# host: O nome do host do serviço (ex: db)
# port: A porta do serviço (ex: 5432)
# cmd: O comando a ser executado depois que o host:port estiver disponível
host="$1"
port="$2"
shift 2 # Remove os dois primeiros argumentos (host e port)
cmd="$@" # O resto dos argumentos é o comando a ser executado

echo "Waiting for PostgreSQL at $host:$port..."

# Loop até que o netcat consiga se conectar ao host:port
while ! nc -z "$host" "$port"; do
  echo "PostgreSQL is unavailable - sleeping"
  sleep 1
done

echo "PostgreSQL is up - executing command"
# Executa o comando passado como argumento (o 'flask run' neste caso)
exec $cmd