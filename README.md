# TODO
# Fetch => Filter => Scrape -> convert to MD -> extract data -> store -> notify
# Use Serper to get the top 20 companies that are hiring for a specific role
# use the filter format 'ai engineer OR llm engineer site:ashbyhq.com after:2026-05-31 before:2026-06-09'
# Extract the title, date posted and link and run it through an LLM to confirm that the role is relevant to the query
# Save to a redis or a queue instance for temporary storage 
# Go through each of the links and use beautiful soup 
# and html-to-markdown to convert to mark down
# Use a low level free AI to extract entities from the JD .md Technical skills list, date posted, company name, job title, and 
# salary, remote or on site, and other critical entries in a JSON format.
# Store this as an entry on google sheet 


# The UI will allow you to connect your google sheet account, 
# allow you enter roles with comma spaced (that change to selectable tags in a dropdown)
# Allow you to select a date range for now with a max of one week 
# connect your whatsapp account to send you notifications when new jobs are posted that match your criteria.

# expose an API that allows the use to ask questions about the job on the sheet
# eg what are the top skills companies are hiring for in ... role
# it comes to the AI agent and they can review the excel sheet and process the information using RAG

Deduplication — if you run this daily, the same job will re-appear. You need a way to skip already-seen URLs before writing to Sheets (a simple set of seen URLs in Redis, a local file, or a Sheets lookup works)

allow user to save data in their own excel as DB 
Create an excel that data has an on going report
save the user preference (keywords) supabase 
save the user 

https://zernio.com/blog/whatsapp-api-tutorial-how-to-send-messages-and-templates



- Get jobs posted everyday that I can apply to as they are opened in whatsapp or email
- Market intelligence on what tools these companies use for AI engineering so I can learn them 
- Post on Linkedin and Instagram about the Jobber AI I built or the IDea of applying as jobs become available with my affiliate link https://theirstack.com?aff=hA6EfhybhFxo



JSearch (via RapidAPI): real-time, Google-for-Jobs backed, and it returns a clean job_posted_at_datetime_utc timestamp on every record. Good fit for on-demand queries. Slab

TheirStack: aggregates from 315,000+ sources including 16,000+ ATS platforms, deduplicates automatically, updates every minute, and lets you filter jobs by company size, funding stage, industry, and tech stack. That company-attribute filtering is gold for market research. Fantastic

Coresignal: 399M+ job posting records with enrichment, but pricey, working out to roughly $0.08 per job at volume, and double that for multi-source enriched records. CavunoFantastic

Techmap / jobdatafeeds: historical job data going back to 2020, useful for trend analysis. Cavuno

search: 
react site:greenhouse.io after:2026-06-07 before:2026-06-09 remote
frontend site:greenhouse.io after:2026-06-07 before:2026-06-09 remote
react site:greenhouse.io after:2026-06-07 before:2026-06-09
product engineer site:greenhouse.io after:2026-06-07 before:2026-06-09 