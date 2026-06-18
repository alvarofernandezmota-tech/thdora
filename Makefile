.PHONY: up down logs smoke rebuild shell-bot shell-api ps pull

## Arrancar todos los servicios (rebuild si hay cambios)
up:
	docker compose up -d --build

## Parar todos los servicios
down:
	docker compose down

## Ver logs del bot en tiempo real
logs:
	docker compose logs -f bot

## Ver logs de la API en tiempo real
logs-api:
	docker compose logs -f thdora

## Ver estado de los contenedores
ps:
	docker compose ps

## Ejecutar smoke test antes de arrancar
smoke:
	docker compose run --rm bot python scripts/smoke_test.py

## Rebuild limpio sin cache
rebuild:
	docker compose build --no-cache

## Rebuild limpio + arrancar
fresh:
	docker compose down
	docker compose build --no-cache
	docker compose up -d

## Entrar al contenedor del bot
shell-bot:
	docker compose exec bot bash

## Entrar al contenedor de la API
shell-api:
	docker compose exec thdora bash

## Actualizar código y reiniciar
pull:
	git pull origin main
	docker compose restart bot

## Secuencia completa de arranque desde cero
start-fresh: pull smoke fresh logs
