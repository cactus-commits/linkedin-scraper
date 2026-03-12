
import random
import os
from dotenv import load_dotenv

#--------------- SUPABASE CONFIG-----------------

load_dotenv()
SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]



#--------------- SEARCH PARAMETERS-----------------

LOCATION = "Stockholm"   # add your location
TIME_FILTER = "r10800"   # r10800 = last 3h | r86400 = 24h
EXPERIENCE_MAP = {
    "1": "Internship",
    "2": "Entry level", 
    "3": "Associate",
    "4": "Mid-Senior",
    "5": "Director",
}

SEARCHES = [ # change these with yours
    {"keywords": "data engineer", "experience": "4", "category": "tech"}, 
    {"keywords": "data analyst", "experience": "4", "category": "tech"}

]

#------------------- HEADERS ----------------------
# Purpose = disguise "python-requests" -> avoid getting blocked
# User-agents rotates 


USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/118.0.0.0 Safari/537.36",
]

HEADERS = {
    "User-Agent": random.choice(USER_AGENTS),  
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "DNT": "1",

}