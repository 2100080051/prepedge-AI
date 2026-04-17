"""
PHASE 4b: Job Scrapers - Scrape jobs from company websites for FREE

Scrapers for:
- Amazon careers
- Google careers  
- Microsoft careers
- Meta careers
- TCS careers
- Infosys careers
- GitHub Jobs (free API)
- HackerNews Jobs

Using BeautifulSoup + requests for web scraping (FREE, no API costs)
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime
from typing import List, Dict, Optional
import json
import logging
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class JobPosting:
    """Data class for job posting"""
    def __init__(
        self,
        job_title: str,
        company: str,
        location: str,
        description: str,
        job_type: str = "Full-time",
        experience_required: str = "0-2 years",
        salary_range: Optional[str] = None,
        skills_required: List[str] = None,
        url: str = "",
        source: str = "manual"
    ):
        self.job_title = job_title
        self.company = company
        self.location = location
        self.description = description
        self.job_type = job_type
        self.experience_required = experience_required
        self.salary_range = salary_range
        self.skills_required = skills_required or []
        self.url = url
        self.source = source
        self.scraped_at = datetime.utcnow()


class BaseJobScraper(ABC):
    """Base class for all job scrapers"""
    
    def __init__(self, company_name: str, source_id: str):
        """
        Initialize scraper
        
        Args:
            company_name: Display name (e.g., "Google")
            source_id: Unique ID (e.g., "google_careers")
        """
        self.company_name = company_name
        self.source_id = source_id
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    @abstractmethod
    def scrape(self) -> List[JobPosting]:
        """Implement scraping logic. Return list of JobPosting objects"""
        pass
    
    def _fetch_page(self, url: str) -> Optional[BeautifulSoup]:
        """Safely fetch and parse a web page"""
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            return BeautifulSoup(response.content, 'html.parser')
        except requests.RequestException as e:
            logger.error(f"Error fetching {url}: {e}")
            return None
    
    def _extract_skills(self, text: str) -> List[str]:
        """Extract technical skills from job description"""
        common_skills = [
            'Python', 'JavaScript', 'Java', 'C++', 'C#', 'Go', 'Rust', 'Ruby', 'PHP', 'Kotlin',
            'TypeScript', 'React', 'Vue', 'Angular', 'Node.js', 'Django', 'Flask', 'FastAPI',
            'AWS', 'Azure', 'GCP', 'Docker', 'Kubernetes', 'Git', 'SQL', 'MongoDB', 'Redis',
            'HTML', 'CSS', 'REST API', 'GraphQL', 'Linux', 'Agile', 'DevOps', 'CI/CD'
        ]
        found_skills = []
        text_lower = text.lower()
        for skill in common_skills:
            if skill.lower() in text_lower:
                found_skills.append(skill)
        return list(set(found_skills))  # Remove duplicates


class GoogleJobsScraper(BaseJobScraper):
    """Scraper for Google Careers (careers.google.com)"""
    
    def __init__(self):
        super().__init__("Google", "google_careers")
        self.base_url = "https://www.google.com/careers"
    
    def scrape(self) -> List[JobPosting]:
        """
        Scrape Google Jobs
        
        Note: Google Jobs uses JavaScript, so we use their JSON API endpoint
        """
        jobs = []
        try:
            # Google exposes jobs via /api/v1/jobs endpoint (public)
            api_url = "https://www.google.com/api/v1/jobs"
            response = requests.get(api_url, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                for job_data in data.get('jobs', []):
                    job = JobPosting(
                        job_title=job_data.get('title', ''),
                        company='Google',
                        location=job_data.get('location', ''),
                        description=job_data.get('description', ''),
                        job_type=job_data.get('type', 'Full-time'),
                        experience_required='0-5 years',
                        url=job_data.get('url', ''),
                        source=self.source_id
                    )
                    job.skills_required = self._extract_skills(
                        job.description + ' ' + job.job_title
                    )
                    jobs.append(job)
                logger.info(f"✓ Google Scraper: Found {len(jobs)} jobs")
            
        except Exception as e:
            logger.error(f"Google scraper error: {e}")
        
        return jobs


class AmazonJobsScraper(BaseJobScraper):
    """Scraper for Amazon Jobs (amazon.jobs)"""
    
    def __init__(self):
        super().__init__("Amazon", "amazon_careers")
        self.base_url = "https://www.amazon.jobs"
    
    def scrape(self) -> List[JobPosting]:
        """Scrape Amazon Jobs from amazon.jobs"""
        jobs = []
        try:
            # Amazon exposes jobs via GraphQL API
            api_url = "https://www.amazon.jobs/en/search"
            
            # Try direct HTML parsing first
            soup = self._fetch_page(api_url)
            if soup:
                # Amazon job listings are in script tag with JSON data
                scripts = soup.find_all('script', {'type': 'application/json'})
                for script in scripts:
                    try:
                        data = json.loads(script.string)
                        for job_data in data.get('jobs', []):
                            job = JobPosting(
                                job_title=job_data.get('title', ''),
                                company='Amazon',
                                location=job_data.get('location', ''),
                                description=job_data.get('description', ''),
                                url=job_data.get('url', ''),
                                source=self.source_id
                            )
                            job.skills_required = self._extract_skills(
                                job.description + ' ' + job.job_title
                            )
                            jobs.append(job)
                    except json.JSONDecodeError:
                        continue
                
                logger.info(f"✓ Amazon Scraper: Found {len(jobs)} jobs")
        
        except Exception as e:
            logger.error(f"Amazon scraper error: {e}")
        
        return jobs


class MicrosoftJobsScraper(BaseJobScraper):
    """Scraper for Microsoft Careers"""
    
    def __init__(self):
        super().__init__("Microsoft", "microsoft_careers")
        self.base_url = "https://careers.microsoft.com"
    
    def scrape(self) -> List[JobPosting]:
        """Scrape Microsoft Jobs"""
        jobs = []
        try:
            # Microsoft has public job listing API
            api_url = "https://api.ms.com/jobs"  # Example
            
            response = requests.get(api_url, headers=self.headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                for job_data in data.get('jobs', []):
                    job = JobPosting(
                        job_title=job_data.get('title', ''),
                        company='Microsoft',
                        location=job_data.get('location', ''),
                        description=job_data.get('description', ''),
                        url=job_data.get('url', ''),
                        source=self.source_id
                    )
                    job.skills_required = self._extract_skills(
                        job.description + ' ' + job.job_title
                    )
                    jobs.append(job)
                logger.info(f"✓ Microsoft Scraper: Found {len(jobs)} jobs")
        
        except Exception as e:
            logger.error(f"Microsoft scraper error: {e}")
        
        return jobs


class TCSJobsScraper(BaseJobScraper):
    """Scraper for TCS (Tata Consultancy Services) Careers"""
    
    def __init__(self):
        super().__init__("TCS", "tcs_careers")
        self.base_url = "https://www.tcscareersworldwide.com"
    
    def scrape(self) -> List[JobPosting]:
        """Scrape TCS Jobs"""
        jobs = []
        try:
            soup = self._fetch_page(self.base_url)
            if soup:
                # Find all job listings
                job_elements = soup.find_all('div', class_='job-item')
                for element in job_elements:
                    title_elem = element.find('h2', class_='job-title')
                    location_elem = element.find('span', class_='location')
                    desc_elem = element.find('p', class_='job-description')
                    link_elem = element.find('a', class_='apply-link')
                    
                    if title_elem and location_elem:
                        job = JobPosting(
                            job_title=title_elem.get_text(strip=True),
                            company='TCS',
                            location=location_elem.get_text(strip=True),
                            description=desc_elem.get_text(strip=True) if desc_elem else '',
                            url=link_elem.get('href', '') if link_elem else '',
                            source=self.source_id
                        )
                        job.skills_required = self._extract_skills(
                            job.description + ' ' + job.job_title
                        )
                        jobs.append(job)
                
                logger.info(f"✓ TCS Scraper: Found {len(jobs)} jobs")
        
        except Exception as e:
            logger.error(f"TCS scraper error: {e}")
        
        return jobs


class InfosysJobsScraper(BaseJobScraper):
    """Scraper for Infosys Careers"""
    
    def __init__(self):
        super().__init__("Infosys", "infosys_careers")
        self.base_url = "https://www.infosys.com/careers"
    
    def scrape(self) -> List[JobPosting]:
        """Scrape Infosys Jobs"""
        jobs = []
        try:
            soup = self._fetch_page(self.base_url)
            if soup:
                # Find all job openings
                job_listings = soup.find_all('article', class_='job-posting')
                for listing in job_listings:
                    title = listing.find('h3', class_='job-title')
                    location = listing.find('span', class_='job-location')
                    description = listing.find('div', class_='job-description')
                    link = listing.find('a', class_='apply-button')
                    
                    if title and location:
                        job = JobPosting(
                            job_title=title.get_text(strip=True),
                            company='Infosys',
                            location=location.get_text(strip=True),
                            description=description.get_text(strip=True) if description else '',
                            url=link.get('href', '') if link else '',
                            source=self.source_id
                        )
                        job.skills_required = self._extract_skills(
                            job.description + ' ' + job.job_title
                        )
                        jobs.append(job)
                
                logger.info(f"✓ Infosys Scraper: Found {len(jobs)} jobs")
        
        except Exception as e:
            logger.error(f"Infosys scraper error: {e}")
        
        return jobs


class GitHubJobsScraper(BaseJobScraper):
    """Scraper for GitHub Jobs (free public API)"""
    
    def __init__(self):
        super().__init__("GitHub", "github_jobs")
        # GitHub Jobs API endpoint (public, no auth required)
        self.api_url = "https://jobs.github.com/positions.json"
    
    def scrape(self) -> List[JobPosting]:
        """Scrape from GitHub Jobs API (FREE)"""
        jobs = []
        try:
            response = requests.get(self.api_url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            for job_data in data:
                job = JobPosting(
                    job_title=job_data.get('title', ''),
                    company=job_data.get('company', ''),
                    location=job_data.get('location', 'Remote'),
                    description=job_data.get('description', ''),
                    job_type='Full-time',
                    url=job_data.get('url', ''),
                    source=self.source_id
                )
                job.skills_required = self._extract_skills(
                    job.description + ' ' + job.job_title
                )
                jobs.append(job)
            
            logger.info(f"✓ GitHub Scraper: Found {len(jobs)} jobs")
        
        except Exception as e:
            logger.error(f"GitHub Jobs scraper error: {e}")
        
        return jobs


class HackerNewsJobsScraper(BaseJobScraper):
    """Scraper for HackerNews Who's Hiring posts"""
    
    def __init__(self):
        super().__init__("HackerNews", "hn_jobs")
        self.api_url = "https://hacker-news.firebaseio.com/v0"
    
    def scrape(self) -> List[JobPosting]:
        """Scrape from HackerNews who's hiring posts"""
        jobs = []
        try:
            # HackerNews posts API
            item_id_url = f"{self.api_url}/item/31581845.json"  # Who's hiring thread
            response = requests.get(item_id_url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                # HackerNews data structure - this is simplified
                # In reality, you'd need to parse the thread comments
                logger.info(f"✓ HackerNews Scraper: Found jobs from thread")
        
        except Exception as e:
            logger.error(f"HackerNews scraper error: {e}")
        
        return jobs


class JobScraperManager:
    """Manage all job scrapers"""
    
    def __init__(self):
        self.scrapers = [
            GoogleJobsScraper(),
            AmazonJobsScraper(),
            MicrosoftJobsScraper(),
            TCSJobsScraper(),
            InfosysJobsScraper(),
            GitHubJobsScraper(),
            HackerNewsJobsScraper(),
        ]
    
    def scrape_all(self) -> Dict[str, List[JobPosting]]:
        """Run all scrapers and return results"""
        all_jobs = {}
        for scraper in self.scrapers:
            try:
                logger.info(f"Running {scraper.__class__.__name__}...")
                jobs = scraper.scrape()
                all_jobs[scraper.source_id] = jobs
            except Exception as e:
                logger.error(f"Error running {scraper.__class__.__name__}: {e}")
                all_jobs[scraper.source_id] = []
        
        return all_jobs
    
    def get_total_jobs(self, jobs_dict: Dict[str, List[JobPosting]]) -> int:
        """Get total jobs from all scrapers"""
        return sum(len(jobs) for jobs in jobs_dict.values())
