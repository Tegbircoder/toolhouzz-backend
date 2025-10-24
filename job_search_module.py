import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import time
import urllib.parse

# Headers to mimic a real browser
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1'
}

def portal_search_links(job_title, location, job_age):
    """
    Generate search URLs for 23+ job portals.
    """
    encoded_title = urllib.parse.quote(job_title)
    encoded_location = urllib.parse.quote(location)
    
    portals = {
        'LinkedIn': f'https://www.linkedin.com/jobs/search/?keywords={encoded_title}&location={encoded_location}&f_TPR=r{job_age * 86400}',
        'Indeed': f'https://www.indeed.com/jobs?q={encoded_title}&l={encoded_location}&fromage={job_age}',
        'Glassdoor': f'https://www.glassdoor.com/Job/jobs.htm?sc.keyword={encoded_title}&locT=C&locId=&jobType=&fromAge={job_age}',
        'Monster': f'https://www.monster.com/jobs/search/?q={encoded_title}&where={encoded_location}&dy={job_age}',
        'Eluta': f'https://www.eluta.ca/search?keywords={encoded_title}&location={encoded_location}',
        'JobBank': f'https://www.jobbank.gc.ca/jobsearch/jobsearch?searchstring={encoded_title}&locationstring={encoded_location}',
        'ZipRecruiter': f'https://www.ziprecruiter.com/jobs-search?search={encoded_title}&location={encoded_location}&days={job_age}',
        'SimplyHired': f'https://www.simplyhired.com/search?q={encoded_title}&l={encoded_location}&fdb={job_age}',
        'Jobboom': f'https://www.jobboom.com/en/job-search?keywords={encoded_title}&locations={encoded_location}',
        'Workopolis': f'https://www.workopolis.com/jobsearch/jobs?ak={encoded_title}&l={encoded_location}',
        'Talent.com': f'https://www.talent.com/jobs?k={encoded_title}&l={encoded_location}',
        'CareerBuilder': f'https://www.careerbuilder.com/jobs?keywords={encoded_title}&location={encoded_location}&posted={job_age}',
        'Robert Half': f'https://www.roberthalf.com/us/en/jobs?keywords={encoded_title}&location={encoded_location}',
        'TalentEgg': f'https://talentegg.ca/jobs/?keywords={encoded_title}&location={encoded_location}',
        'Snagajob': f'https://www.snagajob.com/job-seeker/jobs?keywords={encoded_title}&location={encoded_location}',
        'Careerjet': f'https://www.careerjet.com/search/jobs?s={encoded_title}&l={encoded_location}',
        'Dice': f'https://www.dice.com/jobs?q={encoded_title}&location={encoded_location}&radius=30&radiusUnit=mi&page=1&pageSize=20&filters.postedDate=SEVEN',
        'Upwork': f'https://www.upwork.com/nx/search/jobs/?q={encoded_title}&location={encoded_location}',
        'FlexJobs': f'https://www.flexjobs.com/search?search={encoded_title}&location={encoded_location}',
        'Kijiji': f'https://www.kijiji.ca/b-jobs/{encoded_location}/{encoded_title}/k0c45l0',
        'Workable': f'https://jobs.workable.com/search?query={encoded_title}&location={encoded_location}',
        'RBC': f'https://jobs.rbc.com/ca/en/search-results?keywords={encoded_title}',
        'TD Bank': f'https://jobs.td.com/en-CA/jobs?keywords={encoded_title}&location={encoded_location}',
        'BMO': f'https://jobs.bmo.com/ca/en/search-results?keywords={encoded_title}',
    }
    
    return portals

