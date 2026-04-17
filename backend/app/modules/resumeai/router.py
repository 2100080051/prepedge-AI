from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.auth.dependencies import get_current_user
from app.database.models import User
from app.modules.resumeai.service import ResumeAIService
from app.llm.provider import get_llm_router
from datetime import datetime
import json

# Common company role requirements database
COMPANY_JOB_REQUIREMENTS = {
    "Google": {
        "Software Engineer": {
            "description": "Build and improve the software that powers Google's services",
            "requirements": "Experience with Python, Java, C++, or JavaScript; Strong data structures knowledge; System design experience; Problem-solving skills; Familiarity with distributed systems",
            "key_skills": ["Data Structures", "Algorithms", "System Design", "Python", "Java", "C++", "JavaScript", "Distributed Systems"],
            "experience_level": "3+ years"
        },
        "Product Manager": {
            "description": "Drive product strategy and execution for Google services",
            "requirements": "5+ years of product management; Strong analytical skills; User research experience; Cross-functional leadership; Understanding of technology landscape",
            "key_skills": ["Product Strategy", "Analytics", "User Research", "Leadership", "Communication", "Technical Acumen"],
            "experience_level": "5+ years"
        }
    },
    "Meta": {
        "Software Engineer": {
            "description": "Work on products and infrastructure used by billions",
            "requirements": "Strong CS fundamentals; Experience with backend systems; Knowledge of databases and caching; Python, C++, or Java; Distributed systems experience",
            "key_skills": ["Backend Development", "Databases", "C++", "Python", "Distributed Systems", "Problem Solving"],
            "experience_level": "2+ years"
        },
        "Data Scientist": {
            "description": "Analyze data to solve business problems",
            "requirements": "Strong statistics and machine learning knowledge; Python/R proficiency; Experience with data visualization; A/B testing knowledge; SQL expertise",
            "key_skills": ["Machine Learning", "Statistics", "Python", "R", "SQL", "A/B Testing", "Data Visualization"],
            "experience_level": "3+ years"
        }
    },
    "Microsoft": {
        "Software Engineer": {
            "description": "Design and build cloud solutions",
            "requirements": "Expert level CS fundamentals; Cloud platform experience (Azure preferred); C#, C++, or Java; Microservices knowledge; Strong communication skills",
            "key_skills": ["Azure", "Cloud Development", "C#", "Microservices", "REST APIs", ".NET", "SQL Server"],
            "experience_level": "3+ years"
        },
        "DevOps Engineer": {
            "description": "Build and maintain infrastructure and deployment systems",
            "requirements": "Linux administration; CI/CD pipeline experience; Infrastructure as Code (Terraform/CloudFormation); Docker/Kubernetes; Python/Bash scripting",
            "key_skills": ["Kubernetes", "Docker", "CI/CD", "Terraform", "Linux", "Python", "Azure/AWS", "Infrastructure as Code"],
            "experience_level": "2+ years"
        }
    },
    "Amazon": {
        "Software Development Engineer": {
            "description": "Build Amazon's scale and reliability",
            "requirements": "5+ years of professional software development; Experience with distributed systems; AWS knowledge; Java/C++/Python; Strong problem-solving",
            "key_skills": ["AWS", "Java", "Distributed Systems", "Databases", "Scalability", "Problem Solving"],
            "experience_level": "5+ years"
        },
        "Solutions Architect": {
            "description": "Design cloud solutions for enterprise customers",
            "requirements": "7+ years of IT experience; 3+ years of cloud architecture; Deep AWS knowledge; Strong communication; Business acumen",
            "key_skills": ["AWS", "Cloud Architecture", "Solution Design", "Business Analysis", "Enterprise Systems"],
            "experience_level": "7+ years"
        }
    },
    "Apple": {
        "Software Engineer": {
            "description": "Create incredible products that enrich lives",
            "requirements": "5+ years of software development; iOS/macOS development experience; Objective-C or Swift; Strong attention to detail; Unix/Linux knowledge",
            "key_skills": ["Swift", "Objective-C", "iOS", "macOS", "Cocoa", "Unix/Linux", "Performance Optimization"],
            "experience_level": "5+ years"
        }
    },
    "Netflix": {
        "Software Engineer": {
            "description": "Build the entertainment platform",
            "requirements": "5+ years of software development; Microservices and distributed systems; Java or Scala; AWS experience; Data processing knowledge",
            "key_skills": ["Java", "Scala", "Microservices", "AWS", "Kafka", "Big Data", "Spring Framework"],
            "experience_level": "5+ years"
        }
    },
    "Stripe": {
        "Software Engineer": {
            "description": "Build payment infrastructure",
            "requirements": "4+ years of software development; Experience with payments or financial systems; Strong systems thinking; Python, Go, or Rust; Attention to security",
            "key_skills": ["Python", "Go", "Database Design", "API Design", "Security", "Payments", "Distributed Systems"],
            "experience_level": "4+ years"
        },
        "Product Manager": {
            "description": "Shape payment product strategy",
            "requirements": "3+ years of product management; Fintech experience preferred; Analytical mindset; Stakeholder management; Technical understanding",
            "key_skills": ["Product Strategy", "Analytics", "Customer Discovery", "Fintech", "Technical Communication"],
            "experience_level": "3+ years"
        }
    },
    "Uber": {
        "Software Engineer": {
            "description": "Scale platform for global rides and food",
            "requirements": "3+ years production experience; Large-scale distributed systems; Strong OOP fundamentals; Java, Go, or Python; System design",
            "key_skills": ["Distributed Systems", "Java", "Go", "Python", "Geospatial", "Real-time Processing", "Microservices"],
            "experience_level": "3+ years"
        },
        "Data Scientist": {
            "description": "Drive ML innovations in ridesharing and delivery",
            "requirements": "3+ years ML experience; Python/R; Statistical analysis; SQL; Experience with recommender systems or NLP; Experiment design",
            "key_skills": ["Python", "Machine Learning", "Statistical Analysis", "SQL", "TensorFlow", "Spark", "A/B Testing"],
            "experience_level": "3+ years"
        }
    },
    "Tesla": {
        "Software Engineer": {
            "description": "Build autonomous driving and vehicle software",
            "requirements": "4+ years embedded/systems programming; C++ expertise; Real-time systems; Vehicle software experience preferred; Strong fundamentals",
            "key_skills": ["C++", "Embedded Systems", "Python", "Real-time Systems", "CUDA", "ROS", "Deep Learning"],
            "experience_level": "4+ years"
        },
        "ML Engineer": {
            "description": "Advance autonomous vehicle perception",
            "requirements": "3+ years ML; Computer vision experience; PyTorch/TensorFlow; Dataset annotation knowledge; Vehicle domain knowledge helpful",
            "key_skills": ["Computer Vision", "PyTorch", "Python", "CUDA", "Deep Learning", "Image Processing", "Dataset Engineering"],
            "experience_level": "3+ years"
        }
    },
    "OpenAI": {
        "Research Engineer": {
            "description": "Push boundaries of AI research",
            "requirements": "3+ years ML/AI research; Deep learning fundamentals; Python; Published papers preferred; Strong mathematical foundation; Initiative",
            "key_skills": ["Deep Learning", "Python", "PyTorch", "Math/Statistics", "Model Training", "Research", "CUDA"],
            "experience_level": "3+ years"
        },
        "Software Engineer": {
            "description": "Build products powered by large language models",
            "requirements": "3+ years production software; API design; Scalability mindset; Python/TypeScript; Experience with LLMs helpful",
            "key_skills": ["Python", "TypeScript", "API Design", "LLMs", "Database Design", "Scalability", "DevOps"],
            "experience_level": "3+ years"
        }
    },
    "Goldman Sachs": {
        "Software Engineer": {
            "description": "Build financial technology platforms",
            "requirements": "3+ years engineering; Financial systems knowledge; Java/C++; Strong problem-solving; Understanding of trading systems preferred",
            "key_skills": ["Java", "C++", "Financial Systems", "Databases", "Distributed Systems", "Python", "Low-latency Programming"],
            "experience_level": "3+ years"
        },
        "Quantitative Researcher": {
            "description": "Develop trading algorithms and models",
            "requirements": "PhD in Math/Physics or strong technical background; Python; Strong statistics; Market knowledge; Backtesting experience",
            "key_skills": ["Python", "Statistics", "Mathematical Modeling", "Market Knowledge", "Backtesting", "Machine Learning"],
            "experience_level": "PhD or equivalent"
        }
    },
    "JPMorgan Chase": {
        "Technology Analyst": {
            "description": "Build banking and trading systems",
            "requirements": "1-3 years experience; Java/Python; Problem-solving skills; Understanding of financial products; Team collaboration",
            "key_skills": ["Java", "Python", "SQL", "Spring Framework", "Databases", "Trading Systems", "Financial Knowledge"],
            "experience_level": "1-3 years"
        }
    },
    "LinkedIn": {
        "Software Engineer": {
            "description": "Connect the world's professionals",
            "requirements": "3+ years production software; Scalability at LinkedIn's scale; Java or Scala; Analytics and BI systems knowledge helpful",
            "key_skills": ["Java", "Scala", "Distributed Systems", "Analytics", "SQL", "Spark", "Large-scale Data"],
            "experience_level": "3+ years"
        }
    },
    "Twitter": {
        "Software Engineer": {
            "description": "Build real-time communication platform",
            "requirements": "3+ years systems engineering; Real-time data pipelines; Scala/Python; Stream processing; Twitter platform knowledge helpful",
            "key_skills": ["Scala", "Python", "Stream Processing", "Kafka", "Distributed Systems", "Real-time Analytics"],
            "experience_level": "3+ years"
        }
    },
    "Intel": {
        "Hardware Engineer": {
            "description": "Design next-generation processors",
            "requirements": "5+ years chip design; Verilog/VHDL; CPU architecture; Physical design knowledge; EDA tools experience",
            "key_skills": ["Verilog", "VHDL", "CPU Architecture", "Physical Design", "SystemC", "EDA Tools", "Power/Timing Analysis"],
            "experience_level": "5+ years"
        }
    },
    "NVIDIA": {
        "GPU Software Engineer": {
            "description": "Optimize software for NVIDIA GPUs",
            "requirements": "3+ years GPU programming; CUDA expertise; C++; Performance optimization; Understanding of parallel computing",
            "key_skills": ["CUDA", "C++", "GPU Programming", "Parallel Computing", "Performance Optimization", "Python", "TensorFlow"],
            "experience_level": "3+ years"
        }
    },
    "Airbnb": {
        "Full Stack Engineer": {
            "description": "Build travel experience platform",
            "requirements": "3+ years full-stack development; React/JavaScript frontend; Backend (any language); Scalability experience; Travel industry helpful",
            "key_skills": ["React", "JavaScript", "Node.js", "Python", "AWS", "SQL", "Product Thinking"],
            "experience_level": "3+ years"
        }
    },
    "Snap": {
        "Software Engineer": {
            "description": "Build Snapchat platform",
            "requirements": "3+ years mobile/backend; Android/iOS or backend systems; Real-time app experience; Camera/imaging helpful; C++/Java/Python",
            "key_skills": ["Android", "iOS", "C++", "Java", "Real-time Systems", "Image Processing", "Mobile Optimization"],
            "experience_level": "3+ years"
        }
    },
    "Databricks": {
        "Software Engineer": {
            "description": "Build data and ML platform",
            "requirements": "3+ years distributed systems; Big data experience; Spark knowledge; Scala or Python; Database internals helpful",
            "key_skills": ["Scala", "Python", "Spark", "Distributed Systems", "Database Systems", "Data Engineering", "Distributed Computing"],
            "experience_level": "3+ years"
        }
    },
    "Figma": {
        "Software Engineer": {
            "description": "Build collaborative design platform",
            "requirements": "3+ years systems design; WebGL or graphics experience; Real-time collaboration; JavaScript/TypeScript; Scalability at scale",
            "key_skills": ["TypeScript", "JavaScript", "WebGL", "Real-time Sync", "Graphics Programming", "React", "Distributed Systems"],
            "experience_level": "3+ years"
        }
    },
    "Canva": {
        "Software Engineer": {
            "description": "Democratize design tools",
            "requirements": "2+ years production software; Frontend or backend systems; JavaScript/Python/Java; User-focused product thinking",
            "key_skills": ["JavaScript", "React", "Python", "AWS", "Scalable Architecture", "UX Focus", "SQL/NoSQL"],
            "experience_level": "2+ years"
        }
    },
    "Notion": {
        "Software Engineer": {
            "description": "Build all-in-one workspace",
            "requirements": "2+ years full-stack; React and Node/backend; Real-time collaboration; Document editing; Performance optimization",
            "key_skills": ["React", "TypeScript", "Node.js", "Real-time Sync", "Database Design", "Performance", "Architecture"],
            "experience_level": "2+ years"
        }
    },
    "Spotify": {
        "Backend Engineer": {
            "description": "Power music streaming at scale",
            "requirements": "3+ years backend development; Large-scale distributed systems; JVM languages or Go; Kafka experience; Data pipelines",
            "key_skills": ["Scala", "Java", "Go", "Kafka", "Distributed Systems", "SQL", "Microservices", "Analytics"],
            "experience_level": "3+ years"
        }
    },
    "Grammarly": {
        "ML Engineer": {
            "description": "Build AI writing assistant",
            "requirements": "3+ years ML; NLP focus; Python; Understanding of linguistics helpful; Hypothesis-driven approach; TensorFlow/PyTorch",
            "key_skills": ["Python", "NLP", "TensorFlow", "PyTorch", "ML Operations", "Statistical Analysis", "Writing Systems"],
            "experience_level": "3+ years"
        }
    },
    "Dropbox": {
        "Software Engineer": {
            "description": "Build file sync and cloud storage",
            "requirements": "3+ years systems software; C++/Python; File systems or sync engines; Distributed systems; Performance critical",
            "key_skills": ["C++", "Python", "Distributed Systems", "File Systems", "Performance Optimization", "Sync Engines"],
            "experience_level": "3+ years"
        }
    },
    "GitHub": {
        "Software Engineer": {
            "description": "Build developer platform",
            "requirements": "3+ years web development; GitHub/Git understanding; Ruby/Rails or similar; Performance at scale; Open source contribution",
            "key_skills": ["Ruby", "Rails", "JavaScript", "Git", "Distributed Systems", "Database", "Developer Tools"],
            "experience_level": "3+ years"
        }
    }
}

