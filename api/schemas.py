from datetime import date
from typing import Optional
from pydantic import BaseModel, computed_field


class TeamBase(BaseModel):
    name: str
    short_name: str
    city: str
    league: str = "National"

    model_config = {"from_attributes": True}


class PlayerBase(BaseModel):
    first_name: str
    last_name: str
    position: str
    nationality: str
    number: Optional[int] = None

    model_config = {"from_attributes": True}

    @computed_field
    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"


class ScorerOut(BaseModel):
    rank: int
    player_id: int
    full_name: str
    team: str
    team_short: str
    goals: int
    assists: int
    penalties: int

    model_config = {"from_attributes": True}


class AssistOut(BaseModel):
    rank: int
    player_id: int
    full_name: str
    team: str
    assists: int

    model_config = {"from_attributes": True}


class StandingOut(BaseModel):
    rank: int
    team: str
    team_short: str
    played: int
    won: int
    drawn: int
    lost: int
    goals_for: int
    goals_against: int
    goal_diff: int
    points: int

    model_config = {"from_attributes": True}


class MatchOut(BaseModel):
    id: int
    matchday: int
    match_date: Optional[date]
    home_team: str
    away_team: str
    home_score: Optional[int]
    away_score: Optional[int]
    result: Optional[str] = None  # "W", "D", "L" from FCSM perspective

    model_config = {"from_attributes": True}


class FormOut(BaseModel):
    club: str
    last_n: int
    matches: list[MatchOut]
    form_string: str  # e.g. "WWDLW"
    wins: int
    draws: int
    losses: int
    goals_scored: int
    goals_conceded: int

    model_config = {"from_attributes": True}


class HealthOut(BaseModel):
    status: str
    version: str
    db: str