def scrape_generic_jobs(url, source_name):
    """
    Generic scraper for job portals. Attempts to extract job listings.
    Returns a list of job dictionaries.
    """
    jobs = []
    
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        
        if response.status_code != 200:
            print(f"[{source_name}] Failed to fetch: {response.status_code}")
            return []
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Common patterns for job listings (adjust as needed)
        job_containers = []
        
        # Try multiple common selectors
        selectors = [
            'div.job',
            'div[class*="job"]',
            'li[class*="job"]',
            'article',
            'div[class*="result"]',
            'div[class*="listing"]'
        ]
        
        for selector in selectors:
            containers = soup.select(selector)
            if len(containers) > 3:  # If we found meaningful results
                job_containers = containers[:20]  # Limit to 20
                break
        
        if not job_containers:
            print(f"[{source_name}] No job containers found")
            return []
        
        print(f"[{source_name}] Found {len(job_containers)} potential jobs")
        
        for container in job_containers:
            try:
                # Try to extract title
                title_elem = (
                    container.find('h2') or 
                    container.find('h3') or 
                    container.find('a', class_=lambda x: x and 'title' in x.lower()) or
                    container.find('a')
                )
                title = title_elem.get_text(strip=True) if title_elem else 'N/A'
                
                # Try to extract company
                company_elem = (
                    container.find('span', class_=lambda x: x and 'company' in x.lower()) or
                    container.find('div', class_=lambda x: x and 'company' in x.lower())
                )
                company = company_elem.get_text(strip=True) if company_elem else 'N/A'
                
                # Try to extract location
                location_elem = (
                    container.find('span', class_=lambda x: x and 'location' in x.lower()) or
                    container.find('div', class_=lambda x: x and 'location' in x.lower())
                )
                location = location_elem.get_text(strip=True) if location_elem else 'N/A'
                
                # Try to extract URL
                link_elem = container.find('a', href=True)
                job_url = link_elem['href'] if link_elem else url
                
                # Make URL absolute if relative
                if job_url.startswith('/'):
                    from urllib.parse import urljoin
                    job_url = urljoin(url, job_url)
                
                jobs.append({
                    'date': datetime.now().strftime('%Y-%m-%d'),
                    'source': source_name,
                    'company': company,
                    'title': title,
                    'location': location,
                    'url': job_url,
                    'detected_term': '',
                    'posted_utc': datetime.utcnow().isoformat()
                })
                
            except Exception as e:
                print(f"[{source_name}] Error parsing job: {str(e)}")
                continue
        
        return jobs
    
    except requests.Timeout:
        print(f"[{source_name}] Request timed out")
        return []
    except Exception as e:
        print(f"[{source_name}] Error: {str(e)}")
        return []

def search_all_portals(job_title, location, job_age=15):
    """
    Search all 23+ job portals and return combined results.
    """
    print(f"\n{'='*60}")
    print(f"Starting job search for: {job_title}")
    print(f"Location: {location}")
    print(f"Job age: Last {job_age} days")
    print(f"{'='*60}\n")
    
    all_jobs = []
    portals = portal_search_links(job_title, location, job_age)
    
    # Search each portal
    for portal_name, portal_url in portals.items():
        print(f"[{portal_name}] Searching...")
        
        try:
            jobs = scrape_generic_jobs(portal_url, portal_name)
            
            if jobs:
                print(f"[{portal_name}] ✓ Found {len(jobs)} jobs")
                for job in jobs:
                    job['detected_term'] = job_title
                all_jobs.extend(jobs)
            else:
                print(f"[{portal_name}] ✗ No jobs found")
            
            # Small delay to avoid rate limiting
            time.sleep(0.5)
            
        except Exception as e:
            print(f"[{portal_name}] Error: {str(e)}")
            continue
    
    print(f"\n{'='*60}")
    print(f"Search complete! Total jobs found: {len(all_jobs)}")
    print(f"{'='*60}\n")
    
    # If no results from scraping, create placeholder results
    if len(all_jobs) == 0:
        print("[INFO] Creating sample results since no jobs were scraped...")
        
        # Generate direct search URLs for major portals
        all_jobs = []
        major_portals = {
            'LinkedIn': f'https://www.linkedin.com/jobs/search/?keywords={urllib.parse.quote(job_title)}&location={urllib.parse.quote(location)}',
            'Indeed': f'https://www.indeed.com/jobs?q={urllib.parse.quote(job_title)}&l={urllib.parse.quote(location)}',
            'Glassdoor': f'https://www.glassdoor.com/Job/jobs.htm?sc.keyword={urllib.parse.quote(job_title)}',
            'Monster': f'https://www.monster.com/jobs/search/?q={urllib.parse.quote(job_title)}&where={urllib.parse.quote(location)}',
            'ZipRecruiter': f'https://www.ziprecruiter.com/jobs-search?search={urllib.parse.quote(job_title)}&location={urllib.parse.quote(location)}',
        }
        
        for portal_name, url in major_portals.items():
            all_jobs.append({
                'date': datetime.now().strftime('%Y-%m-%d'),
                'source': portal_name,
                'company': 'Visit Portal',
                'title': f'{job_title} - Click URL to search {portal_name}',
                'location': location,
                'url': url,
                'detected_term': job_title,
                'posted_utc': datetime.utcnow().isoformat()
            })
    
    return all_jobs

def test_search():
    """Test function for local testing"""
    results = search_all_portals(
        job_title="Business Analyst",
        location="Toronto, Canada",
        job_age=15
    )
    
    print(f"\nTotal results: {len(results)}")
    
    if results:
        print("\nFirst 5 results:")
        for i, job in enumerate(results[:5], 1):
            print(f"\n{i}. {job['title']}")
            print(f"   Company: {job['company']}")
            print(f"   Source: {job['source']}")
            print(f"   URL: {job['url']}")

if __name__ == '__main__':
    test_search()
