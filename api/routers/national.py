from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from api.database import get_db
from api import models, schemas

router = APIRouter(prefix="/api/v1/national", tags=["National"])


@router.get("/buteurs", response_model=list[schemas.ScorerOut])
async def get_national_buteurs(
    season: str = Query("2025", description="Saison (ex: 2025)"),
    limit: int = Query(20, le=50),
    db: AsyncSession = Depends(get_db),
):
    """Top buteurs du Championnat National pour une saison."""
    stmt = (
        select(
            models.Player,
            func.count(models.Goal.id).filter(models.Goal.own_goal.is_(False)).label("goals"),
            func.count(models.Goal.id).filter(models.Goal.penalty.is_(True)).label("penalties"),
            func.count(models.Assist.id).label("assists"),
        )
        .join(models.Goal, models.Goal.scorer_id == models.Player.id)
        .join(models.Match, models.Match.id == models.Goal.match_id)
        .outerjoin(models.Assist, (models.Assist.player_id == models.Player.id) & (models.Assist.match_id == models.Match.id))
        .where(models.Match.season == season, models.Goal.own_goal.is_(False))
        .group_by(models.Player.id)
        .order_by(func.count(models.Goal.id).filter(models.Goal.own_goal.is_(False)).desc())
        .limit(limit)
    )
    result = await db.execute(stmt)
    rows = result.all()

    return [
        schemas.ScorerOut(
            rank=i + 1,
            player_id=p.id,
            full_name=p.full_name,
            team=p.team.name if p.team else "",
            team_short=p.team.short_name if p.team else "",
            goals=goals,
            assists=assists,
            penalties=pens,
        )
        for i, (p, goals, pens, assists) in enumerate(rows)
    ]


@router.get("/passeurs", response_model=list[schemas.AssistOut])
async def get_national_passeurs(
    season: str = Query("2025"),
    limit: int = Query(20, le=50),
    db: AsyncSession = Depends(get_db),
):
    """Top passeurs décisifs du Championnat National."""
    stmt = (
        select(
            models.Player,
            func.count(models.Assist.id).label("assists"),
        )
        .join(models.Assist, models.Assist.player_id == models.Player.id)
        .join(models.Match, models.Match.id == models.Assist.match_id)
        .where(models.Match.season == season)
        .group_by(models.Player.id)
        .order_by(func.count(models.Assist.id).desc())
        .limit(limit)
    )
    result = await db.execute(stmt)
    rows = result.all()

    return [
        schemas.AssistOut(
            rank=i + 1,
            player_id=p.id,
            full_name=p.full_name,
            team=p.team.name if p.team else "",
            assists=assists,
        )
        for i, (p, assists) in enumerate(rows)
    ]


@router.get("/classement", response_model=list[schemas.StandingOut])
async def get_classement(
    season: str = Query("2025"),
    db: AsyncSession = Depends(get_db),
):
    """Classement du Championnat National."""
    teams_result = await db.execute(select(models.Team).where(models.Team.league == "National"))
    teams = teams_result.scalars().all()

    standings = []
    for team in teams:
        home_q = await db.execute(
            select(models.Match).where(
                models.Match.home_team_id == team.id,
                models.Match.season == season,
                models.Match.played.is_(True),
            )
        )
        away_q = await db.execute(
            select(models.Match).where(
                models.Match.away_team_id == team.id,
                models.Match.season == season,
                models.Match.played.is_(True),
            )
        )
        home_matches = home_q.scalars().all()
        away_matches = away_q.scalars().all()

        w, d, l, gf, ga = 0, 0, 0, 0, 0
        for m in home_matches:
            gf += m.home_score or 0
            ga += m.away_score or 0
            diff = (m.home_score or 0) - (m.away_score or 0)
            if diff > 0: w += 1
            elif diff == 0: d += 1
            else: l += 1
        for m in away_matches:
            gf += m.away_score or 0
            ga += m.home_score or 0
            diff = (m.away_score or 0) - (m.home_score or 0)
            if diff > 0: w += 1
            elif diff == 0: d += 1
            else: l += 1

        played = len(home_matches) + len(away_matches)
        points = w * 3 + d

        standings.append({
            "team": team.name,
            "team_short": team.short_name,
            "played": played,
            "won": w,
            "drawn": d,
            "lost": l,
            "goals_for": gf,
            "goals_against": ga,
            "goal_diff": gf - ga,
            "points": points,
        })

    standings.sort(key=lambda x: (-x["points"], -x["goal_diff"], -x["goals_for"]))
    return [schemas.StandingOut(rank=i + 1, **s) for i, s in enumerate(standings)]
