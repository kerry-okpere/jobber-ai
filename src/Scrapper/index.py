import aiohttp
import os
from dotenv import load_dotenv
from bs4 import BeautifulSoup

load_dotenv()
serpapi_key = os.getenv("SERPAPI_KEY")


class Scrapper:
    def __init__(self, session: aiohttp.ClientSession):
        self.session = session

    def title_matches_roles(self, title: str, roles: list[str]) -> bool:
        title_lower = title.lower()
        return any(role in title_lower for role in roles)

    async def get_job_description(self, url: str) -> str:
        async with self.session.get(url) as response:
            response.raise_for_status()
            html_content = await response.text()

        soup = BeautifulSoup(html_content, "html.parser")
        return soup.get_text()

    async def search_jobs(
        self,
        site: str,
        roles: list[str],
        date_after: str = None,
        date_before: str = None,
        extra_filters: str = None,
    ) -> list[dict]:
        all_results = []
        seen = set()

        for role in roles:
            query = f"{role} site:{site}"
            if extra_filters:
                query += f" {extra_filters}"

            params = {
                "q": query,
                "num": 20,
                "api_key": serpapi_key,
            }
            if date_after:
                params["tbs"] = f"cdr:1,cd_min:{date_after},cd_max:{date_before or ''}"

            print(f"Query: {query}")
            async with self.session.get(
                "https://serpapi.com/search",
                params=params,
            ) as resp:
                if not resp.ok:
                    body = await resp.text()
                    raise Exception(f"SerpAPI {resp.status}: {body}")
                data = await resp.json()

            for r in data.get("organic_results", []):
                link = r.get("link", "")
                if link in seen:
                    continue
                seen.add(link)
                all_results.append({
                    "title": r.get("title", ""),
                    "link": link,
                    "snippet": r.get("snippet", ""),
                    "date": r.get("date", ""),
                })

        return [r for r in all_results if self.title_matches_roles(r["title"], roles)]
