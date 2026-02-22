"""
Scraper squelette pour FFF / sites football.
Respecte robots.txt et les délais de politesse.
Usage : python scripts/scrape_fff.py
"""
import asyncio
import time
import httpx
from bs4 import BeautifulSoup

SOURCES = {
    "fff_national": "https://www.fff.fr/competition/national/",
    "footmercato": "https://www.footmercato.net/championnat/national/",
    "fcsm_officiel": "https://www.fcsochaux.fr/",
}

HEADERS = {
    "User-Agent": "fcsmtop-scraper/1.0 (https://github.com/jura39bot/fcsmtop-api; respectful bot)",
    "Accept-Language": "fr-FR,fr;q=0.9",
}

DELAY = 2.0  # secondes entre requêtes


async def check_robots(base_url: str, client: httpx.AsyncClient) -> bool:
    """Vérifie si le scraping est autorisé."""
    try:
        r = await client.get(f"{base_url.rstrip('/')}/robots.txt", timeout=5)
        if "fcsmtop" in r.text.lower() or "disallow: /" in r.text:
            print(f"⚠️  robots.txt restrictif sur {base_url}")
            return False
        return True
    except Exception:
        return True  # En cas d'absence de robots.txt


async def scrape_classement_national(client: httpx.AsyncClient) -> list[dict]:
    """Récupère le classement depuis la FFF (squelette — adapter selon la structure HTML réelle)."""
    url = "https://www.fff.fr/competition/national/classement.html"
    try:
        r = await client.get(url, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")

        # ⚠️ Le sélecteur CSS doit être adapté à la structure réelle du site
        rows = soup.select("table.classement tbody tr")
        results = []
        for i, row in enumerate(rows):
            cells = row.select("td")
            if len(cells) >= 8:
                results.append({
                    "rank": i + 1,
                    "team": cells[1].get_text(strip=True),
                    "played": cells[2].get_text(strip=True),
                    "won": cells[3].get_text(strip=True),
                    "drawn": cells[4].get_text(strip=True),
                    "lost": cells[5].get_text(strip=True),
                    "goals_for": cells[6].get_text(strip=True),
                    "goals_against": cells[7].get_text(strip=True),
                    "points": cells[8].get_text(strip=True) if len(cells) > 8 else "?",
                })
        return results
    except Exception as e:
        print(f"❌ Erreur scraping classement: {e}")
        return []


async def scrape_buteurs_national(client: httpx.AsyncClient) -> list[dict]:
    """Scrape les buteurs du National (squelette)."""
    # TODO: adapter le sélecteur au site réel
    print("ℹ️  scrape_buteurs_national — à implémenter selon la structure du site cible")
    return []


async def main():
    print("🕷️  fcsmtop scraper — démarrage")
    async with httpx.AsyncClient(headers=HEADERS, follow_redirects=True) as client:
        # Vérification robots.txt
        for name, url in SOURCES.items():
            allowed = await check_robots(url, client)
            print(f"{'✅' if allowed else '⛔'} {name}: {'OK' if allowed else 'Bloqué par robots.txt'}")
            await asyncio.sleep(DELAY)

        # Scraping classement (squelette)
        print("\n📊 Scraping classement National...")
        classement = await scrape_classement_national(client)
        if classement:
            print(f"   {len(classement)} équipes trouvées")
            for row in classement[:3]:
                print(f"   {row['rank']}. {row['team']} — {row['points']} pts")
        else:
            print("   Aucun résultat (sélecteur à adapter)")

        await asyncio.sleep(DELAY)

        print("\n✅ Scraping terminé.")
        print("ℹ️  Adapter les sélecteurs CSS dans ce fichier selon la structure HTML réelle des sites.")


if __name__ == "__main__":
    asyncio.run(main())
