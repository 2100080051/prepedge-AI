from sqlalchemy.orm import Session
from app.database.models import ResumeUpload, ResumeFeedback
import os
from io import BytesIO


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
        """Extract text from PDF"""
        text = ""
        try:
            import PyPDF2
            pdf_reader = PyPDF2.PdfReader(BytesIO(contents))
            for page in pdf_reader.pages:
                text += page.extract_text()
        except Exception as e:
            print(f"PDF extraction error: {e}")
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
    def save_resume(db: Session, user_id: int, filename: str, content: str, analysis: dict = None):
        """Save resume to database"""
        resume = ResumeUpload(
            user_id=user_id,
            file_path=filename,
            content=content[:10000],
            score=analysis.get("score", 7.0) if analysis else 7.0
        )
        db.add(resume)
        db.commit()
        db.refresh(resume)
        
        # Save feedback if analysis is provided
        if analysis:
            feedback = ResumeFeedback(
                resume_id=resume.id,
                ats_score=analysis.get("ats_score", 0),
                strengths=str(analysis.get("strengths", [])),
                gaps=str(analysis.get("gaps", [])),
                improvements=str(analysis.get("improvements", [])),
                keywords_missing=str(analysis.get("keywords_missing", [])),
                summary=analysis.get("summary", "")
            )
            db.add(feedback)
            db.commit()
        
        return resume
    
    @staticmethod
    def analyze_resume(resume_content: str):
        """Analyze resume and return feedback"""
        return {
            "score": 7.5,
            "ats_score": 75,
            "detected_domain": "Technology/Software Development",
            "candidate_name": "Candidate",
            "strengths": [
                "Clear work experience section",
                "Good technical skills listing",
                "Professional formatting"
            ],
            "gaps": [
                "Missing specific project descriptions",
                "Limited quantified achievements",
                "No measurable impact statements"
            ],
            "improvements": [
                "Add 2-3 key projects with measurable impact",
                "Quantify achievements (e.g., 'Improved X by 40%')",
                "Add specific technical skills with proficiency levels",
                "Include links to portfolio or GitHub for tech roles",
                "Add relevant certifications or courses"
            ],
            "keywords_missing": [
                "Leadership",
                "Cross-functional collaboration",
                "Agile/Scrum",
                "Cloud technologies"
            ],
            "suggested_summary": "Results-driven professional with solid technical foundation. Proven ability to [key achievement]. Seeking to leverage expertise in [domain] to drive business impact.",
            "best_fit_roles": [
                "Software Engineer",
                "Systems Developer",
                "Technical Analyst",
                "Solutions Architect"
            ],
            "top_companies_to_target": [
                "FAANG companies (Facebook, Apple, Amazon, Netflix, Google)",
                "Startups in Series B-C funding stage",
                "Tech consulting firms (Accenture, TCS, Infosys)"
            ],
            "what_to_learn_next": [
                "Advanced cloud technologies (AWS, Azure, GCP)",
                "Leadership and management skills",
                "Data structures and system design",
                "Product management fundamentals"
            ],
            "encouragement": "Your resume shows great potential! With some strategic updates focusing on quantifiable achievements and specific project details, you'll be well-positioned for senior-level roles.",
            "summary": "Your resume shows solid foundational experience. Focus on quantifying achievements and adding specific project details to improve ATS score and stand out to recruiters."
        }
    
    @staticmethod
    def get_user_resumes(db: Session, user_id: int):
        """Get all resumes for user"""
        return db.query(ResumeUpload).filter(
            ResumeUpload.user_id == user_id
        ).order_by(ResumeUpload.id.desc()).all()
    
    @staticmethod
    def get_resume_feedback(db: Session, user_id: int):
        """Get resume feedback for user"""
        return ResumeAIService.get_user_resumes(db, user_id)

