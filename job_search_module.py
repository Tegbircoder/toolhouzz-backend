import csv
import io
import urllib.parse
from datetime import datetime

# NOTE:
# We are NOT scraping job sites here (most block bots and cause errors on Render).
# Instead, we generate smart search links for the top boards.
# This keeps your API reliable and fast, and still gives users an actionable CSV.

JOB_SOURCES = [
    ("LinkedIn",  "https://www.linkedin.com/jobs/search/"),
    ("Indeed",    "https://ca.indeed.com/jobs"),
    ("Glassdoor", "https://www.glassdoor.ca/Job/jobs.htm"),
    ("Google Jobs", "https://www.google.com/search"),
]

def _clean_str(x: str) -> str:
    return (x or "").strip()

def _as_int(x, default=30):
    try:
        v = int(str(x).strip())
        return v if v > 0 else default
    except Exception:
        return default

def build_search_links(job_title: str, job_age_days: int, city: str, country: str):
    """
    Returns a list of dict rows:
      Date, Source, Company, Job Title, Location, Link, Notes
    We don't guess company (N/A). Links point to filtered searches on each site.
    """
    job_title = _clean_str(job_title) or "Business Analyst"
    city      = _clean_str(city)
    country   = _clean_str(country) or "Canada"
    job_age_days = _as_int(job_age_days, default=30)

    # Build human-friendly location
    location = ", ".join([p for p in [city, country] if p])

    query = job_title
    today = datetime.utcnow().strftime("%Y-%m-%d")

    rows = []

    # LinkedIn
    # We approximate filters. (LinkedIn also supports fancy filters via facets.)
    li_params = {
        "keywords": query,
        "location": location or country,
        "f_TPR": "r" + str(job_age_days * 24 * 60),  # recent in minutes (approx)
    }
    li_url = "https://www.linkedin.com/jobs/search/?" + urllib.parse.urlencode(li_params)

    # Indeed
    indeed_params = {
        "q": query,
        "l": location or country,
        "fromage": job_age_days,  # age in days
    }
    indeed_url = "https://ca.indeed.com/jobs?" + urllib.parse.urlencode(indeed_params)

    # Glassdoor
    gd_params = {
        "sc.keyword": query,
        "locT": "C",
        "locId": "",  # left blank; still works with free-text search
        "locKeyword": location or country,
        "fromAge": job_age_days,
    }
    gd_url = "https://www.glassdoor.ca/Job/jobs.htm?" + urllib.parse.urlencode(gd_params)

    # Google Jobs
    g_params = {
        "q": f'{query} jobs in {location or country}',
        "ibp": "htl;jobs",
        "tbs": f"qdr:d{job_age_days}",  # past N days
    }
    g_url = "https://www.google.com/search?" + urllib.parse.urlencode(g_params)

    link_map = [
        ("LinkedIn", li_url),
        ("Indeed", indeed_url),
        ("Glassdoor", gd_url),
        ("Google Jobs", g_url),
    ]

    for src, url in link_map:
        rows.append({
            "Date": today,
            "Source": src,
            "Company": "N/A",
            "Job Title": query,
            "Location": location or country,
            "Link": url,
            "Notes": f"Search results (past {job_age_days} days)"
        })

    return rows

def rows_to_csv(rows):
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=["Date","Source","Company","Job Title","Location","Link","Notes"])
    writer.writeheader()
    for r in rows:
        writer.writerow(r)
    return buf.getvalue()

def perform_job_search(payload: dict):
    """
    Main entry the Flask app calls.
    Payload keys (all optional, sensible defaults):
      job_title: str
      job_age: int (days)
      city: str
      country: str

    Returns: (rows, csv_text)
    """
    job_title = payload.get("job_title", "Business Analyst")
    job_age   = payload.get("job_age", 30)
    city      = payload.get("city", "")
    country   = payload.get("country", "Canada")

    rows = build_search_links(job_title, job_age, city, country)
    csv_text = rows_to_csv(rows)
    return rows, csv_text
