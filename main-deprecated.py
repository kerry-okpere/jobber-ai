import aiohttp
import asyncio
from src.Scrapper.index import Scrapper

TARGET_ROLES = ["ai engineer", "llm engineer", "applied ai engineer"]
WATCH_LIST = [
    "jobs.ashbyhq.com",
    "jobs.lever.co",
    "job-boards.greenhouse.io",
    "apply.workable.com",
    "jobs.smartrecruiters.com",
    "myworkdayjobs.com",
    "breezy.hr",
    "recruitee.com",
    "personio.com",
    "recruiterbox.com",
    "jobvite.com",
    "iCIMS.com",
    "JazzHR.com",
    "jobdiva.com",
    "successfactors.com",
    "workforcenow.adp.com",
    "bamboohr.com",
    "brassring.com",
    "bullhorn.com",
    "taleo.net",
    "personio.de",
    "pinpointhq.com",
    "linkup.so",
    "join.com",
]

extra_filters = ("remote", "worldwide", "work from anywhere", "EMEA")
test_watch_list = WATCH_LIST[:5]  # Limit to first 5 sites for testing


async def main():
    async with aiohttp.ClientSession() as session:
        scrapper = Scrapper(session)
        semaphore = asyncio.Semaphore(3)

        async def bounded_search(site):
            async with semaphore:
                return await scrapper.search_jobs(
                    site=site,
                    roles=TARGET_ROLES,
                    # date_after="2026-05-31",
                    # date_before="2026-06-09",
                )

        tasks = [bounded_search(site) for site in test_watch_list]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        for site, result in zip(test_watch_list, results):
            if isinstance(result, Exception):
                print(f"Failed {site}: {result}")
            else:
                print(f"Processed {site}, {result}")


if __name__ == "__main__":
    asyncio.run(main())
