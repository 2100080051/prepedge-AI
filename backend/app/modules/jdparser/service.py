import re
from typing import Dict, List, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class JobDescriptionParser:
    """
    Parse job descriptions and extract requirements
    Extracts skills, experience level, qualifications, responsibilities
    """

    # Common skill keywords by category
    SKILL_KEYWORDS = {
        "frontend": [
            "react", "vue", "angular", "html", "css", "javascript", "typescript",
            "next.js", "webpack", "babel", "responsive design", "ui/ux"
        ],
        "backend": [
            "node.js", "python", "java", "go", "rust", "c#", "ruby", "php",
            "django", "flask", "spring", "express", "fastapi"
        ],
        "databases": [
            "sql", "postgresql", "mysql", "mongodb", "cassandra", "redis",
            "elasticsearch", "dynamodb", "firestore", "caching"
        ],
        "cloud": [
            "aws", "azure", "gcp", "kubernetes", "docker", "terraform",
            "cloudformation", "lambda", "ec2", "s3", "heroku"
        ],
        "devops": [
            "ci/cd", "jenkins", "github actions", "gitlab ci", "docker",
            "kubernetes", "terraform", "ansible", "monitoring", "logging"
        ],
        "data": [
            "sql", "python", "r", "spark", "hadoop", "kafka", "tableau",
            "power bi", "machine learning", "statistics", "etl"
        ],
        "mobile": [
            "ios", "android", "swift", "kotlin", "react native", "flutter",
            "objective-c", "xamarin"
        ]
    }

    # Experience level patterns
    EXPERIENCE_PATTERNS = {
        "entry": r"(\d{0,1}\s*years?|entry\s*level|fresh|graduate|0\d\s*years?)",
        "junior": r"(\d\s*years?|junior|1\-3)",
        "mid": r"(3\-5|mid\s*level|senior|4\-6\s*years?)",
        "senior": r"(5\+|7\+|senior|lead|10\s*years?|expert)",
        "lead": r"(lead|principal|architect|director|staff)"
    }

    @staticmethod
    def parse_job_description(text: str) -> Dict:
        """
        Parse full job description and extract all relevant data
        """
        if not text or len(text) < 50:
            return {"error": "Job description too short"}

        # Extract different sections
        job_data = {
            "title": JobDescriptionParser._extract_job_title(text),
            "company": JobDescriptionParser._extract_company(text),
            "experience_level": JobDescriptionParser._extract_experience_level(text),
            "required_skills": JobDescriptionParser._extract_required_skills(text),
            "nice_to_have_skills": JobDescriptionParser._extract_nice_to_have_skills(text),
            "qualifications": JobDescriptionParser._extract_qualifications(text),
            "responsibilities": JobDescriptionParser._extract_responsibilities(text),
            "salary_range": JobDescriptionParser._extract_salary(text),
            "location": JobDescriptionParser._extract_location(text),
            "job_type": JobDescriptionParser._extract_job_type(text),
            "keywords": JobDescriptionParser._extract_keywords(text),
            "skill_categories": JobDescriptionParser._categorize_skills(
                JobDescriptionParser._extract_required_skills(text)
            )
        }

        return {
            "success": True,
            "job_data": job_data,
            "parsed_at": datetime.utcnow().isoformat()
        }

    @staticmethod
    def _extract_job_title(text: str) -> Optional[str]:
        """Extract job title from text"""
        # Look for common job title patterns
        title_pattern = r"(?:job title|position|role):\s*([A-Za-z\s]+(?:Engineer|Developer|Manager|Lead|Analyst|Architect))"
        match = re.search(title_pattern, text, re.IGNORECASE)
        if match:
            return match.group(1).strip()

        # Try to find title in first line
        lines = text.split('\n')
        for line in lines[:3]:
            if any(keyword in line.lower() for keyword in ['engineer', 'developer', 'manager', 'lead', 'analyst', 'architect']):
                return line.strip()

        return "Software Engineer"  # Default

    @staticmethod
    def _extract_company(text: str) -> Optional[str]:
        """Extract company name from text"""
        company_pattern = r"(?:company|hiring|at):\s*([A-Za-z\s&.,]+?)(?:\n|$)"
        match = re.search(company_pattern, text, re.IGNORECASE)
        if match:
            return match.group(1).strip()

        return None

    @staticmethod
    def _extract_experience_level(text: str) -> str:
        """Determine experience level required"""
        text_lower = text.lower()

        for level, pattern in JobDescriptionParser.EXPERIENCE_PATTERNS.items():
            if re.search(pattern, text_lower):
                if level == "lead":
                    return "Lead/Principal"
                elif level == "senior":
                    return "Senior (5+ years)"
                elif level == "mid":
                    return "Mid-level (3-5 years)"
                elif level == "junior":
                    return "Junior (1-3 years)"
                elif level == "entry":
                    return "Entry-level (0-1 years)"

        return "Mid-level (3-5 years)"  # Default

    @staticmethod
    def _extract_required_skills(text: str) -> List[str]:
        """Extract required skills from text"""
        text_lower = text.lower()
        found_skills = set()

        # Look for skills in "Required Skills" section
        required_section = re.search(
            r"(?:required\s+skills?|must\s+have|essential|core\s+skills?):(.*?)(?:nice|preferred|optional|responsibilities|qualifications|$)",
            text,
            re.IGNORECASE | re.DOTALL
        )

        if required_section:
            section_text = required_section.group(1).lower()
        else:
            section_text = text_lower

        # Check against all skill keywords
        for category, skills in JobDescriptionParser.SKILL_KEYWORDS.items():
            for skill in skills:
                if skill in section_text:
                    found_skills.add(skill.title())

        return sorted(list(found_skills))

    @staticmethod
    def _extract_nice_to_have_skills(text: str) -> List[str]:
        """Extract nice-to-have/preferred skills"""
        text_lower = text.lower()
        found_skills = set()

        # Look for nice-to-have section
        nice_section = re.search(
            r"(?:nice\s+to\s+have|preferred|optional|bonus):(.*?)(?:responsibilities|qualifications|$)",
            text,
            re.IGNORECASE | re.DOTALL
        )

        if nice_section:
            section_text = nice_section.group(1).lower()

            # Check against all skill keywords
            for category, skills in JobDescriptionParser.SKILL_KEYWORDS.items():
                for skill in skills:
                    if skill in section_text:
                        found_skills.add(skill.title())

        return sorted(list(found_skills))

    @staticmethod
    def _extract_qualifications(text: str) -> List[str]:
        """Extract qualifications/requirements"""
        qualifications = []

        qual_pattern = r"(?:qualifications|requirements):(.*?)(?:responsibilities|skills|$)"
        match = re.search(qual_pattern, text, re.IGNORECASE | re.DOTALL)

        if match:
            qual_text = match.group(1)
            # Split by bullet points or newlines
            items = re.split(r"[-•*]\s+|\n", qual_text)
            qualifications = [item.strip() for item in items if item.strip() and len(item.strip()) > 10]

        # If no qualifications found, extract common patterns
        if not qualifications:
            degree_pattern = r"(?:bachelor|master|phd|degree).*?(?:in|from).*?[A-Za-z\s]+"
            qualifications = re.findall(degree_pattern, text, re.IGNORECASE)

        return qualifications[:10]  # Top 10 qualifications

    @staticmethod
    def _extract_responsibilities(text: str) -> List[str]:
        """Extract job responsibilities"""
        responsibilities = []

        resp_pattern = r"(?:responsibilities|duties|about\s+the\s+role|you\s+will):(.*?)(?:qualifications|requirements|skills|$)"
        match = re.search(resp_pattern, text, re.IGNORECASE | re.DOTALL)

        if match:
            resp_text = match.group(1)
            # Split by bullet points or newlines
            items = re.split(r"[-•*]\s+|\n", resp_text)
            responsibilities = [item.strip() for item in items if item.strip() and len(item.strip()) > 10]

        return responsibilities[:8]  # Top 8 responsibilities

    @staticmethod
    def _extract_salary(text: str) -> Optional[str]:
        """Extract salary range if mentioned"""
        salary_pattern = r"\$[\d,]+(?:\s*[-–]\s*\$[\d,]+)?|\d+[kK]\s*[-–]\s*\d+[kK]"
        match = re.search(salary_pattern, text)
        if match:
            return match.group(0)
        return None

    @staticmethod
    def _extract_location(text: str) -> Optional[str]:
        """Extract job location"""
        location_pattern = r"(?:location|based|in):\s*([^,\n]+(?:,\s*[A-Z]{2})?)"
        match = re.search(location_pattern, text, re.IGNORECASE)
        if match:
            return match.group(1).strip()

        # Try finding US states
        states = r"(California|New York|Texas|Florida|Washington|Massachusetts)"
        match = re.search(states, text)
        if match:
            return match.group(1)

        return "Remote"

    @staticmethod
    def _extract_job_type(text: str) -> str:
        """Extract job type (Full-time, Contract, etc.)"""
        text_lower = text.lower()

        for job_type in ["full-time", "part-time", "contract", "temporary", "freelance", "permanent"]:
            if job_type in text_lower:
                return job_type.title()

        return "Full-time"  # Default

    @staticmethod
    def _extract_keywords(text: str) -> List[str]:
        """Extract important keywords from job description"""
        # Remove common words
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'is', 'are', 'was', 'be',
            'in', 'on', 'at', 'to', 'for', 'of', 'with', 'from', 'by', 'as'
        }

        words = re.findall(r'\b[A-Za-z]+\b', text)
        keywords = set()

        for word in words:
            if len(word) > 4 and word.lower() not in stop_words:
                keywords.add(word)

        # Prioritize capitalized words (potential company/product names)
        important_keywords = [w for w in keywords if w[0].isupper()]

        return important_keywords[:20]

    @staticmethod
    def _categorize_skills(skills: List[str]) -> Dict[str, List[str]]:
        """Categorize skills by type"""
        skill_mapping = JobDescriptionParser.SKILL_KEYWORDS
        categorized = {category: [] for category in skill_mapping.keys()}

        for skill in skills:
            for category, category_skills in skill_mapping.items():
                if any(cs.lower() == skill.lower() for cs in category_skills):
                    categorized[category].append(skill)
                    break

        # Remove empty categories
        return {k: v for k, v in categorized.items() if v}

    @staticmethod
    def compare_with_resume(jd_data: Dict, resume_data: Dict) -> Dict:
        """
        Compare job description requirements with user's resume
        Returns match score, missing skills, and recommendations
        """
        jd_required_skills = set(s.lower() for s in jd_data.get("required_skills", []))
        jd_nice_skills = set(s.lower() for s in jd_data.get("nice_to_have_skills", []))

        resume_skills = set(s.lower() for s in resume_data.get("skills", []))
        resume_experience = resume_data.get("experience", [])
        resume_education = resume_data.get("education", [])

        # Calculate match scores
        required_match = len(jd_required_skills & resume_skills) / len(jd_required_skills) if jd_required_skills else 0
        nice_match = len(jd_nice_skills & resume_skills) / len(jd_nice_skills) if jd_nice_skills else 0

        missing_required = jd_required_skills - resume_skills
        missing_nice = jd_nice_skills - resume_skills

        overall_score = (required_match * 0.7 + nice_match * 0.3) * 100

        return {
            "overall_match_score": round(overall_score, 1),
            "required_skills_match": round(required_match * 100, 1),
            "nice_skills_match": round(nice_match * 100, 1),
            "matched_required_skills": sorted(list(jd_required_skills & resume_skills)),
            "matched_nice_skills": sorted(list(jd_nice_skills & resume_skills)),
            "missing_required_skills": sorted(list(missing_required)),
            "missing_nice_skills": sorted(list(missing_nice)),
            "recommendations": JobDescriptionParser._generate_recommendations(
                missing_required, missing_nice, overall_score, resume_experience, jd_data
            )
        }

    @staticmethod
    def _generate_recommendations(
        missing_required: set,
        missing_nice: set,
        score: float,
        resume_experience: list,
        jd_data: dict
    ) -> List[str]:
        """Generate resume improvement recommendations"""
        recommendations = []

        if score >= 80:
            recommendations.append("✅ Strong match! You meet most of the requirements.")
        elif score >= 60:
            recommendations.append("⚠️ Good fit with some gaps. Consider addressing missing skills.")
        else:
            recommendations.append("❌ Significant skill gaps. This role may not be ideal fit yet.")

        if missing_required:
            skills_str = ", ".join(list(missing_required)[:3])
            recommendations.append(f"📚 Learn these critical skills: {skills_str}")

        if len(missing_required) > len(resume_experience):
            recommendations.append(f"💼 Add more work experience or work on projects using the required tech stack")

        if missing_nice and score < 50:
            recommendations.append(f"🎯 Taking courses in {list(missing_nice)[0]} would strengthen your application")

        if len(resume_experience) == 0:
            recommendations.append("🔨 Add projects or work experience to your resume")

        recommendations.append("✏️ Customize your resume to match this job description's keywords")
        recommendations.append("📄 Use the required skills as keywords in your resume summary")

        return recommendations[:5]
