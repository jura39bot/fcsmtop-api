"""Requêtes DB directes pour le CLI standalone (pas besoin de serveur API)."""
import asyncio
import os
import sys

# Ajoute la racine du projet au path pour les imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///./fcsmtop.db")

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from api.database import AsyncSessionLocal, init_db
from api import models


def run(coro):
    """Helper pour lancer une coroutine depuis du code synchrone."""
    return asyncio.run(coro)


async def _ensure_db():
    """Initialise la DB et seed si vide."""
    await init_db()
    async with AsyncSessionLocal() as db:
        count = await db.scalar(select(func.count(models.Team.id)))
        if count == 0:
            from scripts.seed_data import seed
            print("📦 Première utilisation — initialisation des données...")
            await seed()
            print()


async def _buteurs_national(season: str, limit: int) -> list[dict]:
    await _ensure_db()
    async with AsyncSessionLocal() as db:
        stmt = (
            select(
                models.Player,
                func.count(models.Goal.id).filter(models.Goal.own_goal.is_(False)).label("goals"),
                func.count(models.Goal.id).filter(models.Goal.penalty.is_(True)).label("penalties"),
                func.count(models.Assist.id).label("assists"),
            )
            .join(models.Goal, models.Goal.scorer_id == models.Player.id)
            .join(models.Match, models.Match.id == models.Goal.match_id)
            .outerjoin(
                models.Assist,
                (models.Assist.player_id == models.Player.id) &
                (models.Assist.match_id == models.Match.id),
            )
            .where(models.Match.season == season, models.Goal.own_goal.is_(False))
            .group_by(models.Player.id)
            .order_by(func.count(models.Goal.id).filter(models.Goal.own_goal.is_(False)).desc())
            .limit(limit)
        )
        rows = (await db.execute(stmt)).all()
        result = []
        for i, (p, goals, pens, assists) in enumerate(rows):
            team = await db.get(models.Team, p.team_id)
            result.append({
                "rank": i + 1, "full_name": p.full_name,
                "team": team.name if team else "", "team_short": team.short_name if team else "",
                "goals": goals, "penalties": pens, "assists": assists,
            })
        return result


async def _buteurs_club(club_short: str, season: str) -> list[dict]:
    await _ensure_db()
    async with AsyncSessionLocal() as db:
        team_row = await db.execute(select(models.Team).where(models.Team.short_name == club_short.upper()))
        team = team_row.scalar_one_or_none()
        if not team:
            return []
        stmt = (
            select(
                models.Player,
                func.count(models.Goal.id).filter(models.Goal.own_goal.is_(False)).label("goals"),
                func.count(models.Goal.id).filter(models.Goal.penalty.is_(True)).label("penalties"),
            )
            .join(models.Goal, models.Goal.scorer_id == models.Player.id)
            .join(models.Match, models.Match.id == models.Goal.match_id)
            .where(models.Player.team_id == team.id, models.Match.season == season, models.Goal.own_goal.is_(False))
            .group_by(models.Player.id)
            .order_by(func.count(models.Goal.id).filter(models.Goal.own_goal.is_(False)).desc())
        )
        rows = (await db.execute(stmt)).all()
        return [
            {"rank": i+1, "full_name": p.full_name, "team": team.name, "team_short": team.short_name,
             "goals": g, "penalties": pen, "assists": 0}
            for i, (p, g, pen) in enumerate(rows)
        ]


async def _passeurs(club_short: str | None, season: str, limit: int) -> list[dict]:
    await _ensure_db()
    async with AsyncSessionLocal() as db:
        stmt = (
            select(models.Player, func.count(models.Assist.id).label("assists"))
            .join(models.Assist, models.Assist.player_id == models.Player.id)
            .join(models.Match, models.Match.id == models.Assist.match_id)
            .where(models.Match.season == season)
        )
        if club_short:
            team_row = await db.execute(select(models.Team).where(models.Team.short_name == club_short.upper()))
            team = team_row.scalar_one_or_none()
            if team:
                stmt = stmt.where(models.Player.team_id == team.id)
        stmt = stmt.group_by(models.Player.id).order_by(func.count(models.Assist.id).desc()).limit(limit)
        rows = (await db.execute(stmt)).all()
        result = []
        for i, (p, assists) in enumerate(rows):
            team = await db.get(models.Team, p.team_id)
            result.append({"rank": i+1, "full_name": p.full_name, "team": team.name if team else "", "assists": assists})
        return result


