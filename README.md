# fcsmtop-api ⚽🟡

**Plateforme de statistiques pour le football français** (National + Ligue 2), avec un focus particulier sur le **FC Sochaux-Montbéliard (FCSM)**.

API REST (FastAPI) + CLI (Typer/Rich) + Dashboard web (Chart.js).

---

## Compétitions couvertes

| Saison | Compétition | Statut | Dossier de données |
|--------|-------------|--------|--------------------|
| 2025-2026 | Championnat National | ✅ terminée (FCSM promu L2) | `data/national/2025-2026/` |
| 2026-2027 | Ligue 2 BKT | 🟡 en cours (J10, J11 reportée au 02/11) | `data/ligue2/2026-2027/` |

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
│   └── ligue2/2026-2027/    # Saison L2 en cours (J10, J11 reportée)
│       ├── matches.csv      # 34 journées, FCSM J1-J10 joués
│       ├── players.json     # Effectif FCSM L2 (recrues : Clairicia)
│       ├── scorers.json     # Top buteurs L2 + FCSM scorers
│       ├── standings.json   # Classement après J10 (+ 5 matches de J11)
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

> **Snapshot au 30/10/2026** — J10 complète + 5 matches de J11 joués le 30/10.  
> FCSM **13e (11 pts, 2V-5N-3D)** sur 18 clubs, 3 matches sans victoire. Leader : Saint-Étienne 25 pts.  
> ⚠️ **J11 Reims - FCSM reportée au lundi 02/11/2026 à 20h45** (Stade Auguste-Delaune, beIN SPORTS 1), à la demande de la préfecture de la Marne.

### 🏆 Classement (après J10 + matches du 30/10)

| Pos | Club | Pts | J | V | N | D | Diff |
|-----|------|-----|---|---|---|---|------|
| 1 | AS Saint-Étienne | 25 | 10 | 8 | 1 | 1 | +15 |
| 2 | Montpellier HSC | 21 | 10 | 6 | 3 | 1 | +7 |
| 3 | Pau FC | 20 | 11 | 6 | 2 | 3 | +5 |
| 4 | AS Nancy Lorraine | 19 | 10 | 6 | 1 | 3 | +4 |
| 5 | Stade de Reims | 18 | 10 | 4 | 6 | 0 | +8 |
| 6 | Red Star FC | 17 | 10 | 5 | 2 | 3 | +1 |
| 7 | FC Annecy | 16 | 10 | 5 | 1 | 4 | +2 |
| 8 | Dijon FCO | 15 | 11 | 4 | 3 | 4 | +1 |
| 9 | FC Metz | 14 | 11 | 3 | 5 | 3 | 0 |
| 10 | Rodez Aveyron Football | 13 | 11 | 4 | 1 | 6 | -5 |
| 11 | USL Dunkerque | 12 | 11 | 3 | 3 | 5 | -3 |
| 12 | En Avant Guingamp | 11 | 10 | 3 | 2 | 5 | -2 |
| 13 | **Sochaux** | 11 | 10 | 2 | 5 | 3 | -4 |
| 14 | US Boulogne CO | 10 | 11 | 1 | 7 | 3 | -1 |
| 15 | FC Nantes | 9 | 11 | 2 | 3 | 6 | -6 |
| 16 | Stade Lavallois | 9 | 11 | 2 | 3 | 6 | -7 |
| 17 | Clermont Foot 63 | 8 | 11 | 0 | 8 | 3 | -5 |
| 18 | Grenoble Foot 38 | 8 | 11 | 2 | 2 | 7 | -10 |

> Manager : **Vincent Hognon** (continuité après promotion).  
> Recrue L2 : Mathias Clairicia (ex-Bochum).  
> Sources : FC Sochaux officiel + L'Union / L'Est Républicain / footeo / Ouest-France, vérifié 2026-10-30 23h00 GMT+1.

### ⚽ Buteurs FCSM en L2

| Joueur | Buts | Match |
|--------|------|-------|
| Benjamin Gomel | 3 | J6 vs Nantes (61e), J8 vs Boulogne (8e), J9 à Metz (46e) |
| Boubacar Fofana | 1 | J3 vs Guingamp (1-0, 14e) |
| Mathias Clairicia | 1 | J5 à Pau (1-1) |
| Samy Baghdadi | 1 | J7 à Laval (1-1, 79e) |
| Deedson Louicius | 1 | J9 à Metz (3-2, 90+1) |
| Honoré Bayanginisa | 1 | J10 vs Annecy (1-3, 65e) |

### 📅 Prochains matchs FCSM

| J | Date | Domicile | Extérieur |
|---|------|----------|-----------|
| 11 | 02/11/2026 | Reims | FCSM |
| 12 | 06/11/2026 | Nancy | FCSM |
| 13 | 20/11/2026 | FCSM | Dunkerque |

➡️ Détail complet : `data/ligue2/2026-2027/`

---

*Fait avec ❤️ et ⚽ — Allez Sochaux !*
