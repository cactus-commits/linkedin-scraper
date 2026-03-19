# LinkedIn Job Scraper

Scrapes LinkedIn job postings on a schedule and persists them to Supabase - no LinkedIn account or API key required.

---

## How it works

Uses LinkedIn's unauthenticated guest API endpoints to fetch job listings by keyword, location, and experience level. Runs automatically via GitHub Actions and upserts results into a Supabase table, deduplicating by `job_id`.

Pipeline:
1. Fetch job IDs matching your search criteria
2. Fetch full details for each job ID
3. Upsert into Supabase (`linkedin_jobs` table)

---

## Use this as a template

### 1. Supabase setup

Create a `linkedin_jobs` table with at minimum:

```sql
create table linkedin_jobs (
  job_id text primary key,
  job_title text,
  company_name text,
  location text,
  time_posted text,
  num_applicants text,
  job_url text,
  category text,
  experience_level text
);
```

### 2. Configure your searches

Edit [config.py](config.py):

```python
LOCATION = "Stockholm"       # your city
TIME_FILTER = "r86400"       # r3600=1h | r10800=3h | r86400=24h

SEARCHES = [
    {"keywords": "backend engineer", "experience": "4", "category": "tech"},
    {"keywords": "data analyst",     "experience": "2", "category": "tech"},
]

# Experience levels: 1=Internship 2=Entry 3=Associate 4=Mid-Senior 5=Director
```

### 3. Environment variables

```bash
cp .env.example .env
# Add your SUPABASE_URL and SUPABASE_KEY
```

For GitHub Actions, add both as **repository secrets** (`Settings → Secrets → Actions`).

### 4. Run locally

```bash
uv sync
uv run scraper.py
```

### 5. Automate with GitHub Actions

The included [workflow](.github/workflows/scraper.yml) runs on a cron schedule. Change the schedule to suit your needs:

```yaml
schedule:
  - cron: "0 */8 * * *"  # every 8 hours
```

Trigger manually anytime from the **Actions** tab in GitHub.

> **Keep these in sync:** `TIME_FILTER` in `config.py` and the cron interval must align. The cron interval should be ≤ the time filter window - if you run every 8 hours, set `TIME_FILTER = "r28800"`. Running more frequently than the window just re-fetches the same jobs (harmless, but wasteful). Running less frequently creates gaps where postings get missed.

---

## Stack

- **Python 3.12** - scraping with `requests` + `BeautifulSoup4`
- **Supabase** - persistence with upsert deduplication
- **GitHub Actions** - scheduling

---

## Caveats

LinkedIn's guest API is undocumented and can change or start rate-limiting without notice. The scraper uses rotating user-agents (99.9% useless but hey, why not) and random delays between requests to stay under the radar - but it's not guaranteed. If you start getting `429`/`403` responses, back off the schedule.
