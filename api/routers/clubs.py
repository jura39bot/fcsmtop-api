from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from api.database import get_db
from api import models, schemas

router = APIRouter(prefix="/api/v1/clubs", tags=["Clubs"])

FCSM_SHORT = "FCSM"


async def _get_team(db: AsyncSession, short_name: str) -> models.Team:
    result = await db.execute(select(models.Team).where(models.Team.short_name == short_name.upper()))
    team = result.scalar_one_or_none()
    if not team:
        raise HTTPException(status_code=404, detail=f"Club '{short_name}' introuvable")
    return team


@router.get("/{club}/buteurs", response_model=list[schemas.ScorerOut])
async def get_club_buteurs(
    club: str,
    season: str = Query("2025"),
    db: AsyncSession = Depends(get_db),
):
    """Top buteurs d'un club pour une saison."""
    team = await _get_team(db, club)

    stmt = (
        select(
            models.Player,
            func.count(models.Goal.id).filter(models.Goal.own_goal.is_(False)).label("goals"),
            func.count(models.Goal.id).filter(models.Goal.penalty.is_(True)).label("penalties"),
        )
        .join(models.Goal, models.Goal.scorer_id == models.Player.id)
        .join(models.Match, models.Match.id == models.Goal.match_id)
        .where(
            models.Player.team_id == team.id,
            models.Match.season == season,
            models.Goal.own_goal.is_(False),
        )
        .group_by(models.Player.id)
        .order_by(func.count(models.Goal.id).filter(models.Goal.own_goal.is_(False)).desc())
    )
    result = await db.execute(stmt)
    rows = result.all()

    return [
        schemas.ScorerOut(
            rank=i + 1,
            player_id=p.id,
            full_name=p.full_name,
            team=team.name,
            team_short=team.short_name,
            goals=goals,
            assists=0,
            penalties=pens,
        )
        for i, (p, goals, pens) in enumerate(rows)
    ]


@router.get("/{club}/passeurs", response_model=list[schemas.AssistOut])
async def get_club_passeurs(
    club: str,
    season: str = Query("2025"),
    db: AsyncSession = Depends(get_db),
):
    """Top passeurs d'un club pour une saison."""
    team = await _get_team(db, club)

    stmt = (
        select(models.Player, func.count(models.Assist.id).label("assists"))
        .join(models.Assist, models.Assist.player_id == models.Player.id)
        .join(models.Match, models.Match.id == models.Assist.match_id)
        .where(models.Player.team_id == team.id, models.Match.season == season)
        .group_by(models.Player.id)
        .order_by(func.count(models.Assist.id).desc())
    )
    result = await db.execute(stmt)
    rows = result.all()

    return [
        schemas.AssistOut(rank=i + 1, player_id=p.id, full_name=p.full_name, team=team.name, assists=assists)
        for i, (p, assists) in enumerate(rows)
    ]


@router.get("/{club}/matches", response_model=list[schemas.MatchOut])
async def get_club_matches(
    club: str,
    season: str = Query("2025"),
    last: int = Query(10, le=38),
    db: AsyncSession = Depends(get_db),
):
    """Derniers matchs d'un club."""
    team = await _get_team(db, club)

    stmt = (
        select(models.Match)
        .where(
            or_(models.Match.home_team_id == team.id, models.Match.away_team_id == team.id),
            models.Match.season == season,
            models.Match.played.is_(True),
        )
        .order_by(models.Match.match_date.desc())
        .limit(last)
    )
    result = await db.execute(stmt)
    matches = result.scalars().all()

    out = []
    for m in matches:
        await db.refresh(m, ["home_team", "away_team"])
        is_home = m.home_team_id == team.id
        gf = m.home_score if is_home else m.away_score
        ga = m.away_score if is_home else m.home_score
        if gf is not None and ga is not None:
            result_str = "W" if gf > ga else ("D" if gf == ga else "L")
        else:
            result_str = None
        out.append(schemas.MatchOut(
            id=m.id,
            matchday=m.matchday,
            match_date=m.match_date,
            home_team=m.home_team.name,
            away_team=m.away_team.name,
            home_score=m.home_score,
            away_score=m.away_score,
            result=result_str,
        ))

    return out


@router.get("/{club}/form", response_model=schemas.FormOut)
async def get_club_form(
    club: str,
    season: str = Query("2025"),
    last: int = Query(5, le=10),
    db: AsyncSession = Depends(get_db),
):
    """Forme récente d'un club (W/D/L sur les N derniers matchs)."""
    team = await _get_team(db, club)

    stmt = (
        select(models.Match)
        .where(
            or_(models.Match.home_team_id == team.id, models.Match.away_team_id == team.id),
            models.Match.season == season,
            models.Match.played.is_(True),
        )
        .order_by(models.Match.match_date.desc())
        .limit(last)
    )
    result = await db.execute(stmt)
    matches = result.scalars().all()

    match_outs = []
    form_chars = []
    wins = draws = losses = gf_total = ga_total = 0

    for m in matches:
        await db.refresh(m, ["home_team", "away_team"])
        is_home = m.home_team_id == team.id
        gf = (m.home_score if is_home else m.away_score) or 0
        ga = (m.away_score if is_home else m.home_score) or 0
        gf_total += gf
        ga_total += ga
        if gf > ga:
            wins += 1; form_chars.append("W")
        elif gf == ga:
            draws += 1; form_chars.append("D")
        else:
            losses += 1; form_chars.append("L")
        match_outs.append(schemas.MatchOut(
            id=m.id, matchday=m.matchday, match_date=m.match_date,
            home_team=m.home_team.name, away_team=m.away_team.name,
            home_score=m.home_score, away_score=m.away_score,
            result=form_chars[-1],
        ))

    return schemas.FormOut(
        club=team.name,
        last_n=last,
        matches=match_outs,
        form_string="".join(form_chars),
        wins=wins,
        draws=draws,
        losses=losses,
        goals_scored=gf_total,
        goals_conceded=ga_total,
    )
