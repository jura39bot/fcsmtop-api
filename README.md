# fcsmtop-api ⚽🟡

**Plateforme de statistiques pour le football français** (National + Ligue 2), avec un focus particulier sur le **FC Sochaux-Montbéliard (FCSM)**.

API REST (FastAPI) + CLI (Typer/Rich) + Dashboard web (Chart.js).

---

## Compétitions couvertes

| Saison | Compétition | Statut | Dossier de données |
|--------|-------------|--------|--------------------|
| 2025-2026 | Championnat National | ✅ terminée (FCSM promu L2) | `data/national/2025-2026/` |
| 2026-2027 | Ligue 2 BKT | 🟡 en cours (J6) | `data/ligue2/2026-2027/` |

---

## Fonctionnalités

| Scope | Feature |
|-------|---------|
| National/Ligue 2 | Classement en temps réel |
| National/Ligue 2 | Top buteurs & passeurs décisifs |
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
├── data/
│   ├── national/2025-2026/   # Saison National terminée (FCSM 2e, promu L2)
│   │   ├── matches.csv      # 32 journées + matches N1/J8 Ajaccio forfait
│   │   ├── players.json     # Effectif FCSM fin de saison
│   │   ├── scorers.json     # Top buteurs FCSM + National
│   │   ├── standings.json   # Classement final 18 clubs (Dijon 1er, FCSM 2e)
│   │   └── season_summary.json  # Bilan, manager Hognon, trophées, promotion
│   └── ligue2/2026-2027/    # Saison L2 en cours (J6)
│       ├── matches.csv      # 34 journées, FCSM J1-J6 joués
│       ├── players.json     # Effectif FCSM L2 (recrues : Clairicia)
│       ├── scorers.json     # Top buteurs L2 + FCSM scorers
│       ├── standings.json   # Classement après J5 (+ FCSM J6 = 6e/9 pts)
│       └── season_summary.json  # Contexte L2, manager, calendrier, format
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
- **LFP Officiel** : [lfp.fr](https://www.lfp.fr/) — Ligue 2 BKT, classement et calendrier
- **Footmercato / FBref / ladepeche.fr / L'Est Républicain** : classements, buteurs, calendriers
- **FCSM Officiel** : [fcsochaux.fr](https://www.fcsochaux.fr/) — effectif, résultats
- **APIs tierces** : football-data.org, worldfootball.net

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

## 📊 Saison 2025-2026 — Championnat National (terminée)

> **FCSM 2e (58 pts)** — promotion en Ligue 2 avec Dijon FCO (champion, 65 pts).  
> Saison terminée le 16/05/2026 (32 journées). AC Ajaccio exclu (forfait général).

### 🏆 Classement final

| Pos | Club | Pts | J | V | N | D | Diff |
|-----|------|-----|---|---|---|---|------|
| 1 | Dijon FCO | 65 | 32 | 18 | 11 | 3 | +27 |
| 2 | **FCSM** | **58** | **32** | **16** | **10** | **6** | **+25** |
| 3 | Le Mans | 58 | 32 | 16 | 10 | 6 | +17 |

> Manager : **Vincent Hognon**. Nomination aux Trophées National 2026 meilleur entraîneur.  
> Gomel (12 buts) et Boutoutaou (6) cités pour le trophée meilleur joueur.  
> Sources : FFF officiel + classement vérifié.

➡️ Détail complet : `data/national/2025-2026/`

---

## 🟡 Saison 2026-2027 — Ligue 2 BKT (en cours)

> **Snapshot au 13/09/2026** — J6 jouée (FCSM 1-0 Nantes, but Gomel 61e).  
> FCSM **6e (9 pts, 2V-3N-1D)** sur 18 clubs. Leader : Saint-Étienne 15 pts.

### 🏆 Classement (après J5 — derniers résultats complets, FCSM J6 inclus)

| Pos | Club | Pts | J | V | N | D | Diff |
|-----|------|-----|---|---|---|---|------|
| 1 | Saint-Étienne | 15 | 5 | 5 | 0 | 0 | +12 |
| 2 | Annecy | 10 | 5 | 3 | 1 | 1 | +2 |
| 3 | Reims | 9 | 5 | 2 | 3 | 0 | +5 |
| 4 | Metz | 9 | 5 | 2 | 3 | 0 | +4 |
| 5 | Montpellier | 8 | 5 | 2 | 2 | 1 | 0 |
| 6 | **Sochaux** | **9** | **6** | **2** | **3** | **1** | **-1** |
| 7 | Red Star | 8 | 5 | 2 | 2 | 1 | -1 |
| 18 | Nantes | 1 | 5 | 0 | 1 | 4 | -6 |

> Manager : **Vincent Hognon** (continuité après promotion).  
> Recrue L2 : Mathias Clairicia (ex-Bochum) — buteur décisif dès J5.  
> Sources : FBref + ladepeche.fr + LFP + L'Est Républicain, vérifié 2026-09-13 15:45 GMT+2.

### ⚽ Buteurs FCSM en L2

| Joueur | Buts | Match |
|--------|------|-------|
| Boubacar Fofana | 1 | J3 vs Guingamp (1-0, 14e) |
| Mathias Clairicia | 1 | J5 à Pau (1-1, égalisation à 10 contre 11) |
| Benjamin Gomel | 1 | J6 vs Nantes (1-0, 61e) |

### 📅 Prochains matchs FCSM

| J | Date | Domicile | Extérieur |
|---|------|----------|-----------|
| 7 | 18/09/2026 | Laval | FCSM |
| 8 | 09/10/2026 | FCSM | Boulogne |
| 9 | 17/10/2026 | Metz | FCSM |

➡️ Détail complet : `data/ligue2/2026-2027/`

---

*Fait avec ❤️ et ⚽ — Allez Sochaux !*
