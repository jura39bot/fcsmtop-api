# fcsmtop-api ⚽🟡

**Plateforme de statistiques pour le Championnat National de football français**, avec un focus particulier sur le **FC Sochaux-Montbéliard (FCSM)**.

API REST (FastAPI) + CLI (Typer/Rich) + Dashboard web (Chart.js).

---

## Fonctionnalités

| Scope | Feature |
|-------|---------|
| National | Classement en temps réel |
| National | Top buteurs & passeurs décisifs |
| FCSM | Buteurs, passeurs, cartons |
| FCSM | Derniers résultats (N matchs) |
| FCSM | Forme récente (W/D/L) |
| CLI | Interface riche en terminal |
| Web | Dashboard avec graphiques Chart.js |
| Docker | PostgreSQL 16 + API conteneurisés |

---

## Quick Start

### ⚡ Option 1 — CLI standalone (le plus simple, après `git clone`)

```bash
git clone https://github.com/jura39bot/fcsmtop-api.git
cd fcsmtop-api

# Setup complet en une commande (venv + deps + données)
make dev

# Ou manuellement :
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python3 scripts/seed_data.py   # initialise SQLite + données

# CLI prêt !
python3 cli/main.py buteurs --club FCSM
python3 cli/main.py classement
python3 cli/main.py form --club FCSM --last 5
```

> ℹ️ La base SQLite (`fcsmtop.db`) est créée automatiquement. Aucun serveur nécessaire pour le CLI.

### Option 2 — API + Web (SQLite)

```bash
source .venv/bin/activate
uvicorn api.main:app --reload
# → http://localhost:8000      (dashboard)
# → http://localhost:8000/docs (API Swagger)
```

### Option 3 — Docker Compose (PostgreSQL)

```bash
cp .env.example .env   # adapter les mots de passe
docker compose up -d
docker compose exec api python3 scripts/seed_data.py
```

---

## API — Exemples de routes

```bash
# Classement National
GET /api/v1/national/classement?season=2025

# Top buteurs National
GET /api/v1/national/buteurs?season=2025&limit=20

# Top passeurs National
GET /api/v1/national/passeurs?season=2025

# Buteurs FCSM
GET /api/v1/clubs/FCSM/buteurs?season=2025

# Passeurs FCSM
GET /api/v1/clubs/FCSM/passeurs?season=2025

# 10 derniers matchs FCSM
GET /api/v1/clubs/FCSM/matches?last=10&season=2025

# Forme FCSM (5 derniers matchs)
GET /api/v1/clubs/FCSM/form?last=5&season=2025

# Santé API
GET /health
```

---

## CLI — fcsmtop

```bash
# Installation
pip install -e .  # (ou python cli/main.py)

# Top buteurs National
python cli/main.py buteurs --league national --season 2025

# Top buteurs FCSM
python cli/main.py buteurs --club FCSM --season 2025

# Passeurs FCSM
python cli/main.py passeurs --club FCSM

# Classement
python cli/main.py classement --season 2025

# Derniers matchs FCSM
python cli/main.py matches --club FCSM --last 10

# Forme récente
python cli/main.py form --club FCSM --last 5
```

---

## Architecture

```
fcsmtop-api/
├── api/
│   ├── main.py          # FastAPI app + CORS + static files
│   ├── models.py        # SQLAlchemy : Team, Player, Match, Goal, Assist, Card
│   ├── schemas.py       # Pydantic : ScorerOut, StandingOut, FormOut…
│   ├── database.py      # Engine async (PostgreSQL ou SQLite)
│   └── routers/
│       ├── national.py  # /api/v1/national/*
│       └── clubs.py     # /api/v1/clubs/{club}/*
├── web/
│   ├── index.html       # Dashboard National
│   ├── fcsm.html        # Page FCSM
│   └── static/
│       ├── style.css    # Thème sombre jaune/bleu
│       └── app.js       # Fetch API + Chart.js
├── cli/
│   └── main.py          # CLI Typer + Rich
├── scripts/
│   ├── seed_data.py     # Données initiales (16 équipes, 20 matchs FCSM…)
│   └── scrape_fff.py    # Scraper squelette (FFF, footmercato)
├── docker-compose.yml   # PostgreSQL 16 + API
├── Dockerfile
└── requirements.txt
```

---

## Stack technique

| Composant | Technologie |
|-----------|------------|
| API | FastAPI 0.115 + Uvicorn |
| ORM | SQLAlchemy 2.0 async |
| DB prod | PostgreSQL 16 |
| DB dev | SQLite (aiosqlite) |
| CLI | Typer + Rich |
| Frontend | HTML + Chart.js 4 |
| Docker | Docker Compose v3 |

---

## Sources de données

- **FFF Officiel** : [fff.fr/competition/national](https://www.fff.fr/competition/national/)
- **Footmercato** : classements buteurs National
- **FCSM Officiel** : [fcsochaux.fr](https://www.fcsochaux.fr/) — effectif, résultats
- **APIs tierces** : football-data.org (si disponible pour la N)

> Le scraper respecte les `robots.txt` et applique un délai de 2s entre requêtes.

---

## Contribuer

```bash
git clone https://github.com/jura39bot/fcsmtop-api.git
cd fcsmtop-api
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python scripts/seed_data.py
uvicorn api.main:app --reload
```

---

---

## 📊 Saison en cours — National 2025-2026

> Mise à jour après la **24e journée** (6 mars 2026)

### 🏆 Classement

| Pos | Club | Pts | J | V | N | D |
|-----|------|-----|---|---|---|---|
| 1 | Dijon | 43 | 24 | 13 | 4 | 7 |
| 2 | **FCSM** | **42** | **23** | **12** | **6** | **4** |
| 3 | Rouen | 42 | 24 | 12 | 6 | 6 |
| 4 | Versailles | ~36 | 24 | — | — | — |
| … | … | … | … | … | … | … |

> ⚠️ Dijon 1er aux points — Rouen et FCSM à égalité (départage : confrontations directes).  
> FCSM exempt J24 (Ajaccio exclu de la compétition).  
> Sources : footamateur.ouest-france.fr · L'Équipe · BeSoccer

---

### ⚽ Meilleurs buteurs FCSM

| Rang | Joueur | Buts | Matchs |
|------|--------|------|--------|
| 1 | Benjamin Gomel | 8 | 21 |
| 2 | Kapitbafan Djoco | 6 | 21 |
| 2 | Aymen Boutoutaou | 6 | 21 |
| 4 | Solomon Loubao | 2 | 15 |
| 4 | Boubacar Fofana | 2 | 13 |
| 4 | Elson Mendes | 2 | 19 |

### 🎯 Meilleurs passeurs FCSM

| Rang | Joueur | Passes déc. | Matchs |
|------|--------|-------------|--------|
| 1 | Dylan Tavares dos Santos | 4 | 16 |
| 2 | Benjaloud Youssouf | 2 | 14 |
| 2 | Élie N'Gatta | 2 | 14 |

> Stats après ~J21 — sources : AiScore · Footmercato · L'Est Républicain

---

### 📅 Prochains matchs FCSM

| Journée | Date | Domicile | Extérieur |
|---------|------|----------|-----------|
| J25 | 13/03/2026 | FCSM | Concarneau |
| J26 | 20/03/2026 | Aubagne | FCSM |
| J27 | 27/03/2026 | FCSM | QRM |

---

*Fait avec ❤️ et ⚽ — Allez Sochaux !*