router = APIRouter(prefix="/resumeai", tags=["resumeai"])

@router.post("/upload")
async def upload_resume(
    file: UploadFile = File(...),
    target_company: str = None,
    target_role: str = None,
    job_description: str = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload and analyze a resume with ATS scoring and role-specific recommendations.
    
    Parameters:
    - file: Resume file (txt, pdf, doc, docx)
    - target_company: Company the resume is for (e.g., "Google", "Microsoft")
    - target_role: Target role (e.g., "Senior Software Engineer")
    - job_description: Job requirements (optional, for detailed matching)
    
    Returns: Comprehensive analysis with:
    - ATS score and breakdown
    - Strengths and gaps for the target role
    - Role-specific recommendations
    - What to KEEP (already good for this role)
    - What to CHANGE (needs updating for this role)
    - Company match score
    """
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

    # Run AI analysis with role/company context
    analysis = await ResumeAIService.analyze_resume(
        resume_content=text_content,
        target_company=target_company,
        target_role=target_role,
        job_description=job_description
    )

    # Save to DB with role/company context
    ResumeAIService.save_resume(
        db=db,
        user_id=current_user.id,
        filename=file.filename,
        content=text_content,
        analysis=analysis,
        target_company=target_company,
        target_role=target_role,
        job_description=job_description
    )

    # Return comprehensive response
    return {
        "filename": file.filename,
        "target_company": target_company or "Not specified",
        "target_role": target_role or "Not specified",
        "overall_score": analysis.get("overall_score", 0),
        "ats_score": analysis.get("ats_score", 0),
        "ats_breakdown": analysis.get("ats_breakdown", {}),
        "strengths": analysis.get("strengths", []),
        "gaps": analysis.get("gaps", []),
        "role_specific_recommendations": analysis.get("role_specific_recommendations", []),
        "what_to_keep": analysis.get("what_to_keep", []),
        "what_to_change": analysis.get("what_to_change", []),
        "company_match_score": analysis.get("company_match_score", 0),
        "keywords_missing": analysis.get("keywords_missing", []),
        "suggested_summary": analysis.get("suggested_summary", ""),
        "best_fit_roles": analysis.get("best_fit_roles", []),
        "summary": analysis.get("summary", ""),
    }

@router.get("/feedback")
def get_resume_feedback(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get resume analysis history for the current user with role/company context"""
    resumes = ResumeAIService.get_user_resumes(db, current_user.id)
    result = []
    for r in resumes:
        fb = r.feedback[0] if r.feedback else None
        result.append({
            "id": r.id,
            "filename": r.file_path,
            "target_company": r.target_company,
            "target_role": r.target_role,
            "overall_score": r.score,
            "created_at": str(r.created_at),
            "ats_score": fb.ats_score if fb else 0,
            "ats_breakdown": json.loads(fb.ats_breakdown) if fb and hasattr(fb, 'ats_breakdown') and fb.ats_breakdown else {},
            "strengths": json.loads(fb.strengths) if fb and fb.strengths else [],
            "improvements": json.loads(fb.improvements) if fb and fb.improvements else [],
            "role_specific_recommendations": json.loads(fb.role_specific_recommendations) if fb and hasattr(fb, 'role_specific_recommendations') and fb.role_specific_recommendations else [],
            "what_to_keep": json.loads(fb.what_to_keep) if fb and hasattr(fb, 'what_to_keep') and fb.what_to_keep else [],
            "what_to_change": json.loads(fb.what_to_change) if fb and hasattr(fb, 'what_to_change') and fb.what_to_change else [],
            "company_match_score": fb.company_match_score if fb and hasattr(fb, 'company_match_score') else 0,
            "keywords_missing": json.loads(fb.keywords_missing) if fb and fb.keywords_missing else [],
            "summary": fb.summary if fb else ""
        })
    return result

@router.get("/companies")
def get_companies():
    """Get list of companies with job requirements"""
    return {
        "companies": list(COMPANY_JOB_REQUIREMENTS.keys()),
        "total": len(COMPANY_JOB_REQUIREMENTS)
    }

@router.get("/companies/{company}")
def get_company_roles(company: str):
    """Get available roles for a specific company"""
    company = company.title()  # Convert to title case to match keys
    
    if company not in COMPANY_JOB_REQUIREMENTS:
        raise HTTPException(status_code=404, detail=f"Company '{company}' not found")
    
    roles = COMPANY_JOB_REQUIREMENTS[company]
    return {
        "company": company,
        "roles": list(roles.keys()),
        "total_roles": len(roles)
    }

@router.get("/companies/{company}/{role}")
def get_job_requirements(company: str, role: str):
    """Get job requirements for a specific company and role"""
    company = company.title()
    role = role.title()
    
    if company not in COMPANY_JOB_REQUIREMENTS:
        raise HTTPException(status_code=404, detail=f"Company '{company}' not found")
    
    if role not in COMPANY_JOB_REQUIREMENTS[company]:
        raise HTTPException(status_code=404, detail=f"Role '{role}' not found for {company}")
    
    requirements = COMPANY_JOB_REQUIREMENTS[company][role]
    return {
        "company": company,
        "role": role,
        "description": requirements["description"],
        "requirements": requirements["requirements"],
        "key_skills": requirements["key_skills"],
        "experience_level": requirements["experience_level"],
        "optimization_tips": [
            f"Ensure all these skills are clearly mentioned: {', '.join(requirements['key_skills'][:3])}",
            "Add quantifiable achievements and metrics to your experience",
            f"Highlight projects that demonstrate {requirements['key_skills'][0]} expertise",
            "Use industry-standard terminology from the job description",
            "Include relevant certifications or training",
            "Show continuous learning and skill development"
        ]
    }

@router.post("/analyze-for-job")
async def analyze_resume_for_job(
    file: UploadFile = File(...),
    company: str = None,
    role: str = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Analyze resume for a specific company and role.
    Use predefined job requirements if company and role are provided.
    """
    if not file.filename.lower().endswith(('.txt', '.pdf', '.doc', '.docx')):
        raise HTTPException(status_code=400, detail="Unsupported file type")
    
    content = await file.read()
    
    try:
        text_content = ResumeAIService.extract_resume_text(content, file.filename)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Could not extract text: {str(e)}")
    
    # Get job description from database if company and role provided
    job_desc = None
    if company and role:
        company = company.title()
        role = role.title()
        if company in COMPANY_JOB_REQUIREMENTS and role in COMPANY_JOB_REQUIREMENTS[company]:
            req = COMPANY_JOB_REQUIREMENTS[company][role]
            job_desc = f"""
Position: {role} at {company}

Description: {req['description']}

Requirements: {req['requirements']}

Key Skills: {', '.join(req['key_skills'])}

Experience Required: {req['experience_level']}
"""
    
    # Analyze resume
    analysis = await ResumeAIService.analyze_resume(
        resume_content=text_content,
        target_company=company,
        target_role=role,
        job_description=job_desc
    )
    
    # Save to DB
    ResumeAIService.save_resume(
        db=db,
        user_id=current_user.id,
        filename=file.filename,
        content=text_content,
        analysis=analysis,
        target_company=company,
        target_role=role,
        job_description=job_desc
    )
    
    return {
        "filename": file.filename,
        "target_company": company or "Not specified",
        "target_role": role or "Not specified",
        "overall_score": analysis.get("overall_score", 0),
        "ats_score": analysis.get("ats_score", 0),
        "ats_breakdown": analysis.get("ats_breakdown", {}),
        "strengths": analysis.get("strengths", []),
        "gaps": analysis.get("gaps", []),
        "role_specific_recommendations": analysis.get("role_specific_recommendations", []),
        "what_to_keep": analysis.get("what_to_keep", []),
        "what_to_change": analysis.get("what_to_change", []),
        "company_match_score": analysis.get("company_match_score", 0),
        "keywords_missing": analysis.get("keywords_missing", []),
        "suggested_summary": analysis.get("suggested_summary", ""),
        "summary": analysis.get("summary", ""),
    }

@router.post("/generate-cover-letter")
async def generate_cover_letter(
    company: str,
    job_title: str,
    resume_content: str,
    job_description: str = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate professional cover letter for a specific job.
    
    Parameters:
    - company: Company name (e.g., "Google")
    - job_title: Job title (e.g., "Senior Software Engineer")
    - resume_content: Your resume text/content
    - job_description: Detailed job description (optional)
    
    Returns: Cover letter in multiple formats (formal, confident, personable)
    """
    try:
        llm_router = get_llm_router()
        
        # Generate cover letter using LLM
        cover_letter_data = await llm_router.generate_cover_letter(
            resume_content=resume_content,
            company_name=company,
            job_title=job_title,
            job_description=job_description
        )
        
        return {
            "company": company,
            "job_title": job_title,
            "cover_letter": cover_letter_data.get("cover_letter", ""),
            "opening": cover_letter_data.get("opening", ""),
            "variations": cover_letter_data.get("variations", {}),
            "tips": cover_letter_data.get("tips", []),
            "keywords_to_highlight": cover_letter_data.get("keywords_to_highlight", []),
            "generated_at": str(datetime.utcnow())
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cover letter generation failed: {str(e)}")
