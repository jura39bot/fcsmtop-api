"""Charge les données initiales en base (équipes, joueurs, matchs, buts, passes)."""
import asyncio
import sys
import os
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///./fcsmtop.db")

from api.database import AsyncSessionLocal, init_db
from api.models import Team, Player, Match, Goal, Assist, Card


TEAMS = [
    ("FC Sochaux-Montbéliard", "FCSM", "Montbéliard"),
    ("US Orléans", "ORL", "Orléans"),
    ("Rouen FC", "ROU", "Rouen"),
    ("Red Star FC", "RST", "Saint-Ouen"),
    ("Avranches FC", "AVR", "Avranches"),
    ("Villefranche Beaujolais", "VIL", "Villefranche"),
    ("Marignane Gignac FC", "MGF", "Marignane"),
    ("Concarneau FC", "CON", "Concarneau"),
    ("Châteauroux", "CHT", "Châteauroux"),
    ("Béziers FC", "BEZ", "Béziers"),
    ("Versailles FC", "VER", "Versailles"),
    ("Grenoble Foot 38", "GRE", "Grenoble"),
    ("Dijon FCO", "DIJ", "Dijon"),
    ("Évreux FC 27", "EVR", "Évreux"),
    ("Annecy FC", "ANN", "Annecy"),
    ("Bergerac Périgord FC", "BER", "Bergerac"),
]

FCSM_PLAYERS = [
    ("Maxime", "Pichon", "Gardien", "Français", 1),
    ("Théo", "Hamelin", "Défenseur", "Français", 2),
    ("Kévin", "Fortuné", "Défenseur", "Français", 5),
    ("Julien", "Voisin", "Défenseur", "Français", 3),
    ("Moussa", "Sidibé", "Défenseur", "Malien", 4),
    ("Florian", "Tardieu", "Milieu", "Français", 6),
    ("Nicolas", "Laurent", "Milieu", "Français", 8),
    ("Samir", "Hadji", "Milieu", "Marocain", 10),
    ("Mathis", "Brun", "Milieu", "Français", 7),
    ("Yacine", "Fofana", "Milieu", "Français", 14),
    ("Alexis", "Bernard", "Milieu", "Français", 11),
    ("Dylan", "Bronn", "Attaquant", "Tunisien", 9),
    ("Eliakim", "Mangala", "Attaquant", "Français", 19),
    ("Jordan", "Lefort", "Attaquant", "Français", 17),
    ("Ibrahim", "Koné", "Attaquant", "Ivoirien", 18),
    ("Thomas", "Robinet", "Attaquant", "Français", 22),
    ("Bastien", "Meupiyou", "Défenseur", "Français", 13),
    ("Sébastien", "Crozet", "Milieu", "Français", 16),
    ("Raphaël", "Aguirre", "Attaquant", "Franco-Espagnol", 21),
    ("Amine", "Zidane", "Milieu", "Algérien", 23),
]

OTHER_PLAYERS = [
    ("Nathan", "Géry", "Attaquant", "Français", "ORL"),
    ("Luca", "Ferrari", "Attaquant", "Franco-Italien", "ROU"),
    ("Kevin", "Tapoko", "Attaquant", "Français", "RST"),
    ("Dorian", "Lévêque", "Milieu", "Français", "AVR"),
    ("Mehdi", "Chahiri", "Attaquant", "Marocain", "VIL"),
    ("Théo", "Defourny", "Attaquant", "Belge", "GRE"),
    ("Marvin", "Senaya", "Attaquant", "Français", "DIJ"),
    ("Baptiste", "Soudan", "Milieu", "Français", "ORL"),
]

MATCHES_DATA = [
    # (matchday, date, home_short, away_short, home_score, away_score)
    (1,  date(2024, 8, 10), "FCSM", "ORL",  2, 0),
    (2,  date(2024, 8, 17), "RST",  "FCSM", 1, 1),
    (3,  date(2024, 8, 24), "FCSM", "ROU",  3, 1),
    (4,  date(2024, 8, 31), "AVR",  "FCSM", 0, 2),
    (5,  date(2024, 9,  7), "FCSM", "VIL",  1, 0),
    (6,  date(2024, 9, 14), "MGF",  "FCSM", 2, 2),
    (7,  date(2024, 9, 21), "FCSM", "CON",  4, 0),
    (8,  date(2024, 9, 28), "CHT",  "FCSM", 0, 1),
    (9,  date(2024, 10, 5), "FCSM", "BEZ",  2, 1),
    (10, date(2024, 10,12), "VER",  "FCSM", 1, 3),
    (11, date(2024, 10,19), "FCSM", "GRE",  1, 1),
    (12, date(2024, 10,26), "DIJ",  "FCSM", 0, 2),
    (13, date(2024, 11, 2), "FCSM", "EVR",  3, 0),
    (14, date(2024, 11, 9), "ANN",  "FCSM", 1, 2),
    (15, date(2024, 11,16), "FCSM", "BER",  2, 0),
    (16, date(2024, 11,23), "ORL",  "FCSM", 0, 1),
    (17, date(2024, 11,30), "FCSM", "RST",  2, 0),
    (18, date(2024, 12, 7), "ROU",  "FCSM", 1, 1),
    (19, date(2024, 12,14), "FCSM", "AVR",  1, 0),
    (20, date(2024, 12,21), "VIL",  "FCSM", 2, 3),
    # Matchs inter-équipes (sans FCSM)
    (1,  date(2024, 8, 10), "RST",  "VER",  2, 1),
    (1,  date(2024, 8, 10), "DIJ",  "GRE",  0, 0),
    (1,  date(2024, 8, 10), "ORL",  "AVR",  1, 0),
    (2,  date(2024, 8, 17), "VER",  "DIJ",  1, 2),
    (3,  date(2024, 8, 24), "AVR",  "RST",  0, 1),
]

