import requests
import time
import random
from bs4 import BeautifulSoup
from supabase import create_client
from config import HEADERS, LOCATION, TIME_FILTER, EXPERIENCE_MAP, SEARCHES, SUPABASE_URL, SUPABASE_KEY


supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# 1: GET JOB IDs
# Hits Linkedin's guest API endpoint (no login needed) -> returns a list of job id's for your search.

def get_job_ids(keywords, experience, start=0):
    url = (
        f"https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"
        f"?keywords={keywords.replace(' ', '%20')}"
        f"&location={LOCATION}"
        f"&f_TPR={TIME_FILTER}"
        + (f"&f_E={experience}" if experience else "")
        + f"&sortBy=DD"
        f"&start={start}"
    )

    response = requests.get(url, headers=HEADERS)

    # If blocked it will return status 429 or 403
    if response.status_code != 200:
        print(f"Failed to fetch job list. Status: {response.status_code}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    job_cards = soup.find_all("li")

    id_list = []
    for card in job_cards:
        base_card = card.find("div", {"class": "base-card"})
        if base_card:
            job_id = base_card.get("data-entity-urn", "").split(":")[-1]
            if job_id:
                id_list.append(job_id)

    return id_list


# 2: GET JOB INFO
# separate guest API endpoint for each job id -> returns job posting -> parse out the fields we need
#
def get_job_details(job_id, category, experience):
    url = f"https://www.linkedin.com/jobs-guest/jobs/api/jobPosting/{job_id}"
    response = requests.get(url, headers=HEADERS)

    if response.status_code != 200:
        print(f"Could not fetch job {job_id}. Status: {response.status_code}")
        return None

    soup = BeautifulSoup(response.text, "html.parser")

    job = {"job_id": job_id}  # save job_id so supabase can deduplicate later

    # try/except for each field to avoid crashing the script if one field is missing
    try:
        job["job_title"] = soup.find(
            "h2", {"class": "top-card-layout__title"}
        ).text.strip()
    except AttributeError:
        job["job_title"] = None

    try:
        job["company_name"] = soup.find(
            "a", {"class": "topcard__org-name-link"}
        ).text.strip()
    except AttributeError:
        job["company_name"] = None

    try:
        job["location"] = soup.find(
            "span", {"class": "topcard__flavor--bullet"}
        ).text.strip()
    except AttributeError:
        job["location"] = None

    try:
        job["time_posted"] = soup.find(
            "span", {"class": "posted-time-ago__text"}
        ).text.strip()
    except AttributeError:
        job["time_posted"] = None

    try:
        job["num_applicants"] = soup.find(
            "span", {"class": "num-applicants__caption"}
        ).text.strip()
    except AttributeError:
        job["num_applicants"] = None

    # Direct link to apply
    job["job_url"] = f"https://www.linkedin.com/jobs/view/{job_id}"

    job["category"] = category
    job["experience_level"] = EXPERIENCE_MAP.get(experience)

    return job


# 3: SAVE TO SUPABASE
# upsert = insert if new, update if already exists
# on_conflict="job_id" means: if a row with this job_id exists, update it instead of creating a duplicate.

def save_to_supabase(jobs):
    saved = 0
    for job in jobs:
        try:
            supabase.table("linkedin_jobs").upsert(
                job, on_conflict="job_id"
            ).execute()
            saved += 1
        except Exception as e:
            print(f"Failed to save job {job.get('job_id')}: {e}")
    return saved



# ties everything together

def run_scraper():
    jobs = []
    
    for search in SEARCHES:
        print(f"Fetching job IDs for: {search['keywords']}...")
        job_ids = get_job_ids(
            keywords=search["keywords"],
            experience=search["experience"],
            start=0
        )
        print(f"Found {len(job_ids)} jobs")

        for i, job_id in enumerate(job_ids):
            print(f"Fetching details for job {i+1}/{len(job_ids)}: {job_id}")
            details = get_job_details(
                job_id,
                category=search["category"],
                experience=search["experience"]
            )
            if details:
                jobs.append(details)

            time.sleep(random.uniform(2, 5))

    saved = save_to_supabase(jobs)
    print(f"Saved {saved} jobs.")
