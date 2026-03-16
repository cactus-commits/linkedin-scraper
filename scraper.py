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

    # Blocked? status 429 or 403
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



