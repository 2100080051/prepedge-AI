import re
from typing import Dict, Optional, List
from datetime import datetime
import requests
from urllib.parse import urlparse
import logging

logger = logging.getLogger(__name__)


class LinkedInParser:
    """
    LinkedIn profile parser for extracting resume data
    In production, use official LinkedIn API or web scraping library
    """

    # LinkedIn URL patterns
    LINKEDIN_URL_PATTERNS = [
        r'linkedin\.com/in/[\w-]+/?',
        r'linkedin\.com/company/[\w-]+/?',
        r'linkedin\.com/profile/view\?id=[\w]+',
    ]

    @staticmethod
    def validate_linkedin_url(url: str) -> bool:
        """Validate if URL is a valid LinkedIn profile URL"""
        try:
            parsed = urlparse(url)
            if 'linkedin.com' not in parsed.netloc:
                return False

            # Check for /in/ (personal profile) or /company/ (company page)
            if '/in/' in parsed.path or '/company/' in parsed.path:
                return True

            return False
        except Exception as e:
            logger.error(f"Error validating LinkedIn URL: {e}")
            return False

    @staticmethod
    def extract_linkedin_username(url: str) -> Optional[str]:
        """Extract username from LinkedIn URL"""
        try:
            # Clean up URL
            url = url.strip().rstrip('/')

            # Match /in/username pattern
            match = re.search(r'/in/([\w-]+)', url)
            if match:
                return match.group(1)

            # Match company pattern
            match = re.search(r'/company/([\w-]+)', url)
            if match:
                return match.group(1)

            return None
        except Exception as e:
            logger.error(f"Error extracting LinkedIn username: {e}")
            return None

    @staticmethod
    def parse_profile(url: str) -> Dict:
        """
        Parse LinkedIn profile and extract data
        Returns structured profile data for resume builder
        """
        if not LinkedInParser.validate_linkedin_url(url):
            return {"error": "Invalid LinkedIn URL"}

        username = LinkedInParser.extract_linkedin_username(url)
        if not username:
            return {"error": "Could not extract profile username"}

        # Simulate profile data extraction
        # In production, use LinkedIn API or web scraping library
        profile_data = LinkedInParser._simulate_profile_extraction(username)

        return {
            "success": True,
            "username": username,
            "data": profile_data
        }

    @staticmethod
    def _simulate_profile_extraction(username: str) -> Dict:
        """
        Simulate LinkedIn profile extraction
        In production, implement real web scraping or API calls
        """
        return {
            "header": {
                "fullName": f"{username.replace('-', ' ').title()}",
                "headline": "Software Engineer | Full Stack Developer",
                "location": "San Francisco, CA",
                "email": f"{username}@example.com",
                "phone": "+1 (555) 000-0000",
                "website": f"https://{username}.com",
                "linkedin": f"https://linkedin.com/in/{username}",
                "profileImage": f"https://media.licdn.com/dms/image/{username}"
            },
            "summary": """Experienced full-stack software engineer with 5+ years of experience building scalable web applications. 
Proficient in React, Node.js, Python, and cloud technologies. Passionate about solving complex problems and mentoring junior developers.""",
            "experience": [
                {
                    "company": "Tech Company A",
                    "role": "Senior Software Engineer",
                    "startDate": "2022-01",
                    "endDate": "2024-12",
                    "currentlyWorking": False,
                    "description": "Led development of microservices architecture. Mentored 3 junior engineers. Improved system performance by 40%."
                },
                {
                    "company": "Tech Company B",
                    "role": "Software Engineer",
                    "startDate": "2020-06",
                    "endDate": "2021-12",
                    "currentlyWorking": False,
                    "description": "Built React components and REST APIs. Collaborated with product and design teams. Achieved 95% code coverage."
                },
                {
                    "company": "Startup C",
                    "role": "Full Stack Developer",
                    "startDate": "2018-03",
                    "endDate": "2020-05",
                    "currentlyWorking": False,
                    "description": "Early employee at Series A startup. Built MVP in 3 months. Grew platform to 10k+ users."
                }
            ],
            "education": [
                {
                    "school": "University of Technology",
                    "degree": "Bachelor of Science",
                    "field": "Computer Science",
                    "graduationDate": "2018-05",
                    "gpa": "3.8"
                },
                {
                    "school": "Coursera",
                    "degree": "Professional Certificate",
                    "field": "Machine Learning",
                    "graduationDate": "2021-06",
                    "gpa": None
                }
            ],
            "skills": [
                "JavaScript",
                "React",
                "Node.js",
                "Python",
                "TypeScript",
                "AWS",
                "Docker",
                "PostgreSQL",
                "MongoDB",
                "GraphQL",
                "REST APIs",
                "Git",
                "Agile",
                "Team Leadership",
                "Technical Writing"
            ],
            "certifications": [
                {
                    "name": "AWS Certified Solutions Architect",
                    "issuer": "Amazon Web Services",
                    "date": "2023-06"
                },
                {
                    "name": "Kubernetes Application Developer",
                    "issuer": "Linux Foundation",
                    "date": "2022-09"
                }
            ],
            "projects": [
                {
                    "name": "E-Commerce Platform",
                    "description": "Built full-stack e-commerce platform with microservices. Handled 10k+ concurrent users.",
                    "technologies": ["React", "Node.js", "PostgreSQL", "AWS", "Docker"],
                    "link": "https://example-ecom.com"
                },
                {
                    "name": "Data Analytics Dashboard",
                    "description": "Real-time analytics dashboard for business metrics visualization. Processed 100M+ events/day.",
                    "technologies": ["React", "Python", "Kafka", "Elasticsearch", "Grafana"],
                    "link": "https://example-analytics.com"
                }
            ]
        }

    @staticmethod
    def extract_and_format(url: str, target_section: str = None) -> Dict:
        """
        Parse LinkedIn profile and format for resume builder
        target_section: 'header', 'summary', 'experience', 'education', 'skills', 'certifications', 'projects', or None for all
        """
        profile = LinkedInParser.parse_profile(url)

        if not profile.get("success"):
            return profile

        data = profile["data"]

        if target_section and target_section in data:
            return {
                "success": True,
                "section": target_section,
                "data": data[target_section]
            }

        return {
            "success": True,
            "all_sections": data
        }

    @staticmethod
    def validate_profile_data(data: Dict) -> Dict:
        """
        Validate extracted profile data for completeness
        Returns completeness score and missing fields
        """
        completeness = 0
        total_fields = 0
        missing_fields = []

        sections = {
            "header": ["fullName", "headline", "location"],
            "summary": [True],  # Just check if summary exists
            "experience": [True],  # Just check if has at least 1
            "education": [True],  # Just check if has at least 1
            "skills": [True]  # Just check if has skills
        }

        total_fields = 5  # 5 major sections

        # Check header
        header = data.get("header", {})
        if header.get("fullName") and header.get("headline") and header.get("location"):
            completeness += 1
        else:
            missing_fields.append("header (missing fullName, headline, or location)")

        # Check summary
        if data.get("summary"):
            completeness += 1
        else:
            missing_fields.append("summary")

        # Check experience
        if data.get("experience") and len(data["experience"]) > 0:
            completeness += 1
        else:
            missing_fields.append("experience")

        # Check education
        if data.get("education") and len(data["education"]) > 0:
            completeness += 1
        else:
            missing_fields.append("education")

        # Check skills
        if data.get("skills") and len(data["skills"]) > 0:
            completeness += 1
        else:
            missing_fields.append("skills")

        completeness_score = (completeness / total_fields) * 100

        return {
            "completeness_score": round(completeness_score, 1),
            "missing_fields": missing_fields,
            "ready_for_resume": completeness_score >= 80,
            "sections_filled": completeness,
            "total_sections": total_fields
        }
