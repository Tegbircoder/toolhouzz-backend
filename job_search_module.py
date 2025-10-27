import requests
from datetime import datetime
import urllib.parse

# Adzuna API credentials
ADZUNA_APP_ID = "98fe5840"  # Replace with your actual app_id
ADZUNA_API_KEY = "d968bfc5a0fd5bf7773bc54fbfa36a7d"	  # Replace with your actual api_key

def search_adzuna_jobs(job_title, location, max_results=50):
    """
    Search jobs using Adzuna API (FREE - 500 searches/month)
    Covers: Indeed, Monster, Glassdoor, CareerBuilder, and 50+ sites!
    """
    jobs = []
    
    # Determine country code based on location
    if "canada" in location.lower() or "ca" in location.lower():
        country = "ca"
    elif "uk" in location.lower() or "united kingdom" in location.lower():
        country = "gb"
    elif "australia" in location.lower() or "au" in location.lower():
        country = "au"
    elif "usa" in location.lower() or "united states" in location.lower() or "us" in location.lower():
        country = "us"
    else:
        country = "ca"  # Default to Canada
    
    print(f"\n{'='*60}")
    print(f"🔍 Searching Adzuna API for: {job_title}")
    print(f"📍 Location: {location} (Country: {country.upper()})")
    print(f"{'='*60}\n")
    
    try:
        # Adzuna API endpoint
        url = f"https://api.adzuna.com/v1/api/jobs/{country}/search/1"
        
        params = {
            'app_id': ADZUNA_APP_ID,
            'app_key': ADZUNA_API_KEY,
            'results_per_page': max_results,
            'what': job_title,
            'where': location,
            'max_days_old': 15,
            'sort_by': 'date'
        }
        
        print(f"[Adzuna] Making API request...")
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code != 200:
            print(f"[Adzuna] ❌ API Error: Status {response.status_code}")
            print(f"[Adzuna] Response: {response.text}")
            return generate_search_links(job_title, location)
        
        data = response.json()
        results = data.get('results', [])
        
        print(f"[Adzuna] ✅ Found {len(results)} jobs from Adzuna API!")
        print(f"[Adzuna] (Sources: Indeed, Monster, Glassdoor, CareerBuilder, etc.)\n")
        
        for job in results:
            try:
                # Extract job details
                title = job.get('title', 'N/A')
                company = job.get('company', {}).get('display_name', 'N/A')
                job_location = job.get('location', {}).get('display_name', location)
                job_url = job.get('redirect_url', '')
                description = job.get('description', '')[:200] + '...'
                
                # Salary info (if available)
                salary_min = job.get('salary_min')
                salary_max = job.get('salary_max')
                salary_str = ''
                if salary_min and salary_max:
                    salary_str = f"${salary_min:,.0f}-${salary_max:,.0f}"
                elif salary_min:
                    salary_str = f"${salary_min:,.0f}+"
                
                jobs.append({
                    'date': datetime.now().strftime('%m/%d/%Y'),
                    'source': 'Adzuna',
                    'company': company,
                    'title': title,
                    'location': job_location,
                    'url': job_url,
                    'salary': salary_str,
                    'description': description,
                    'detected_term': job_title,
                    'posted_utc': datetime.utcnow().isoformat()
                })
                
            except Exception as e:
                print(f"[Adzuna] Warning: Error parsing job: {str(e)}")
                continue
        
        print(f"[Adzuna] ✅ Successfully extracted {len(jobs)} jobs!\n")
        
    except requests.Timeout:
        print(f"[Adzuna] ❌ Request timed out")
        return generate_search_links(job_title, location)
    except Exception as e:
        print(f"[Adzuna] ❌ Error: {str(e)}")
        return generate_search_links(job_title, location)
    
    # Add search links for additional portals not in Adzuna
    print(f"[Links] Adding search links for additional portals...\n")
    additional_links = generate_search_links(job_title, location)
    jobs.extend(additional_links)
    
    return jobs

def generate_search_links(job_title, location):
    """
    Generate direct search links for job portals
    """
    encoded_title = urllib.parse.quote(job_title)
    encoded_location = urllib.parse.quote(location)
    
    portals = {
        'LinkedIn': f'https://www.linkedin.com/jobs/search/?keywords={encoded_title}&location={encoded_location}&f_TPR=r604800',
        'JobBank': f'https://www.jobbank.gc.ca/jobsearch/jobsearch?searchstring={encoded_title}&locationstring={encoded_location}',
        'ZipRecruiter': f'https://www.ziprecruiter.com/jobs-search?search={encoded_title}&location={encoded_location}&days=15',
        'SimplyHired': f'https://www.simplyhired.com/search?q={encoded_title}&l={encoded_location}&fdb=15',
        'Workopolis': f'https://www.workopolis.com/jobsearch/jobs?ak={encoded_title}&l={encoded_location}',
    }
    
    jobs = []
    for portal_name, portal_url in portals.items():
        jobs.append({
            'date': datetime.now().strftime('%m/%d/%Y'),
            'source': portal_name,
            'company': '🔗 Click to Search',
            'title': f'Search {portal_name} for "{job_title}"',
            'location': location,
            'url': portal_url,
            'salary': '',
            'description': '',
            'detected_term': job_title,
            'posted_utc': datetime.utcnow().isoformat()
        })
    
    return jobs

def search_all_portals(job_title, location, job_age=15):
    """
    Main search function - uses Adzuna API
    """
    print(f"\n{'='*60}")
    print(f"🚀 ADZUNA API JOB SEARCH")
    print(f"Job Title: {job_title}")
    print(f"Location: {location}")
    print(f"Job Age: Last {job_age} days")
    print(f"{'='*60}\n")
    
    # Search using Adzuna API
    all_jobs = search_adzuna_jobs(job_title, location, max_results=50)
    
    print(f"\n{'='*60}")
    print(f"✅ SEARCH COMPLETE!")
    print(f"📊 Total Results: {len(all_jobs)}")
    
    adzuna_count = sum(1 for job in all_jobs if job['source'] == 'Adzuna')
    link_count = len(all_jobs) - adzuna_count
    
    print(f"   - Adzuna API jobs: {adzuna_count}")
    print(f"   - Search links: {link_count}")
    print(f"{'='*60}\n")
    
    return all_jobs

def test_search():
    """Test function for local testing"""
    results = search_all_portals(
        job_title="Data Analyst",
        location="Toronto, Canada",
        job_age=15
    )
    
    print(f"\n📊 RESULTS SUMMARY:")
    print(f"Total jobs: {len(results)}")
    
    if results:
        print(f"\n✅ First 5 results:")
        for i, job in enumerate(results[:5], 1):
            print(f"\n{i}. {job['title']}")
            print(f"   Company: {job['company']}")
            print(f"   Location: {job['location']}")
            print(f"   Source: {job['source']}")
            if job.get('salary'):
                print(f"   Salary: {job['salary']}")

if __name__ == '__main__':
    test_search()
