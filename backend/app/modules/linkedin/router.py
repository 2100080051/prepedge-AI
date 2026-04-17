from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.auth.dependencies import get_current_user
from app.database.session import get_db
from app.database.models import User
from app.modules.linkedin.parser import LinkedInParser
from typing import Dict
from pydantic import BaseModel

router = APIRouter(prefix="/linkedin", tags=["LinkedIn"])


class LinkedInURLRequest(BaseModel):
    url: str


class LinkedInDataRequest(BaseModel):
    url: str
    section: str = None  # 'header', 'summary', 'experience', 'education', 'skills', 'certifications', 'projects'


@router.post("/validate-url")
async def validate_linkedin_url(
    request: LinkedInURLRequest,
    current_user: User = Depends(get_current_user)
) -> Dict:
    """
    Validate if a URL is a valid LinkedIn profile URL
    """
    is_valid = LinkedInParser.validate_linkedin_url(request.url)

    if not is_valid:
        raise HTTPException(status_code=400, detail="Invalid LinkedIn URL format")

    username = LinkedInParser.extract_linkedin_username(request.url)

    return {
        "success": True,
        "valid": True,
        "username": username,
        "url": request.url
    }


@router.post("/parse-profile")
async def parse_linkedin_profile(
    request: LinkedInURLRequest,
    current_user: User = Depends(get_current_user)
) -> Dict:
    """
    Parse LinkedIn profile and extract all data
    Returns: header, summary, experience, education, skills, certifications, projects
    """
    try:
        result = LinkedInParser.parse_profile(request.url)

        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("error", "Failed to parse profile"))

        # Validate extracted data
        validation = LinkedInParser.validate_profile_data(result["data"])

        return {
            "success": True,
            "username": result["username"],
            "data": result["data"],
            "validation": validation
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error parsing profile: {str(e)}")


@router.post("/extract-section")
async def extract_section(
    request: LinkedInDataRequest,
    current_user: User = Depends(get_current_user)
) -> Dict:
    """
    Extract a specific section from LinkedIn profile
    section: 'header', 'summary', 'experience', 'education', 'skills', 'certifications', 'projects'
    """
    valid_sections = ['header', 'summary', 'experience', 'education', 'skills', 'certifications', 'projects']

    if request.section and request.section not in valid_sections:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid section. Must be one of: {', '.join(valid_sections)}"
        )

    try:
        result = LinkedInParser.extract_and_format(request.url, request.section)

        if not result.get("success"):
            raise HTTPException(status_code=400, detail="Failed to extract data")

        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error extracting section: {str(e)}")


@router.post("/validate-completeness")
async def validate_completeness(
    request: LinkedInURLRequest,
    current_user: User = Depends(get_current_user)
) -> Dict:
    """
    Check if extracted profile data is complete enough for resume builder
    Returns: completeness_score, missing_fields, ready_for_resume
    """
    try:
        profile = LinkedInParser.parse_profile(request.url)

        if not profile.get("success"):
            raise HTTPException(status_code=400, detail=profile.get("error", "Failed to parse profile"))

        validation = LinkedInParser.validate_profile_data(profile["data"])

        return {
            "success": True,
            "username": profile["username"],
            "completeness": validation
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error validating: {str(e)}")


@router.post("/auto-fill-resume")
async def auto_fill_resume(
    request: LinkedInURLRequest,
    current_user: User = Depends(get_current_user)
) -> Dict:
    """
    Parse LinkedIn profile and return data formatted for resume builder auto-fill
    User can then review and edit before saving
    """
    try:
        profile = LinkedInParser.parse_profile(request.url)

        if not profile.get("success"):
            raise HTTPException(status_code=400, detail=profile.get("error", "Failed to parse profile"))

        data = profile["data"]
        validation = LinkedInParser.validate_profile_data(data)

        # Format for resume builder consumption
        resume_data = {
            "template": "modern",
            "header": data.get("header", {}),
            "summary": data.get("summary", ""),
            "experience": data.get("experience", []),
            "education": data.get("education", []),
            "skills": data.get("skills", []),
            "certifications": data.get("certifications", []),
            "projects": data.get("projects", [])
        }

        return {
            "success": True,
            "username": profile["username"],
            "resume_data": resume_data,
            "validation": validation,
            "import_notes": [
                "Review and edit all imported data before saving",
                "Add or remove items as needed",
                "LinkedIn profiles may not capture all details"
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error auto-filling resume: {str(e)}")


@router.get("/profile-summary/{username}")
async def get_profile_summary(
    username: str,
    current_user: User = Depends(get_current_user)
) -> Dict:
    """
    Get a quick summary of extracted LinkedIn profile
    Quick view without full profile parsing
    """
    try:
        # Reconstruct URL from username
        url = f"https://linkedin.com/in/{username}"

        profile = LinkedInParser.parse_profile(url)

        if not profile.get("success"):
            raise HTTPException(status_code=400, detail="Profile not found")

        data = profile["data"]

        return {
            "success": True,
            "username": username,
            "summary": {
                "name": data.get("header", {}).get("fullName", ""),
                "headline": data.get("header", {}).get("headline", ""),
                "location": data.get("header", {}).get("location", ""),
                "experience_count": len(data.get("experience", [])),
                "education_count": len(data.get("education", [])),
                "skills_count": len(data.get("skills", [])),
                "certifications_count": len(data.get("certifications", [])),
                "projects_count": len(data.get("projects", []))
            }
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error fetching summary: {str(e)}")