# Buts FCSM avec buteur et passeur
FCSM_GOALS = [
    # (matchday, home_short, away_short, scorer_last, penalty, own_goal, assister_last)
    (1,  "FCSM", "ORL",  "Bronn",     False, False, "Hadji"),
    (1,  "FCSM", "ORL",  "Koné",      False, False, "Laurent"),
    (3,  "FCSM", "ROU",  "Bronn",     False, False, "Tardieu"),
    (3,  "FCSM", "ROU",  "Mangala",   False, False, None),
    (3,  "FCSM", "ROU",  "Hadji",     True,  False, None),
    (4,  "AVR",  "FCSM", "Lefort",    False, False, "Hadji"),
    (4,  "AVR",  "FCSM", "Bronn",     False, False, "Fofana"),
    (5,  "FCSM", "VIL",  "Koné",      False, False, "Laurent"),
    (6,  "MGF",  "FCSM", "Bronn",     False, False, "Hadji"),
    (6,  "MGF",  "FCSM", "Mangala",   False, False, None),
    (7,  "FCSM", "CON",  "Bronn",     False, False, "Tardieu"),
    (7,  "FCSM", "CON",  "Lefort",    False, False, "Hadji"),
    (7,  "FCSM", "CON",  "Koné",      False, False, "Fofana"),
    (7,  "FCSM", "CON",  "Hadji",     True,  False, None),
    (8,  "CHT",  "FCSM", "Bronn",     False, False, "Laurent"),
    (9,  "FCSM", "BEZ",  "Mangala",   False, False, "Hadji"),
    (9,  "FCSM", "BEZ",  "Lefort",    False, False, "Bronn"),
    (10, "VER",  "FCSM", "Bronn",     False, False, "Hadji"),
    (10, "VER",  "FCSM", "Koné",      False, False, "Tardieu"),
    (10, "VER",  "FCSM", "Fofana",    False, False, None),
    (12, "DIJ",  "FCSM", "Bronn",     False, False, "Hadji"),
    (12, "DIJ",  "FCSM", "Mangala",   False, False, "Lefort"),
    (13, "FCSM", "EVR",  "Koné",      False, False, "Fofana"),
    (13, "FCSM", "EVR",  "Bronn",     False, False, "Laurent"),
    (13, "FCSM", "EVR",  "Hadji",     True,  False, None),
    (14, "ANN",  "FCSM", "Mangala",   False, False, "Bronn"),
    (14, "ANN",  "FCSM", "Lefort",    False, False, "Hadji"),
    (15, "FCSM", "BER",  "Bronn",     False, False, "Tardieu"),
    (15, "FCSM", "BER",  "Koné",      False, False, "Hadji"),
    (16, "ORL",  "FCSM", "Fofana",    False, False, "Bronn"),
    (17, "FCSM", "RST",  "Bronn",     False, False, "Hadji"),
    (17, "FCSM", "RST",  "Mangala",   False, False, "Lefort"),
    (19, "FCSM", "AVR",  "Koné",      False, False, "Bronn"),
    (20, "VIL",  "FCSM", "Lefort",    False, False, "Hadji"),
    (20, "VIL",  "FCSM", "Bronn",     False, False, "Fofana"),
    (20, "VIL",  "FCSM", "Hadji",     True,  False, None),
]


async def seed():
    await init_db()
    async with AsyncSessionLocal() as db:
        # Teams
        team_map = {}
        for name, short, city in TEAMS:
            t = Team(name=name, short_name=short, city=city)
            db.add(t)
            await db.flush()
            team_map[short] = t

        # FCSM players
        fcsm = team_map["FCSM"]
        player_map = {}
        for fn, ln, pos, nat, num in FCSM_PLAYERS:
            p = Player(first_name=fn, last_name=ln, position=pos, nationality=nat, number=num, team_id=fcsm.id)
            db.add(p)
            await db.flush()
            player_map[ln] = p

        # Other players
        for fn, ln, pos, nat, short in OTHER_PLAYERS:
            team = team_map.get(short)
            if team:
                p = Player(first_name=fn, last_name=ln, position=pos, nationality=nat, team_id=team.id)
                db.add(p)
                await db.flush()
                player_map[f"{short}_{ln}"] = p

        # Matches
        match_map = {}
        for md, dt, home_s, away_s, hs, as_ in MATCHES_DATA:
            m = Match(
                season="2025", matchday=md, match_date=dt,
                home_team_id=team_map[home_s].id, away_team_id=team_map[away_s].id,
                home_score=hs, away_score=as_, played=True,
            )
            db.add(m)
            await db.flush()
            match_map[(md, home_s, away_s)] = m

        # Goals & Assists
        for md, home_s, away_s, scorer_ln, penalty, own_goal, assister_ln in FCSM_GOALS:
            match = match_map.get((md, home_s, away_s))
            scorer = player_map.get(scorer_ln)
            if not match or not scorer:
                continue
            g = Goal(match_id=match.id, scorer_id=scorer.id, penalty=penalty, own_goal=own_goal)
            db.add(g)
            await db.flush()
            if assister_ln and not penalty:
                assister = player_map.get(assister_ln)
                if assister:
                    a = Assist(match_id=match.id, player_id=assister.id)
                    db.add(a)

        await db.commit()
        print("✅ Données chargées avec succès !")
        print(f"   {len(TEAMS)} équipes, {len(FCSM_PLAYERS)} joueurs FCSM, {len(MATCHES_DATA)} matchs, {len(FCSM_GOALS)} buts")


if __name__ == "__main__":
    asyncio.run(seed())
