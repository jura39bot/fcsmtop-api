.PHONY: install seed dev api cli help

PYTHON ?= python3
VENV   := .venv
PIP    := $(VENV)/bin/pip
PY     := $(VENV)/bin/python

help: ## Affiche cette aide
	@grep -E '^[a-zA-Z_-]+:.*##' $(MAKEFILE_LIST) | awk 'BEGIN{FS=":.*##"}{printf "  \033[36m%-12s\033[0m %s\n",$$1,$$2}'

install: ## Crée le venv et installe les dépendances
	$(PYTHON) -m venv $(VENV)
	$(PIP) install --upgrade pip -q
	$(PIP) install -r requirements.txt -q
	@echo "✅ Dépendances installées"

seed: ## Initialise la base SQLite et charge les données
	$(PY) scripts/seed_data.py

dev: install seed ## Setup complet (venv + deps + données) — idéal après git clone
	@echo ""
	@echo "🎉 Prêt ! Lance le CLI :"
	@echo "   $(PY) cli/main.py buteurs --club FCSM"
	@echo "   $(PY) cli/main.py classement"
	@echo "   $(PY) cli/main.py form --club FCSM"
	@echo ""
	@echo "🌐 Ou l'API :"
	@echo "   $(PY) -m uvicorn api.main:app --reload"

api: ## Lance l'API FastAPI (uvicorn)
	$(PY) -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

cli: ## Lance le CLI (exemple)
	$(PY) cli/main.py buteurs --club FCSM --season 2025
