up:
	docker compose -f local.yml up $(filter-out $@,$(MAKECMDGOALS))

build:
	docker compose -f local.yml build $(filter-out $@,$(MAKECMDGOALS))

run:
	docker compose -f local.yml run $(filter-out $@,$(MAKECMDGOALS))

restart:
	docker compose -f local.yml restart $(filter-out $@,$(MAKECMDGOALS))

stop:
	docker compose -f local.yml stop $(filter-out $@,$(MAKECMDGOALS))

bash:
	docker compose -f local.yml exec django /entrypoint bash

createsuperuser:
	docker-compose -f local.yml exec django /entrypoint ./manage.py createsuperuser

shell:
	docker-compose -f local.yml exec django /entrypoint ./manage.py shell_plus

makemigrations:
	docker compose -f local.yml run --rm django python manage.py makemigrations $(filter-out $@,$(MAKECMDGOALS))

migrate:
	docker compose -f local.yml run --rm django python manage.py migrate $(filter-out $@,$(MAKECMDGOALS))

showmigrations:
	docker compose -f local.yml run --rm django python manage.py showmigrations $(filter-out $@,$(MAKECMDGOALS))

sqlmigrate:
	docker compose -f local.yml run --rm django python manage.py sqlmigrate $(filter-out $@,$(MAKECMDGOALS))

makemessages:
	docker compose -f local.yml run --rm django python manage.py makemessages --no-location -l ar

compilemessages:
	docker compose -f local.yml run --rm django python manage.py compilemessages

urls:
	docker compose -f local.yml run django python manage.py show_urls

logs:
	docker compose -f local.yml logs -f $(filter-out $@,$(MAKECMDGOALS))

test:
	docker compose -f local.yml exec django /entrypoint python manage.py test --settings=config.settings.test $(filter-out $@,$(MAKECMDGOALS))

down:
	docker compose -f local.yml down $(filter-out $@,$(MAKECMDGOALS))

destroy:
	docker compose -f local.yml down -v
