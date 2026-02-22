"""fcsmtop — CLI pour interroger l'API de statistiques National/FCSM."""
import typer
import httpx
from rich.console import Console
from rich.table import Table
from rich import box

app = typer.Typer(help="fcsmtop — Stats Championnat National & FCSM 🟡🔵")
console = Console()

API_BASE = "http://localhost:8000/api/v1"


def _get(path: str, params: dict = None) -> dict | list:
    try:
        r = httpx.get(f"{API_BASE}{path}", params=params or {}, timeout=10)
        r.raise_for_status()
        return r.json()
    except httpx.ConnectError:
        console.print("[red]❌ Impossible de contacter l'API. Lance d'abord le serveur :[/red]")
        console.print("   uvicorn api.main:app --reload")
        raise typer.Exit(1)
    except httpx.HTTPStatusError as e:
        console.print(f"[red]❌ Erreur API {e.response.status_code}[/red]")
        raise typer.Exit(1)


@app.command()
def buteurs(
    league: str = typer.Option(None, "--league", "-l", help="Ligue (ex: national)"),
    club: str = typer.Option(None, "--club", "-c", help="Club (ex: FCSM)"),
    season: str = typer.Option("2025", "--season", "-s", help="Saison"),
    top: int = typer.Option(10, "--top", "-n", help="Nombre de résultats"),
):
    """🥅 Top buteurs — National ou par club."""
    if club:
        data = _get(f"/clubs/{club}/buteurs", {"season": season})
        title = f"⚽ Buteurs {club.upper()} — Saison {season}"
    elif league and league.lower() == "national":
        data = _get("/national/buteurs", {"season": season, "limit": top})
        title = f"⚽ Buteurs Championnat National — Saison {season}"
    else:
        console.print("[yellow]Précise --league national ou --club FCSM[/yellow]")
        raise typer.Exit()

    t = Table(title=title, box=box.ROUNDED, show_header=True, header_style="bold yellow")
    t.add_column("#", style="dim", width=4)
    t.add_column("Joueur", style="bold")
    t.add_column("Club")
    t.add_column("Buts", justify="right", style="green bold")
    t.add_column("Dont pen.", justify="right", style="dim")
    t.add_column("Passes D.", justify="right", style="cyan")

    for row in data[:top]:
        t.add_row(
            str(row["rank"]),
            row["full_name"],
            row["team_short"],
            str(row["goals"]),
            str(row["penalties"]) if row["penalties"] else "—",
            str(row["assists"]),
        )

    console.print(t)


@app.command()
def passeurs(
    league: str = typer.Option(None, "--league", "-l"),
    club: str = typer.Option(None, "--club", "-c"),
    season: str = typer.Option("2025", "--season", "-s"),
    top: int = typer.Option(10, "--top", "-n"),
):
    """🎯 Top passeurs décisifs."""
    if club:
        data = _get(f"/clubs/{club}/passeurs", {"season": season})
        title = f"🎯 Passeurs {club.upper()} — Saison {season}"
    else:
        data = _get("/national/passeurs", {"season": season, "limit": top})
        title = f"🎯 Passeurs Championnat National — Saison {season}"

    t = Table(title=title, box=box.ROUNDED, header_style="bold cyan")
    t.add_column("#", width=4, style="dim")
    t.add_column("Joueur", style="bold")
    t.add_column("Club")
    t.add_column("Passes D.", justify="right", style="cyan bold")

    for row in data[:top]:
        t.add_row(str(row["rank"]), row["full_name"], row["team"], str(row["assists"]))

    console.print(t)


@app.command()
def classement(season: str = typer.Option("2025", "--season", "-s")):
    """📊 Classement du Championnat National."""
    data = _get("/national/classement", {"season": season})

    t = Table(title=f"📊 Classement National — Saison {season}", box=box.ROUNDED, header_style="bold white")
    t.add_column("#", width=4, style="dim")
    t.add_column("Équipe", style="bold")
    t.add_column("J", justify="right")
    t.add_column("G", justify="right", style="green")
    t.add_column("N", justify="right", style="yellow")
    t.add_column("P", justify="right", style="red")
    t.add_column("BP", justify="right")
    t.add_column("BC", justify="right")
    t.add_column("+/-", justify="right")
    t.add_column("Pts", justify="right", style="bold yellow")

    for row in data:
        style = "bold cyan" if row["team_short"] == "FCSM" else None
        t.add_row(
            str(row["rank"]), row["team"], str(row["played"]),
            str(row["won"]), str(row["drawn"]), str(row["lost"]),
            str(row["goals_for"]), str(row["goals_against"]),
            f"{row['goal_diff']:+d}", str(row["points"]),
            style=style,
        )

    console.print(t)


@app.command()
def matches(
    club: str = typer.Option("FCSM", "--club", "-c"),
    season: str = typer.Option("2025", "--season", "-s"),
    last: int = typer.Option(10, "--last", "-n"),
):
    """📅 Derniers matchs d'un club."""
    data = _get(f"/clubs/{club}/matches", {"season": season, "last": last})

    t = Table(title=f"📅 Derniers matchs {club.upper()} — Saison {season}", box=box.ROUNDED, header_style="bold white")
    t.add_column("J.", width=4)
    t.add_column("Date")
    t.add_column("Domicile", style="bold")
    t.add_column("Score", justify="center", style="yellow bold")
    t.add_column("Extérieur", style="bold")
    t.add_column("Résultat", justify="center")

    for m in data:
        result_style = {"W": "green", "D": "yellow", "L": "red"}.get(m.get("result"), "")
        result_icon = {"W": "✅ V", "D": "🟡 N", "L": "❌ D"}.get(m.get("result"), "—")
        t.add_row(
            str(m["matchday"]),
            str(m.get("match_date", ""))[:10],
            m["home_team"],
            f"{m.get('home_score', '?')} - {m.get('away_score', '?')}",
            m["away_team"],
            f"[{result_style}]{result_icon}[/{result_style}]" if result_style else result_icon,
        )

    console.print(t)


@app.command()
def form(
    club: str = typer.Option("FCSM", "--club", "-c"),
    season: str = typer.Option("2025", "--season", "-s"),
    last: int = typer.Option(5, "--last", "-n"),
):
    """📈 Forme récente d'un club."""
    data = _get(f"/clubs/{club}/form", {"season": season, "last": last})

    form_str = data["form_string"]
    form_colored = ""
    for c in form_str:
        color = {"W": "green", "D": "yellow", "L": "red"}[c]
        form_colored += f"[{color}]{c}[/{color}]"

    console.print(f"\n[bold]📈 Forme {data['club']} ({last} derniers matchs)[/bold]")
    console.print(f"Forme : {form_colored}")
    console.print(
        f"Bilan : [green]{data['wins']}V[/green] "
        f"[yellow]{data['draws']}N[/yellow] "
        f"[red]{data['losses']}D[/red]"
    )
    console.print(f"Buts  : [green]{data['goals_scored']}[/green] marqués / [red]{data['goals_conceded']}[/red] encaissés\n")


if __name__ == "__main__":
    app()
