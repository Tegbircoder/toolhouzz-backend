import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import urllib.parse

def create_driver():
    """Create a headless Chrome driver for automation"""
    chrome_options = Options()
    
    # Headless mode (no visible browser)
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    
    # Anti-detection measures
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    # User agent
    chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    
    driver = webdriver.Chrome(options=chrome_options)
    
    # Execute script to hide automation
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    return driver

def scrape_linkedin_jobs(driver, job_title, location, max_jobs=20):
    """Scrape LinkedIn jobs with browser automation"""
    jobs = []
    encoded_title = urllib.parse.quote(job_title)
    encoded_location = urllib.parse.quote(location)
    
    url = f'https://www.linkedin.com/jobs/search/?keywords={encoded_title}&location={encoded_location}&f_TPR=r604800'
    
    try:
        print(f"[LinkedIn] Opening browser and navigating...")
        driver.get(url)
        
        # Wait for job cards to load
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CLASS_NAME, "job-search-card"))
        )
        
        print(f"[LinkedIn] Extracting job data...")
        
        # Scroll to load more jobs
        for i in range(3):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1)
        
        # Find all job cards
        job_cards = driver.find_elements(By.CLASS_NAME, "job-search-card")[:max_jobs]
        
        for card in job_cards:
            try:
                # Extract title
                try:
                    title_elem = card.find_element(By.CLASS_NAME, "base-search-card__title")
                    title = title_elem.text.strip()
                except:
                    title = "N/A"
                
                # Extract company
                try:
                    company_elem = card.find_element(By.CLASS_NAME, "base-search-card__subtitle")
                    company = company_elem.text.strip()
                except:
                    company = "N/A"
                
                # Extract location
                try:
                    location_elem = card.find_element(By.CLASS_NAME, "job-search-card__location")
                    job_location = location_elem.text.strip()
                except:
                    job_location = location
                
                # Extract URL
                try:
                    link_elem = card.find_element(By.CLASS_NAME, "base-card__full-link")
                    job_url = link_elem.get_attribute("href")
                except:
                    job_url = url
                
                jobs.append({
                    'date': datetime.now().strftime('%m/%d/%Y'),
                    'source': 'LinkedIn',
                    'company': company,
                    'title': title,
                    'location': job_location,
                    'url': job_url,
                    'detected_term': job_title,
                    'posted_utc': datetime.utcnow().isoformat()
                })
                
            except Exception as e:
                print(f"[LinkedIn] Error extracting job: {str(e)}")
                continue
        
        print(f"[LinkedIn] ✓ Extracted {len(jobs)} jobs")
        
    except Exception as e:
        print(f"[LinkedIn] ✗ Error: {str(e)}")
    
    return jobs

def scrape_indeed_jobs(driver, job_title, location, max_jobs=20):
    """Scrape Indeed jobs with browser automation"""
    jobs = []
    encoded_title = urllib.parse.quote(job_title)
    encoded_location = urllib.parse.quote(location)
    
    url = f'https://ca.indeed.com/jobs?q={encoded_title}&l={encoded_location}&fromage=15'
    
    try:
        print(f"[Indeed] Opening browser and navigating...")
        driver.get(url)
        
        # Wait for job cards to load
        time.sleep(3)
        
        print(f"[Indeed] Extracting job data...")
        
        # Find all job cards
        job_cards = driver.find_elements(By.CLASS_NAME, "job_seen_beacon")[:max_jobs]
        
        for card in job_cards:
            try:
                # Extract title
                try:
                    title_elem = card.find_element(By.CSS_SELECTOR, "h2.jobTitle span")
                    title = title_elem.text.strip()
                except:
                    title = "N/A"
                
                # Extract company
                try:
                    company_elem = card.find_element(By.CSS_SELECTOR, "span[data-testid='company-name']")
                    company = company_elem.text.strip()
                except:
                    company = "N/A"
                
                # Extract location
                try:
                    location_elem = card.find_element(By.CSS_SELECTOR, "div[data-testid='text-location']")
                    job_location = location_elem.text.strip()
                except:
                    job_location = location
                
                # Extract URL
                try:
                    link_elem = card.find_element(By.CSS_SELECTOR, "h2.jobTitle a")
                    job_url = "https://ca.indeed.com" + link_elem.get_attribute("href")
                except:
                    job_url = url
                
                jobs.append({
                    'date': datetime.now().strftime('%m/%d/%Y'),
                    'source': 'Indeed',
                    'company': company,
                    'title': title,
                    'location': job_location,
                    'url': job_url,
                    'detected_term': job_title,
                    'posted_utc': datetime.utcnow().isoformat()
                })
                
            except Exception as e:
                print(f"[Indeed] Error extracting job: {str(e)}")
                continue
        
        print(f"[Indeed] ✓ Extracted {len(jobs)} jobs")
        
    except Exception as e:
        print(f"[Indeed] ✗ Error: {str(e)}")
    
    return jobs

