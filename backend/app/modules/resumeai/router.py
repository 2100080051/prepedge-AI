from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.auth.dependencies import get_current_user
from app.database.models import User
from app.modules.resumeai.service import ResumeAIService
import json

router = APIRouter(prefix="/resumeai", tags=["resumeai"])

@router.post("/upload")
async def upload_resume(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload and analyze a resume using the Nvidia Llama AI model.
    Returns a comprehensive report with score, strengths, gaps, role recommendations, and learning path."""
    allowed = ('.txt', '.pdf', '.doc', '.docx')
    if not file.filename.lower().endswith(allowed):
        raise HTTPException(status_code=400, detail=f"File type not supported. Use: {', '.join(allowed)}")

    content = await file.read()
    
    # Extract text from file using service method
    try:
        text_content = ResumeAIService.extract_resume_text(content, file.filename)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Could not extract text from file: {str(e)}")

    if len(text_content.strip()) < 50:
        raise HTTPException(status_code=400, detail="Resume content too short to analyze")

    # Run AI analysis
    analysis = ResumeAIService.analyze_resume(text_content)

    # Save to DB
    ResumeAIService.save_resume(
        db=db,
        user_id=current_user.id,
        filename=file.filename,
        content=text_content,
        analysis=analysis
    )

    # Return full rich analysis
    return {
        "filename": file.filename,
        "detected_domain": analysis.get("detected_domain", "Unknown"),
        "candidate_name": analysis.get("candidate_name", ""),
        "score": analysis.get("score", 0),
        "ats_score": analysis.get("ats_score", 0),
        "strengths": analysis.get("strengths", []),
        "gaps": analysis.get("gaps", []),
        "improvements": analysis.get("improvements", []),
        "keywords_missing": analysis.get("keywords_missing", []),
        "suggested_summary": analysis.get("suggested_summary", ""),
        "best_fit_roles": analysis.get("best_fit_roles", []),
        "top_companies_to_target": analysis.get("top_companies_to_target", []),
        "what_to_learn_next": analysis.get("what_to_learn_next", []),
        "encouragement": analysis.get("encouragement", ""),
        "summary": analysis.get("summary", ""),
    }

@router.get("/feedback")
def get_resume_feedback(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get resume analysis history for the current user"""
    resumes = ResumeAIService.get_user_resumes(db, current_user.id)
    result = []
    for r in resumes:
        fb = r.feedback[0] if r.feedback else None
        result.append({
            "id": r.id,
            "filename": r.file_path,
            "score": r.score,
            "created_at": str(r.created_at),
            "ats_score": fb.ats_score if fb else 0,
            "strengths": json.loads(fb.strengths) if fb and fb.strengths else [],
            "improvements": json.loads(fb.improvements) if fb and fb.improvements else [],
            "keywords_missing": json.loads(fb.keywords_missing) if fb and fb.keywords_missing else [],
            "summary": fb.summary if fb else ""
        })
    return result
