from sqlalchemy.orm import Session
from app.database.models import ResumeUpload, ResumeFeedback
import os
import json
from io import BytesIO
from app.llm.provider import get_llm_router


class ResumeAIService:
    """Service for resume analysis and optimization"""
    
    @staticmethod
    def extract_resume_text(contents: bytes, filename: str) -> str:
        """Extract text from various resume formats"""
        try:
            # Get file extension
            file_ext = os.path.splitext(filename)[1].lower()
            
            if file_ext == '.pdf':
                return ResumeAIService._extract_from_pdf(contents)
            elif file_ext == '.docx':
                return ResumeAIService._extract_from_docx(contents)
            elif file_ext in ['.txt', '.doc']:
                return contents.decode('utf-8', errors='ignore')
            return ""
        except Exception as e:
            print(f"Text extraction error: {e}")
            return ""
    
    @staticmethod
    def _extract_from_pdf(contents: bytes) -> str:
        """Extract text from PDF with multiple fallback strategies"""
        text = ""
        
        # Strategy 1: PyPDF2
        try:
            import PyPDF2
            pdf_reader = PyPDF2.PdfReader(BytesIO(contents))
            for page in pdf_reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        except Exception as e:
            print(f"PyPDF2 extraction error: {e}")
        
        # Strategy 2: pdfplumber (fallback if PyPDF2 got little/no text)
        if len(text.strip()) < 50:
            try:
                import pdfplumber
                with pdfplumber.open(BytesIO(contents)) as pdf:
                    plumber_text = ""
                    for page in pdf.pages:
                        page_text = page.extract_text()
                        if page_text:
                            plumber_text += page_text + "\n"
                    if len(plumber_text.strip()) > len(text.strip()):
                        text = plumber_text
            except ImportError:
                print("pdfplumber not installed, skipping fallback extraction")
            except Exception as e:
                print(f"pdfplumber extraction error: {e}")
        
        # Strategy 3: Raw bytes decode as last resort
        if len(text.strip()) < 50:
            try:
                raw = contents.decode('utf-8', errors='ignore')
                # Extract readable text chunks
                import re
                chunks = re.findall(r'[\w\s.,;:!?@#$%&*()\-\/]+', raw)
                raw_text = ' '.join(c.strip() for c in chunks if len(c.strip()) > 3)
                if len(raw_text) > len(text.strip()):
                    text = raw_text
            except Exception as e:
                print(f"Raw decode extraction error: {e}")
        
        return text
    
    @staticmethod
    def _extract_from_docx(contents: bytes) -> str:
        """Extract text from DOCX"""
        text = ""
        try:
            import docx
            doc = docx.Document(BytesIO(contents))
            for para in doc.paragraphs:
                text += para.text + "\n"
        except Exception as e:
            print(f"DOCX extraction error: {e}")
        return text
    
    @staticmethod
    def save_resume(db: Session, user_id: int, filename: str, content: str, analysis: dict = None, target_company: str = None, target_role: str = None, job_description: str = None):
        """Save resume to database with role/company context"""
        resume = ResumeUpload(
            user_id=user_id,
            file_path=filename,
            content=content[:10000],
            score=analysis.get("overall_score", 7.0) if analysis else 7.0,
            target_company=target_company,
            target_role=target_role,
            job_description=job_description[:2000] if job_description else None
        )
        db.add(resume)
        db.commit()
        db.refresh(resume)
        
        # Save feedback if analysis is provided
        if analysis:
            feedback = ResumeFeedback(
                resume_id=resume.id,
                overall_score=analysis.get("overall_score", 7.0),
                ats_score=analysis.get("ats_score", 0),
                strengths=json.dumps(analysis.get("strengths", [])),
                improvements=json.dumps(analysis.get("role_specific_recommendations", analysis.get("improvements", []))),
                keywords_missing=json.dumps(analysis.get("keywords_missing", [])),
                role_specific_recommendations=json.dumps(analysis.get("role_specific_recommendations", [])),
                what_to_keep=json.dumps(analysis.get("what_to_keep", [])),
                what_to_change=json.dumps(analysis.get("what_to_change", [])),
                company_match_score=analysis.get("company_match_score", 0),
                summary=analysis.get("summary", "")
            )
            db.add(feedback)
            db.commit()
        
        return resume
    
    @staticmethod
    async def analyze_resume(resume_content: str, target_company: str = None, target_role: str = None, job_description: str = None):
        """
        Analyze resume with ATS scoring, role-specific recommendations, and what to keep/change
        Uses OpenRouter (primary) with Groq fallback for comprehensive analysis
        """
        try:
            # Get the LLM router instance
            llm_router = get_llm_router()
            
            # Limit resume content to prevent token overflow
            limited_content = resume_content[:8000]
            
            # Use provided role or default to Software Engineer
            role = target_role or "Software Engineer"
            
            # Generate comprehensive resume analysis
            analysis_data = await llm_router.generate_resumeai_analysis(
                resume_content=limited_content,
                candidate_role=role,
                target_company=target_company,
                target_job_description=job_description
            )
            
            # Ensure all required fields are present
            result = {
                "overall_score": analysis_data.get("overall_score", 7.5),
                "ats_score": analysis_data.get("ats_score", 75),
                "ats_breakdown": analysis_data.get("ats_breakdown", {
                    "score_reason": "Resume ATS compatibility needs evaluation",
                    "red_flags": [],
                    "improvements": ["Review formatting for ATS compatibility"]
                }),
                "strengths": analysis_data.get("strengths", []),
                "gaps": analysis_data.get("gaps", []),
                "role_specific_recommendations": analysis_data.get("role_specific_recommendations", analysis_data.get("improvements", [])),
                "what_to_keep": analysis_data.get("what_to_keep", []),
                "what_to_change": analysis_data.get("what_to_change", []),
                "company_match_score": analysis_data.get("company_match_score", 0),
                "keywords_missing": analysis_data.get("keywords_missing", []),
                "suggested_summary": analysis_data.get("suggested_summary", ""),
                "best_fit_roles": analysis_data.get("best_fit_roles", []),
                "summary": analysis_data.get("summary", "")
            }
            
            return result
            
        except Exception as e:
            print(f"Error analyzing resume: {e}")
            # Fallback to basic analysis
            return {
                "overall_score": 7.5,
                "ats_score": 75,
                "ats_breakdown": {
                    "score_reason": "Manual review recommended",
                    "red_flags": ["Unable to perform automated analysis"],
                    "improvements": ["Try uploading again or contact support"]
                },
                "strengths": ["Work experience listed", "Technical skills mentioned"],
                "gaps": ["Limited quantified achievements", "Missing project descriptions"],
                "role_specific_recommendations": [
                    "Add specific project details with measurable outcomes",
                    "Quantify achievements (e.g., 'Improved X by Y%')",
                    "Include relevant technical skills for the target role"
                ],
                "what_to_keep": ["Current structure", "Educational background"],
                "what_to_change": ["Add metrics to achievements", "Expand project descriptions"],
                "company_match_score": 0,
                "keywords_missing": ["Leadership", "Technical Skills Relevant to Role"],
                "suggested_summary": f"Professional seeking {target_role or 'growth'} opportunity{f' at {target_company}' if target_company else ''}.",
                "best_fit_roles": [target_role or "Software Engineer"],
                "summary": "Resume analysis unavailable - please try again"
            }
    
    @staticmethod
    def get_user_resumes(db: Session, user_id: int):
        """Get all resumes for user"""
        return db.query(ResumeUpload).filter(
            ResumeUpload.user_id == user_id
        ).order_by(ResumeUpload.id.desc()).all()