def scrape_glassdoor_jobs(driver, job_title, location, max_jobs=20):
    """Scrape Glassdoor jobs with browser automation"""
    jobs = []
    encoded_title = urllib.parse.quote(job_title)
    
    url = f'https://www.glassdoor.ca/Job/jobs.htm?sc.keyword={encoded_title}&locT=N&locId=3&fromAge=15'
    
    try:
        print(f"[Glassdoor] Opening browser and navigating...")
        driver.get(url)
        
        # Wait for job cards to load
        time.sleep(5)
        
        print(f"[Glassdoor] Extracting job data...")
        
        # Find all job cards - Glassdoor uses different selectors
        job_cards = driver.find_elements(By.CSS_SELECTOR, "li[data-test='jobListing']")[:max_jobs]
        
        for card in job_cards:
            try:
                # Extract title
                try:
                    title_elem = card.find_element(By.CSS_SELECTOR, "a[data-test='job-title']")
                    title = title_elem.text.strip()
                except:
                    title = "N/A"
                
                # Extract company
                try:
                    company_elem = card.find_element(By.CSS_SELECTOR, "div[data-test='employer-name']")
                    company = company_elem.text.strip()
                except:
                    company = "N/A"
                
                # Extract location
                try:
                    location_elem = card.find_element(By.CSS_SELECTOR, "div[data-test='emp-location']")
                    job_location = location_elem.text.strip()
                except:
                    job_location = location
                
                # Extract URL
                try:
                    link_elem = card.find_element(By.CSS_SELECTOR, "a[data-test='job-title']")
                    job_url = "https://www.glassdoor.ca" + link_elem.get_attribute("href")
                except:
                    job_url = url
                
                jobs.append({
                    'date': datetime.now().strftime('%m/%d/%Y'),
                    'source': 'Glassdoor',
                    'company': company,
                    'title': title,
                    'location': job_location,
                    'url': job_url,
                    'detected_term': job_title,
                    'posted_utc': datetime.utcnow().isoformat()
                })
                
            except Exception as e:
                print(f"[Glassdoor] Error extracting job: {str(e)}")
                continue
        
        print(f"[Glassdoor] ✓ Extracted {len(jobs)} jobs")
        
    except Exception as e:
        print(f"[Glassdoor] ✗ Error: {str(e)}")
    
    return jobs

def generate_search_links(job_title, location):
    """Generate search links for portals we don't scrape"""
    encoded_title = urllib.parse.quote(job_title)
    encoded_location = urllib.parse.quote(location)
    
    portals = {
        'Monster': f'https://www.monster.com/jobs/search/?q={encoded_title}&where={encoded_location}&dy=15',
        'ZipRecruiter': f'https://www.ziprecruiter.com/jobs-search?search={encoded_title}&location={encoded_location}&days=15',
        'SimplyHired': f'https://www.simplyhired.com/search?q={encoded_title}&l={encoded_location}&fdb=15',
        'JobBank': f'https://www.jobbank.gc.ca/jobsearch/jobsearch?searchstring={encoded_title}&locationstring={encoded_location}',
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
            'detected_term': job_title,
            'posted_utc': datetime.utcnow().isoformat()
        })
    
    return jobs

def search_all_portals(job_title, location, job_age=15):
    """Main function to search all portals with browser automation"""
    print(f"\n{'='*60}")
    print(f"Starting BROWSER AUTOMATION job search for: {job_title}")
    print(f"Location: {location}")
    print(f"Job age: Last {job_age} days")
    print(f"{'='*60}\n")
    
    all_jobs = []
    
    try:
        # Create browser driver
        print("[BROWSER] Creating Chrome driver...")
        driver = create_driver()
        
        # Scrape LinkedIn
        print("[BROWSER] Scraping LinkedIn...")
        linkedin_jobs = scrape_linkedin_jobs(driver, job_title, location)
        all_jobs.extend(linkedin_jobs)
        time.sleep(2)
        
        # Scrape Indeed
        print("[BROWSER] Scraping Indeed...")
        indeed_jobs = scrape_indeed_jobs(driver, job_title, location)
        all_jobs.extend(indeed_jobs)
        time.sleep(2)
        
        # Scrape Glassdoor
        print("[BROWSER] Scraping Glassdoor...")
        glassdoor_jobs = scrape_glassdoor_jobs(driver, job_title, location)
        all_jobs.extend(glassdoor_jobs)
        
        # Close browser
        print("[BROWSER] Closing browser...")
        driver.quit()
        
    except Exception as e:
        print(f"[BROWSER] Error: {str(e)}")
        try:
            driver.quit()
        except:
            pass
    
    # Add search links for other portals
    print("[LINKS] Adding search links for other portals...")
    search_links = generate_search_links(job_title, location)
    all_jobs.extend(search_links)
    
    print(f"\n{'='*60}")
    print(f"Search complete! Total results: {len(all_jobs)}")
    scraped_count = sum(1 for job in all_jobs if job['company'] != '🔗 Click to Search')
    link_count = len(all_jobs) - scraped_count
    print(f"Automated scraping: {scraped_count} jobs")
    print(f"Search links: {link_count} portals")
    print(f"{'='*60}\n")
    
    return all_jobs

def test_search():
    """Test function"""
    results = search_all_portals(
        job_title="Data Analyst",
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

if __name__ == '__main__':
    test_search()
