# Career-OS Makefile
# Verwende `make help` fuer eine Uebersicht aller verfuegbaren Befehle.

.DEFAULT_GOAL := help

.PHONY: help setup test lint format docker-up docker-down migrate seed

help: ## Zeigt diese Hilfemeldung an
	@echo "Career-OS - Verfuegbare Make-Befehle:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'
	@echo ""

setup: ## Richtet die Entwicklungsumgebung ein
	@echo "TODO: Virtuelle Umgebung erstellen und Abhaengigkeiten installieren"

test: ## Fuehrt alle Tests aus
	@echo "TODO: pytest ausfuehren"

lint: ## Prueft den Code auf Stilfehler
	@echo "TODO: ruff und mypy ausfuehren"

format: ## Formatiert den Quellcode
	@echo "TODO: black und ruff --fix ausfuehren"

docker-up: ## Startet alle Docker-Container
	@echo "TODO: docker compose up -d"

docker-down: ## Stoppt alle Docker-Container
	@echo "TODO: docker compose down"

migrate: ## Fuehrt Datenbank-Migrationen aus
	@echo "TODO: Alembic-Migrationen ausfuehren"

seed: ## Befuellt die Datenbank mit Testdaten
	@echo "TODO: Seed-Skript ausfuehren"
