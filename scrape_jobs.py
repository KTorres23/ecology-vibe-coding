"""
Scraper script to fetch jobs from Texas A&M Natural Resources Job Board
and save them as a static JSON file for use in the web frontend.
"""

import requests
from bs4 import BeautifulSoup
import re
import json

JOBS_URL = "https://jobs.rwfm.tamu.edu/search/"
OUTPUT_FILE = "jobs.json"
PAGESIZE = 100  # Number of jobs per page
MAX_PAGES = 2   # Only fetch the most recent 2 pages (newest ~200 jobs)


def scrape_jobs():
    """Fetch and parse recent jobs from the TAMU job board (most recent postings only)."""
    all_jobs = []
    seen = set()
    
    for page in range(1, MAX_PAGES + 1):
        try:
            headers = {'User-Agent': 'ecology-vibe-coding/1.0 (+https://github.com/KTorres23)'}
            params = {'pagesize': PAGESIZE, 'page': page}
            resp = requests.get(JOBS_URL, params=params, headers=headers, timeout=10)
            resp.raise_for_status()
        except Exception as e:
            print(f"Error fetching page {page}: {e}")
            break
        
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        # Find all 'View' links to individual job postings
        for a in soup.find_all('a', href=re.compile(r'view-job')):
            href = a.get('href')
            if not href:
                continue
            
            # Normalize to absolute URL
            if href.startswith('//'):
                link_url = 'https:' + href
            elif href.startswith('/'):
                link_url = 'https://jobs.rwfm.tamu.edu' + href
            elif href.startswith('http'):
                link_url = href
            else:
                link_url = 'https://jobs.rwfm.tamu.edu/' + href
            
            if link_url in seen:
                continue
            seen.add(link_url)
            
            # Walk up the DOM to find title and metadata
            title = None
            location = ''
            description = ''
            parent = a
            
            for _ in range(5):
                parent = parent.parent
                if parent is None:
                    break
                heading = parent.find(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
                if heading:
                    title = heading.get_text(strip=True)
                    break
            
            if not title:
                prev_heading = a.find_previous(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
                if prev_heading:
                    title = prev_heading.get_text(strip=True)
            
            # Extract location info
            container = parent or a
            text = container.get_text(" ", strip=True)
            m = re.search(r'Location[:\s]+([^\[]+?)(?:\s{2,}|\s*\[|$)', text)
            if m:
                location = m.group(1).strip()
            
            # Extract description
            p = container.find('p')
            if p:
                description = p.get_text(strip=True)
            else:
                snippet = text.replace(title or '', '').strip()
                description = snippet[:300].strip()
            
            all_jobs.append({
                'title': title or 'No title',
                'link': link_url,
                'location': location,
                'description': description
            })
    
    return all_jobs


def save_jobs(jobs):
    """Save jobs to JSON file."""
    if not jobs:
        print("No jobs to save")
        return False
    
    try:
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(jobs, f, indent=2, ensure_ascii=False)
        print(f"✅ Successfully saved {len(jobs)} recent jobs to {OUTPUT_FILE}")
        return True
    except Exception as e:
        print(f"Error saving jobs: {e}")
        return False


if __name__ == '__main__':
    print("Scraping recent TAMU Natural Resources jobs...")
    jobs = scrape_jobs()
    if jobs:
        save_jobs(jobs)
    else:
        print("Failed to scrape jobs")
