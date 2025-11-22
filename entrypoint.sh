#!/bin/sh

echo "🚀 Aguardando banco de dados..."
while ! nc -z $POSTGRES_HOST 5432; do
  sleep 1
done

echo "✔ Banco disponível!"

echo "📦 Aplicando migrations..."
python manage.py migrate

echo "🎉 Iniciando aplicação..."
exec "$@"
