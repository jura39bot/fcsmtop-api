from datetime import date, datetime
from typing import Optional
from sqlalchemy import String, Integer, Date, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from api.database import Base


class Team(Base):
    __tablename__ = "teams"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    short_name: Mapped[str] = mapped_column(String(10))
    city: Mapped[str] = mapped_column(String(100))
    league: Mapped[str] = mapped_column(String(50), default="National")

    players: Mapped[list["Player"]] = relationship(back_populates="team")
    home_matches: Mapped[list["Match"]] = relationship(foreign_keys="Match.home_team_id", back_populates="home_team")
    away_matches: Mapped[list["Match"]] = relationship(foreign_keys="Match.away_team_id", back_populates="away_team")


class Player(Base):
    __tablename__ = "players"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    first_name: Mapped[str] = mapped_column(String(100))
    last_name: Mapped[str] = mapped_column(String(100))
    position: Mapped[str] = mapped_column(String(30))
    nationality: Mapped[str] = mapped_column(String(50), default="Français")
    birth_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    number: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    team_id: Mapped[int] = mapped_column(ForeignKey("teams.id"))

    team: Mapped["Team"] = relationship(back_populates="players")
    goals: Mapped[list["Goal"]] = relationship(back_populates="scorer")
    assists: Mapped[list["Assist"]] = relationship(back_populates="player")
    cards: Mapped[list["Card"]] = relationship(back_populates="player")

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"


class Match(Base):
    __tablename__ = "matches"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    season: Mapped[str] = mapped_column(String(10), index=True)
    matchday: Mapped[int] = mapped_column(Integer)
    match_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    home_team_id: Mapped[int] = mapped_column(ForeignKey("teams.id"))
    away_team_id: Mapped[int] = mapped_column(ForeignKey("teams.id"))
    home_score: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    away_score: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    played: Mapped[bool] = mapped_column(Boolean, default=False)

    home_team: Mapped["Team"] = relationship(foreign_keys=[home_team_id], back_populates="home_matches")
    away_team: Mapped["Team"] = relationship(foreign_keys=[away_team_id], back_populates="away_matches")
    goals: Mapped[list["Goal"]] = relationship(back_populates="match")
    assists: Mapped[list["Assist"]] = relationship(back_populates="match")
    cards: Mapped[list["Card"]] = relationship(back_populates="match")


class Goal(Base):
    __tablename__ = "goals"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    match_id: Mapped[int] = mapped_column(ForeignKey("matches.id"))
    scorer_id: Mapped[int] = mapped_column(ForeignKey("players.id"))
    minute: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    own_goal: Mapped[bool] = mapped_column(Boolean, default=False)
    penalty: Mapped[bool] = mapped_column(Boolean, default=False)

    match: Mapped["Match"] = relationship(back_populates="goals")
    scorer: Mapped["Player"] = relationship(back_populates="goals")


class Assist(Base):
    __tablename__ = "assists"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    match_id: Mapped[int] = mapped_column(ForeignKey("matches.id"))
    player_id: Mapped[int] = mapped_column(ForeignKey("players.id"))
    minute: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    match: Mapped["Match"] = relationship(back_populates="assists")
    player: Mapped["Player"] = relationship(back_populates="assists")


class Card(Base):
    __tablename__ = "cards"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    match_id: Mapped[int] = mapped_column(ForeignKey("matches.id"))
    player_id: Mapped[int] = mapped_column(ForeignKey("players.id"))
    card_type: Mapped[str] = mapped_column(String(10))  # "yellow" | "red"
    minute: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    match: Mapped["Match"] = relationship(back_populates="cards")
    player: Mapped["Player"] = relationship(back_populates="cards")
