"""fcsmtop — CLI standalone pour les stats National/FCSM.

Usage :
    python cli/main.py buteurs --club FCSM
    python cli/main.py classement
    python cli/main.py form --club FCSM --last 5

Fonctionne sans serveur API — accès direct à la base SQLite.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///./fcsmtop.db")

import typer
from rich.console import Console
from rich.table import Table
from rich import box

from cli import db as DB

app = typer.Typer(
    help="⚽ fcsmtop — Stats Championnat National & FCSM 🟡🔵\n\nFonctionne directement sans serveur (SQLite auto-initialisée).",
    rich_markup_mode="rich",
)
console = Console()


@app.command()
def buteurs(
    league: str = typer.Option(None, "--league", "-l", help="Ligue : national"),
    club: str  = typer.Option(None, "--club",   "-c", help="Club : FCSM, ORL…"),
    season: str = typer.Option("2025", "--season", "-s"),
    top: int    = typer.Option(15, "--top", "-n"),
):
    """⚽ Top buteurs (National ou club)."""
    if not club and not league:
        console.print("[yellow]Précise --league national ou --club FCSM[/yellow]")
        raise typer.Exit()

    data = DB.buteurs(league=league, club=club, season=season, limit=top)

    if not data:
        console.print("[red]Aucun résultat.[/red]"); return

    title = f"⚽ Buteurs {'FCSM' if club else 'Championnat National'} — Saison {season}"
    t = Table(title=title, box=box.ROUNDED, header_style="bold yellow", show_lines=False)
    t.add_column("#",       width=4,  style="dim")
    t.add_column("Joueur",  style="bold")
    t.add_column("Club",    width=8)
    t.add_column("Buts",    justify="right", style="green bold")
    t.add_column("(pen.)",  justify="right", style="dim")
    t.add_column("P.D.",    justify="right", style="cyan")

    for r in data[:top]:
        t.add_row(str(r["rank"]), r["full_name"], r["team_short"],
                  str(r["goals"]),
                  str(r["penalties"]) if r["penalties"] else "—",
                  str(r["assists"]))

    console.print(t)


@app.command()
def passeurs(
    league: str  = typer.Option(None,   "--league", "-l"),
    club: str    = typer.Option(None,   "--club",   "-c"),
    season: str  = typer.Option("2025", "--season", "-s"),
    top: int     = typer.Option(10,     "--top",    "-n"),
):
    """🎯 Top passeurs décisifs."""
    data = DB.passeurs(club=club, season=season, limit=top)
    if not data:
        console.print("[red]Aucun résultat.[/red]"); return

    title = f"🎯 Passeurs {'FCSM' if club else 'National'} — Saison {season}"
    t = Table(title=title, box=box.ROUNDED, header_style="bold cyan")
    t.add_column("#",        width=4, style="dim")
    t.add_column("Joueur",   style="bold")
    t.add_column("Club")
    t.add_column("Passes D.", justify="right", style="cyan bold")

    for r in data[:top]:
        t.add_row(str(r["rank"]), r["full_name"], r["team"], str(r["assists"]))

    console.print(t)


@app.command()
def classement(season: str = typer.Option("2025", "--season", "-s")):
    """📊 Classement du Championnat National."""
    data = DB.classement(season=season)
    if not data:
        console.print("[red]Aucun résultat.[/red]"); return

    t = Table(title=f"📊 Classement National — Saison {season}", box=box.ROUNDED, header_style="bold white")
    t.add_column("#",   width=4, style="dim")
    t.add_column("Équipe", style="bold")
    t.add_column("J",  justify="right")
    t.add_column("G",  justify="right", style="green")
    t.add_column("N",  justify="right", style="yellow")
    t.add_column("P",  justify="right", style="red")
    t.add_column("BP", justify="right")
    t.add_column("BC", justify="right")
    t.add_column("+/-",justify="right")
    t.add_column("Pts",justify="right", style="bold yellow")

    for r in data:
        style = "bold cyan" if r["team_short"] == "FCSM" else None
        t.add_row(
            str(r["rank"]), r["team"],
            str(r["played"]), str(r["won"]), str(r["drawn"]), str(r["lost"]),
            str(r["goals_for"]), str(r["goals_against"]),
            f"{r['goal_diff']:+d}", str(r["points"]),
            style=style,
        )

    console.print(t)


@app.command()
def matches(
    club: str   = typer.Option("FCSM",  "--club",   "-c"),
    season: str = typer.Option("2025",  "--season", "-s"),
    last: int   = typer.Option(10,      "--last",   "-n"),
):
    """📅 Derniers matchs d'un club."""
    data = DB.matches(club=club, season=season, last=last)
    if not data:
        console.print("[red]Aucun résultat.[/red]"); return

    t = Table(title=f"📅 Matchs {club.upper()} — {season}", box=box.ROUNDED, header_style="bold white")
    t.add_column("J.",  width=4)
    t.add_column("Date", width=12)
    t.add_column("Domicile", style="bold")
    t.add_column("Score", justify="center", style="yellow bold")
    t.add_column("Extérieur", style="bold")
    t.add_column("Résultat", justify="center")

    icons = {"W": "[green]✅ V[/green]", "D": "[yellow]🟡 N[/yellow]", "L": "[red]❌ D[/red]"}
    for m in data:
        t.add_row(
            str(m["matchday"]),
            m["match_date"][:10],
            m["home_team"],
            f"{m.get('home_score','?')} - {m.get('away_score','?')}",
            m["away_team"],
            icons.get(m.get("result", ""), "—"),
        )

    console.print(t)


@app.command()
def form(
    club: str   = typer.Option("FCSM", "--club",   "-c"),
    season: str = typer.Option("2025", "--season", "-s"),
    last: int   = typer.Option(5,      "--last",   "-n"),
):
    """📈 Forme récente d'un club (W/D/L)."""
    data = DB.form(club=club, season=season, last=last)

    colors = {"W": "green", "D": "yellow", "L": "red"}
    form_colored = " ".join(f"[{colors[c]}]{c}[/{colors[c]}]" for c in data["form_string"])

    console.print(f"\n[bold]📈 Forme {club.upper()} — {last} derniers matchs[/bold]")
    console.print(f"  Forme : {form_colored}")
    console.print(
        f"  Bilan : [green]{data['wins']}V[/green]  "
        f"[yellow]{data['draws']}N[/yellow]  "
        f"[red]{data['losses']}D[/red]"
    )
    console.print(
        f"  Buts  : [green]{data['goals_scored']}[/green] marqués "
        f"/ [red]{data['goals_conceded']}[/red] encaissés\n"
    )


if __name__ == "__main__":
    app()
