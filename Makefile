ifneq ("$(wildcard .env)","")
    include .env
    export $(shell sed 's/=.*//' .env)
else
endif

WORKDIR := $(shell pwd)
.ONESHELL:
.EXPORT_ALL_VARIABLES:
DOCKER_BUILDKIT=1


help: ## Display help message
	@echo "Please use \`make <target>' where <target> is one of"
	@perl -nle'print $& if m{^[\.a-zA-Z_-]+:.*?## .*$$}' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m  %-25s\033[0m %s\n", $$1, $$2}'

build_and_run: ## Run and build application
	 docker compose up -d --build 

run_app:  ## Run application
	docker compose up -d

drop_all_containers: ## Drop all containers
	docker compose down -v --remove-orphans

create_migrations: run_app ## Create migration. Usage `make create_migrations m="migration message"`
ifeq ($(strip $(m)),)
	$(error 'Migration should contains message. Please use make create_migrations m="some message here"')
endif
	docker compose exec api alembic revision --autogenerate -m "$(m)"

migrate: run_app ## Apply migrations
	docker compose exec api alembic upgrade head

undo_last_migration: run_app
	docker compose exec api alembic downgrade -1


open_shell: ## Open shell to the app container
	docker compose exec api bash

open_log: ## Open api log
	docker compose logs -f api