async def _classement(season: str) -> list[dict]:
    await _ensure_db()
    async with AsyncSessionLocal() as db:
        teams = (await db.execute(select(models.Team).where(models.Team.league == "National"))).scalars().all()
        standings = []
        for team in teams:
            home = (await db.execute(
                select(models.Match).where(models.Match.home_team_id == team.id, models.Match.season == season, models.Match.played.is_(True))
            )).scalars().all()
            away = (await db.execute(
                select(models.Match).where(models.Match.away_team_id == team.id, models.Match.season == season, models.Match.played.is_(True))
            )).scalars().all()
            w=d=l=gf=ga=0
            for m in home:
                gf += m.home_score or 0; ga += m.away_score or 0
                diff = (m.home_score or 0) - (m.away_score or 0)
                if diff > 0: w+=1
                elif diff == 0: d+=1
                else: l+=1
            for m in away:
                gf += m.away_score or 0; ga += m.home_score or 0
                diff = (m.away_score or 0) - (m.home_score or 0)
                if diff > 0: w+=1
                elif diff == 0: d+=1
                else: l+=1
            standings.append({"team": team.name, "team_short": team.short_name,
                               "played": len(home)+len(away), "won": w, "drawn": d, "lost": l,
                               "goals_for": gf, "goals_against": ga, "goal_diff": gf-ga, "points": w*3+d})
        standings.sort(key=lambda x: (-x["points"], -x["goal_diff"], -x["goals_for"]))
        return [{"rank": i+1, **s} for i, s in enumerate(standings)]


async def _matches(club_short: str, season: str, last: int) -> list[dict]:
    await _ensure_db()
    async with AsyncSessionLocal() as db:
        team_row = await db.execute(select(models.Team).where(models.Team.short_name == club_short.upper()))
        team = team_row.scalar_one_or_none()
        if not team:
            return []
        rows = (await db.execute(
            select(models.Match)
            .where(or_(models.Match.home_team_id == team.id, models.Match.away_team_id == team.id),
                   models.Match.season == season, models.Match.played.is_(True))
            .order_by(models.Match.match_date.desc()).limit(last)
        )).scalars().all()
        result = []
        for m in rows:
            ht = await db.get(models.Team, m.home_team_id)
            at = await db.get(models.Team, m.away_team_id)
            is_home = m.home_team_id == team.id
            gf = (m.home_score if is_home else m.away_score) or 0
            ga = (m.away_score if is_home else m.home_score) or 0
            r = "W" if gf > ga else ("D" if gf == ga else "L")
            result.append({"matchday": m.matchday, "match_date": str(m.match_date or ""),
                           "home_team": ht.name if ht else "?", "away_team": at.name if at else "?",
                           "home_score": m.home_score, "away_score": m.away_score, "result": r})
        return result


async def _form(club_short: str, season: str, last: int) -> dict:
    matches = await _matches(club_short, season, last)
    w=d=l=gf=ga=0
    form_chars = []
    for m in matches:
        r = m["result"]
        form_chars.append(r)
        if r == "W": w+=1; gf += m["home_score"] or 0; ga += m["away_score"] or 0
        elif r == "D": d+=1; gf += m["home_score"] or 0; ga += m["away_score"] or 0
        else: l+=1; gf += m["home_score"] or 0; ga += m["away_score"] or 0
    return {"form_string": "".join(form_chars), "wins": w, "draws": d, "losses": l,
            "goals_scored": gf, "goals_conceded": ga, "matches": matches}


# ── API publique synchrone ────────────────────────────────────────────────────
def buteurs(league=None, club=None, season="2025", limit=20):
    if club:
        return run(_buteurs_club(club, season))
    return run(_buteurs_national(season, limit))

def passeurs(club=None, season="2025", limit=20):
    return run(_passeurs(club, season, limit))

def classement(season="2025"):
    return run(_classement(season))

def matches(club="FCSM", season="2025", last=10):
    return run(_matches(club, season, last))

def form(club="FCSM", season="2025", last=5):
    return run(_form(club, season, last))
