# Makefile para facilitar comandos Docker

.PHONY: help build up down restart logs shell migrate collectstatic createsuperuser test clean backup restore

help:
	@echo "Comandos disponíveis:"
	@echo "  make build          - Build das imagens Docker"
	@echo "  make up             - Iniciar containers (desenvolvimento)"
	@echo "  make up-prod        - Iniciar containers (produção)"
	@echo "  make down           - Parar e remover containers"
	@echo "  make restart        - Reiniciar containers"
	@echo "  make logs           - Ver logs de todos os serviços"
	@echo "  make logs-web       - Ver logs do Django"
	@echo "  make logs-nginx     - Ver logs do Nginx"
	@echo "  make logs-db        - Ver logs do PostgreSQL"
	@echo "  make shell          - Abrir shell no container web"
	@echo "  make migrate        - Executar migrações"
	@echo "  make makemigrations - Criar novas migrações"
	@echo "  make collectstatic  - Coletar arquivos estáticos"
	@echo "  make createsuperuser- Criar superusuário"
	@echo "  make test           - Executar testes"
	@echo "  make clean          - Limpar containers e volumes"
	@echo "  make backup         - Backup do banco de dados"
	@echo "  make restore        - Restaurar backup do banco"
	@echo "  make ps             - Status dos containers"

build:
	docker-compose build

up:
	docker-compose up -d
	@echo "Aplicação disponível em http://localhost"

up-prod:
	docker-compose -f docker-compose.prod.yml up -d
	@echo "Aplicação em produção disponível em http://localhost"

down:
	docker-compose down

restart:
	docker-compose restart

logs:
	docker-compose logs -f

logs-web:
	docker-compose logs -f web

logs-nginx:
	docker-compose logs -f nginx

logs-db:
	docker-compose logs -f db

shell:
	docker-compose exec web bash

shell-db:
	docker-compose exec db psql -U $${POSTGRES_USER:-newcars_user} -d $${POSTGRES_DB:-newcars_db}

migrate:
	docker-compose exec web python manage.py migrate

makemigrations:
	docker-compose exec web python manage.py makemigrations

collectstatic:
	docker-compose exec web python manage.py collectstatic --noinput

createsuperuser:
	docker-compose exec web python manage.py createsuperuser

test:
	docker-compose exec web python manage.py test

ps:
	docker-compose ps

clean:
	docker-compose down -v
	docker system prune -f

backup:
	@mkdir -p backups
	docker-compose exec db pg_dump -U $${POSTGRES_USER:-newcars_user} $${POSTGRES_DB:-newcars_db} > backups/backup_$$(date +%Y%m%d_%H%M%S).sql
	@echo "Backup criado em backups/"

restore:
	@echo "Restaurando último backup..."
	docker-compose exec -T db psql -U $${POSTGRES_USER:-newcars_user} $${POSTGRES_DB:-newcars_db} < $$(ls -t backups/*.sql | head -1)

rebuild:
	docker-compose down
	docker-compose build --no-cache
	docker-compose up -d

prune:
	docker system prune -a -f --volumes
