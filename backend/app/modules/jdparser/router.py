from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from app.auth.dependencies import get_current_user
from app.database.session import get_db
from app.database.models import User
from app.modules.jdparser.service import JobDescriptionParser
from typing import Dict
from pydantic import BaseModel

router = APIRouter(prefix="/jdparser", tags=["Job Description Parser"])


class JobDescriptionRequest(BaseModel):
    job_description: str
    company: str = None
    job_title: str = None


class ComparisonRequest(BaseModel):
    job_description: str
    resume_data: Dict  # {skills, experience, education, ...}


@router.post("/parse")
async def parse_job_description(
    request: JobDescriptionRequest,
    current_user: User = Depends(get_current_user)
) -> Dict:
    """
    Parse job description and extract requirements
    Returns: title, requirements, skills, qualifications, responsibilities, etc.
    """
    if not request.job_description or len(request.job_description) < 50:
        raise HTTPException(
            status_code=400,
            detail="Job description must be at least 50 characters"
        )

    try:
        result = JobDescriptionParser.parse_job_description(request.job_description)

        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("error"))

        return {
            "success": True,
            "company": request.company,
            "job_title": request.job_title,
            "data": result["job_data"]
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error parsing job description: {str(e)}")


@router.post("/upload")
async def upload_job_description(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
) -> Dict:
    """
    Upload job description file (PDF, TXT, DOC)
    Returns parsed job data
    """
    try:
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file provided")

        # Read file content (simplified - in production, handle multiple formats)
        content = await file.read()
        text = content.decode('utf-8')

        result = JobDescriptionParser.parse_job_description(text)

        if not result.get("success"):
            raise HTTPException(status_code=400, detail="Failed to parse file")

        return {
            "success": True,
            "filename": file.filename,
            "data": result["job_data"]
        }
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="File must be text-based (TXT, PDF text)")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error uploading file: {str(e)}")


@router.post("/compare")
async def compare_with_resume(
    request: ComparisonRequest,
    current_user: User = Depends(get_current_user)
) -> Dict:
    """
    Compare job description with user's resume
    Returns: match score, missing skills, recommendations
    """
    try:
        # Parse job description
        jd_result = JobDescriptionParser.parse_job_description(request.job_description)

        if not jd_result.get("success"):
            raise HTTPException(status_code=400, detail="Failed to parse job description")

        jd_data = jd_result["job_data"]

        # Compare with resume
        comparison = JobDescriptionParser.compare_with_resume(jd_data, request.resume_data)

        return {
            "success": True,
            "job_requirements": {
                "title": jd_data.get("title"),
                "experience_level": jd_data.get("experience_level"),
                "required_skills": jd_data.get("required_skills"),
                "nice_to_have": jd_data.get("nice_to_have_skills")
            },
            "match_analysis": comparison
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error comparing: {str(e)}")


@router.post("/extract-skills")
async def extract_skills(
    request: JobDescriptionRequest,
    current_user: User = Depends(get_current_user)
) -> Dict:
    """
    Extract only skills from job description (fast operation)
    """
    try:
        required = JobDescriptionParser._extract_required_skills(request.job_description)
        nice = JobDescriptionParser._extract_nice_to_have_skills(request.job_description)

        return {
            "success": True,
            "required_skills": required,
            "nice_to_have_skills": nice,
            "categorized": JobDescriptionParser._categorize_skills(required + nice)
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error extracting skills: {str(e)}")


@router.post("/get-recommendations")
async def get_recommendations(
    request: ComparisonRequest,
    current_user: User = Depends(get_current_user)
) -> Dict:
    """
    Get personalized recommendations for resume improvement based on job description
    """
    try:
        jd_result = JobDescriptionParser.parse_job_description(request.job_description)

        if not jd_result.get("success"):
            raise HTTPException(status_code=400, detail="Failed to parse job description")

        jd_data = jd_result["job_data"]
        comparison = JobDescriptionParser.compare_with_resume(jd_data, request.resume_data)

        return {
            "success": True,
            "match_score": comparison["overall_match_score"],
            "recommendations": comparison["recommendations"],
            "action_items": [
                {
                    "priority": "high",
                    "action": f"Add {', '.join(list(comparison['missing_required_skills'])[:3])} to your skills",
                    "impact": "Critical for this role"
                },
                {
                    "priority": "medium",
                    "action": "Customize resume summary with job keywords",
                    "impact": "Improves ATS matching"
                },
                {
                    "priority": "low",
                    "action": f"Add projects using {comparison['missing_nice_skills'][0] if comparison['missing_nice_skills'] else 'recommended'} technologies",
                    "impact": "Nice to have"
                }
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error generating recommendations: {str(e)}")


@router.post("/analyze-fit")
async def analyze_fit(
    request: ComparisonRequest,
    current_user: User = Depends(get_current_user)
) -> Dict:
    """
    Comprehensive job fit analysis
    Returns suitability score, gaps, strengths, recommendations
    """
    try:
        jd_result = JobDescriptionParser.parse_job_description(request.job_description)

        if not jd_result.get("success"):
            raise HTTPException(status_code=400, detail="Failed to parse job description")

        jd_data = jd_result["job_data"]
        comparison = JobDescriptionParser.compare_with_resume(jd_data, request.resume_data)

        score = comparison["overall_match_score"]

        # Determine fit level
        if score >= 85:
            fit_level = "Excellent Fit 🚀"
            fit_description = "You're well-qualified for this role. Apply immediately!"
        elif score >= 70:
            fit_level = "Good Fit ✅"
            fit_description = "You meet most requirements. Focus on the gaps before applying."
        elif score >= 50:
            fit_level = "Moderate Fit ⚠️"
            fit_description = "You have potential but significant skill gaps exist."
        else:
            fit_level = "Poor Fit ❌"
            fit_description = "This role may not be suitable yet. Consider learning the required skills first."

        return {
            "success": True,
            "fit_analysis": {
                "overall_score": score,
                "fit_level": fit_level,
                "description": fit_description,
                "matched_skills": {
                    "required": comparison["matched_required_skills"],
                    "nice_to_have": comparison["matched_nice_skills"]
                },
                "gaps": {
                    "critical": comparison["missing_required_skills"],
                    "optional": comparison["missing_nice_skills"]
                }
            },
            "action_plan": comparison["recommendations"],
            "next_steps": [
                "1. Review all recommendations above",
                f"2. Priority: Learn {list(comparison['missing_required_skills'])[0] if comparison['missing_required_skills'] else 'recommended skills'}",
                "3. Update resume with new skills and keywords",
                "4. Build a project using required technologies",
                "5. Reupload resume and compare again"
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error analyzing fit: {str(e)}")
