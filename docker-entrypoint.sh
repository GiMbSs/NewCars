#!/bin/bash
set -e

echo "==> Aguardando banco de dados..."
# Aguarda o PostgreSQL estar pronto usando Python
until python << END
import sys
import psycopg
try:
    conn = psycopg.connect(
        dbname="${POSTGRES_DB}",
        user="${POSTGRES_USER}",
        password="${POSTGRES_PASSWORD}",
        host="${POSTGRES_HOST}",
        port="${POSTGRES_PORT}",
        connect_timeout=5
    )
    conn.close()
    sys.exit(0)
except Exception:
    sys.exit(1)
END
do
  echo "Aguardando PostgreSQL iniciar..."
  sleep 2
done
echo "==> Banco de dados disponível!"

echo "==> Coletando arquivos estáticos..."
python manage.py collectstatic --noinput --clear

echo "==> Executando migrações..."
python manage.py migrate --noinput

echo "==> Criando superusuário (se não existir)..."
python manage.py shell << END
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('Superusuário criado: admin/admin123')
else:
    print('Superusuário já existe')
END

echo "==> Iniciando aplicação..."
exec "$@"
