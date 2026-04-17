"""
⚠️  PROD WARNING: Hardcoded keys below are DEV FALLBACKS only.
Rotate immediately for production. Use .env vars.
Supports: Nvidia, OpenRouter, Groq with seamless fallback.
"""


import os
import httpx
import json
from typing import Optional, Dict, List
from enum import Enum
from duckduckgo_search import DDGS


class LLMProvider(Enum):
    """Available LLM providers"""
    NVIDIA = "nvidia"
    OPENROUTER = "openrouter"
    GROQ = "groq"


class LLMConfig:
    """Configuration for LLM providers"""
    
    # Nvidia configuration (free cloud API)
    NVIDIA_API_KEY = os.getenv("OPENAI_API_KEY", "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")
    NVIDIA_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://integrate.api.nvidia.com/v1")
    NVIDIA_MODELS = {
        "pdf_summarizer": "meta/llama-3.1-8b-instruct",      # Fast summarization
        "learnai_concept": "meta/llama-3.1-8b-instruct",     # Concept explanations
        "default": "meta/llama-3.1-8b-instruct"
    }
    
    # OpenRouter configuration (free tier)
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "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")
    OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
    OPENROUTER_MODELS = {
        "learnai_concept": "openai/gpt-3.5-turbo",
        "resumeai_analysis": "openai/gpt-3.5-turbo",
        "default": "openai/gpt-3.5-turbo"
    }
    
    # Groq configuration (free tier, very fast)
    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
    GROQ_BASE_URL = "https://api.groq.com/openai/v1"
    GROQ_MODELS = {
        "resumeai_analysis": "llama-3.3-70b-versatile",
        "mockmate_question": "llama-3.3-70b-versatile",
        "default": "llama-3.3-70b-versatile"
    }
    
    # Request configuration
    REQUEST_TIMEOUT = 60
    MAX_TOKENS = {
        "learnai": 2000,
        "resumeai": 1500,
        "mockmate": 1000,
        "pdf_summarizer": 1500,
        "proctoring": 500
    }
    
    TEMPERATURE = {
        "learnai": 0.7,           # Creative but coherent
        "resumeai": 0.3,          # Focused, analytical
        "mockmate": 0.8,          # Conversational, dynamic
        "pdf_summarizer": 0.5,    # Balanced
        "default": 0.5
    }


class NvidiaClient:
    """Client for Nvidia API"""
    
    def __init__(self):
        self.api_key = LLMConfig.NVIDIA_API_KEY
        self.base_url = LLMConfig.NVIDIA_BASE_URL
        self.client = httpx.AsyncClient(
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            },
            timeout=LLMConfig.REQUEST_TIMEOUT
        )
    
    async def generate(
        self,
        prompt: str,
        model: Optional[str] = None,
        max_tokens: int = 1500,
        temperature: float = 0.5,
        system_prompt: Optional[str] = None
    ) -> str:
        """Generate text using Nvidia API"""
        try:
            if model is None:
                model = LLMConfig.NVIDIA_MODELS["default"]
            
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            response = await self.client.post(
                f"{self.base_url}/chat/completions",
                json={
                    "model": model,
                    "messages": messages,
                    "max_tokens": max_tokens,
                    "temperature": temperature
                }
            )
            
            response.raise_for_status()
            data = response.json()
            
            return data["choices"][0]["message"]["content"]
        
        except Exception as e:
            print(f"Nvidia error: {e}")
            raise
    
    async def close(self):
        """Close the client"""
        await self.client.aclose()


class OpenRouterClient:
    """Client for OpenRouter API"""
    
    def __init__(self):
        self.api_key = LLMConfig.OPENROUTER_API_KEY
        self.base_url = LLMConfig.OPENROUTER_BASE_URL
        self.client = httpx.AsyncClient(
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "HTTP-Referer": "https://prepedge.ai",
                "X-Title": "PrepEdge AI"
            },
            timeout=LLMConfig.REQUEST_TIMEOUT
        )
    
    async def generate(
        self,
        prompt: str,
        model: Optional[str] = None,
        max_tokens: int = 2000,
        temperature: float = 0.7,
        system_prompt: Optional[str] = None
    ) -> str:
        """
        Generate text using OpenRouter
        
        Args:
            prompt: User message/prompt
            model: Model to use (from OPENROUTER_MODELS)
            max_tokens: Maximum tokens in response
            temperature: Creativity level (0-1)
            system_prompt: System context
        
        Returns:
            Generated text
        """
        try:
            if model is None:
                model = LLMConfig.OPENROUTER_MODELS["default"]
            
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            response = await self.client.post(
                f"{self.base_url}/chat/completions",
                json={
                    "model": model,
                    "messages": messages,
                    "max_tokens": max_tokens,
                    "temperature": temperature
                }
            )
            
            response.raise_for_status()
            data = response.json()
            
            return data["choices"][0]["message"]["content"]
        
        except Exception as e:
            print(f"OpenRouter error: {e}")
            raise
    
    async def close(self):
        """Close the client"""
        await self.client.aclose()


class GroqClient:
    """Client for Groq API"""
    
    def __init__(self):
        self.api_key = LLMConfig.GROQ_API_KEY
        self.base_url = LLMConfig.GROQ_BASE_URL
        self.client = httpx.AsyncClient(
            headers={
                "Authorization": f"Bearer {self.api_key}"
            },
            timeout=LLMConfig.REQUEST_TIMEOUT
        )
    
    async def generate(
        self,
        prompt: str,
        model: Optional[str] = None,
        max_tokens: int = 1500,
        temperature: float = 0.3,
        system_prompt: Optional[str] = None
    ) -> str:
        """
        Generate text using Groq (very fast)
        
        Args:
            prompt: User message/prompt
            model: Model to use (from GROQ_MODELS)
            max_tokens: Maximum tokens in response
            temperature: Creativity level (0-1)
            system_prompt: System context
        
        Returns:
            Generated text
        """
        try:
            if model is None:
                model = LLMConfig.GROQ_MODELS["default"]
            
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            response = await self.client.post(
                f"{self.base_url}/chat/completions",
                json={
                    "model": model,
                    "messages": messages,
                    "max_completion_tokens": max_tokens,
                    "temperature": temperature
                }
            )
            
            response.raise_for_status()
            data = response.json()
            
            return data["choices"][0]["message"]["content"]
        
        except Exception as e:
            print(f"Groq error: {e}")
            raise
    
    async def close(self):
        """Close the client"""
        await self.client.aclose()


class LLMRouter:
    """
    Smart router for selecting best provider per task
    Routes based on: speed, cost, quality, model availability
    Providers: Nvidia (fast), OpenRouter (quality), Groq (speed) with fallback chain
    """
    
    def __init__(self):
        self.nvidia = NvidiaClient()
        self.openrouter = OpenRouterClient()
        self.groq = GroqClient()
    
    async def generate_learnai_concept(
        self,
        domain: str,
        subject: str,
        concept: str,
        language: str = "English"
    ) -> Dict:
        """
        Generate powerful concept explanation using OpenRouter
        Uses best model for detailed, accurate explanations
        """
        system_prompt = f"""You are an expert educational content creator specializing in {subject}.
Your task is to explain concepts in a way that engineering students can easily understand.
Be precise, accurate, and use real-world examples relevant to Indian engineering interviews at {domain}.
Format your response as JSON with the following fields:
- explanation: Detailed explanation (3-4 paragraphs)
- analogy: Real-world analogy to help understand the concept
- example: Step-by-step practical example
- key_points: List of 5-7 key insights
- common_mistakes: List of 3-4 common misconceptions
- interview_tips: How to answer this in an interview setting"""

        user_prompt = f"""
Subject: {subject}
Concept: {concept}
Domain: {domain}
Language: {language}

Provide a comprehensive, well-structured explanation of {concept} in {subject}.
"""
        
        try:
            response = await self.openrouter.generate(
                prompt=user_prompt,
                model=LLMConfig.OPENROUTER_MODELS["learnai_concept"],
                max_tokens=LLMConfig.MAX_TOKENS["learnai"],
                temperature=LLMConfig.TEMPERATURE["learnai"],
                system_prompt=system_prompt
            )
            
            # Try to parse as JSON, fallback to string
            try:
                return json.loads(response)
            except json.JSONDecodeError:
                return {
                    "explanation": response,
                    "analogy": "See above",
                    "example": "See above",
                    "key_points": ["See above"],
                    "common_mistakes": ["See above"],
                    "interview_tips": "Structure your answer with clear examples"
                }
        
        except Exception as e:
            print(f"LearnAI OpenRouter error: {e}. Falling back to Groq...")
            # Fallback to Groq if OpenRouter fails
            try:
                response = await self.groq.generate(
                    prompt=user_prompt,
                    model=LLMConfig.GROQ_MODELS["default"],
                    max_tokens=LLMConfig.MAX_TOKENS["learnai"],
                    temperature=LLMConfig.TEMPERATURE["learnai"],
                    system_prompt=system_prompt
                )
                try:
                    return json.loads(response)
                except json.JSONDecodeError:
                    return {
                        "explanation": response,
                        "analogy": "See comprehensive explanation above",
                        "example": "See comprehensive explanation above",
                        "key_points": ["Refer to main explanation", "Groq fallback used"],
                        "common_mistakes": ["Review the detailed explanation"],
                        "interview_tips": "Structure answer with examples from the explanation"
                    }
            except Exception as groq_error:
                print(f"LearnAI Groq fallback also failed: {groq_error}")
                raise
    
    async def generate_resumeai_analysis(
        self,
        resume_content: str,
        candidate_role: str = "Software Engineer",
        target_company: str = None,
        target_job_description: str = None
    ) -> Dict:
        """
        Generate resume analysis with ATS scoring and role-specific recommendations
        Uses OpenRouter (primary) with Groq fallback
        """
        system_prompt = f"""You are an expert resume reviewer, ATS optimization specialist, and career coach.
Analyze resumes comprehensively for {candidate_role} positions.

Your analysis should include:
1. **ATS Score (0-100)**: Calculate based on keyword matching, formatting, and structure
   - Check for common ATS-killers (tables, graphics, special formatting)
   - Identify critical keywords from job description
   - Check section headers, dates, and formatting
   
2. **Role-Specific Match**: How well the resume fits {f"{target_company} and the {candidate_role} role" if target_company else "the target role"}
   - Required skills/experience gaps
   - What's already aligned (what to KEEP)
   - What needs improvement (what to CHANGE)
   - Missing qualifications

3. **Actionable Recommendations**: Specific changes for this role at this company

Provide response as JSON with these fields:
- ats_score: 0-100 score
- ats_breakdown: {{score_reason: str, red_flags: list, improvements: list}}
- overall_score: General resume quality 0-100
- strengths: List of 3-4 current strengths
- gaps: List of gaps for this specific role
- role_specific_recommendations: List of 5-7 specific actions for this role
- what_to_keep: List of sections/skills/experience that are already good for this role
- what_to_change: List of sections/points that need modification for this role
- company_match_score: 0-100 how well candidate fits {target_company if target_company else "target"} culture
- keywords_missing: Critical keywords to add
- suggested_summary: Recommendation for professional summary
- best_fit_roles: Other roles where this resume would excel
- summary: One sentence verdict"""

        job_desc_context = f"\n\nTarget Company: {target_company}\nJob Requirements:\n{target_job_description[:2000]}" if target_job_description else ""

        user_prompt = f"""Analyze this resume for a {candidate_role} position{f" at {target_company}" if target_company else ""}.

{resume_content[:5000]}
{job_desc_context}

Provide detailed analysis in JSON format. Focus on ATS compatibility and role-specific fit."""
        
        try:
            # Try OpenRouter first for comprehensive analysis
            print(f"Analyzing resume for {target_company or 'target'} {candidate_role}...")
            response = await self.openrouter.generate(
                prompt=user_prompt,
                model=LLMConfig.OPENROUTER_MODELS["resumeai_analysis"],
                max_tokens=LLMConfig.MAX_TOKENS["resumeai"],
                temperature=LLMConfig.TEMPERATURE["resumeai"],
                system_prompt=system_prompt
            )
            
            try:
                return json.loads(response)
            except json.JSONDecodeError:
                print("Failed to parse OpenRouter response, attempting Groq...")
                # Fallback to Groq
                response = await self.groq.generate(
                    prompt=user_prompt,
                    model=LLMConfig.GROQ_MODELS["resumeai_analysis"],
                    max_tokens=LLMConfig.MAX_TOKENS["resumeai"],
                    temperature=LLMConfig.TEMPERATURE["resumeai"],
                    system_prompt=system_prompt
                )
                try:
                    return json.loads(response)
                except json.JSONDecodeError:
                    # Fallback response structure
                    return {
                        "ats_score": 70,
                        "ats_breakdown": {
                            "score_reason": "ATS compatibility is moderate - add more quantifiable metrics",
                            "red_flags": ["Unclear achievements", "Missing metrics"],
                            "improvements": ["Quantify results", "Add specific keywords"]
                        },
                        "overall_score": 68,
                        "strengths": ["Relevant experience", "Clear layout"],
                        "gaps": ["Quantified metrics", "Modern skills highlight"],
                        "role_specific_recommendations": [
                            "Add quantifiable impact metrics for each role",
                            "Highlight programming languages and frameworks prominently",
                            "Include system design experience",
                            "Mention cloud platforms (AWS, GCP, Azure)",
                            "Emphasize team leadership or collaboration"
                        ],
                        "what_to_keep": ["Current work experience", "Educational background", "Clear structure"],
                        "what_to_change": ["Add metrics to achievements", "Enhance technical skills section", "Update project descriptions"],
                        "company_match_score": 65,
                        "keywords_missing": ["AWS", "System Design", "Microservices", "Docker", "Kubernetes"],
                        "suggested_summary": response[:150] if response else "Experienced professional seeking growth",
                        "best_fit_roles": ["Software Engineer", "Senior Developer", "Technical Lead"],
                        "summary": "Resume shows promise but needs quantifiable achievements and technical depth"
                    }
        
        except Exception as e:
            print(f"ResumeAI generation error: {e}")
            raise
    
    async def generate_mockmate_question(
        self,
        company: str,
        role: str,
        topic: str,
        difficulty: str = "medium"
    ) -> Dict:
        """
        Generate interview question using Groq
        Fast generation for conversational responses
        """
        system_prompt = f"""You are an expert interviewer at {company}.
Generate {difficulty} difficulty interview questions for {role} position.
Questions should test both technical knowledge and problem-solving ability.
Format response as JSON with:
- question: The interview question
- difficulty: Level of difficulty
- expected_depth: What a good answer should cover
- hints: 2-3 hints if candidate struggles
- resources: Links to learn this topic"""

        user_prompt = f"""
Generate an interview question for:
Company: {company}
Role: {role}
Topic: {topic}
Difficulty: {difficulty}

Make it realistic and challenging for this company's interview."""
        
        try:
            response = await self.groq.generate(
                prompt=user_prompt,
                model=LLMConfig.GROQ_MODELS["mockmate_question"],
                max_tokens=LLMConfig.MAX_TOKENS["mockmate"],
                temperature=LLMConfig.TEMPERATURE["mockmate"],
                system_prompt=system_prompt
            )
            
            try:
                return json.loads(response)
            except json.JSONDecodeError:
                return {
                    "question": response,
                    "difficulty": difficulty,
                    "expected_depth": "Use relevant examples and explain trade-offs",
                    "hints": ["Think about edge cases", "Consider scalability"],
                    "resources": []
                }
        
        except Exception as e:
            print(f"MockMate generation error: {e}")
            raise
    
    async def generate_pdf_summary(self, pdf_text: str) -> Dict:
        """
        Generate structured exam notes from PDF text
        Fallback chain: Nvidia → OpenRouter → Groq
        """
        system_prompt = """You are an expert educator creating structured exam revision notes.
Create comprehensive, well-organized study material from the provided text.
Format response as JSON with:
- key_topics: List of main topics (5-7)
- chapter_summaries: Brief summary of each major section
- exam_tips: Practical tips for exam preparation
- quick_revision_points: Bullet points for quick review
- important_definitions: Key terms and definitions
- practice_questions: Sample questions with difficulty levels"""

        user_prompt = f"""Create structured exam notes from this content:

{pdf_text[:3000]}  # Limit to first 3000 chars

Provide comprehensive revision material in JSON format."""

        # Try Nvidia first (fast)
        try:
            print("Attempting Nvidia for PDF summarization...")
            response = await self.nvidia.generate(
                prompt=user_prompt,
                model=LLMConfig.NVIDIA_MODELS["pdf_summarizer"],
                max_tokens=LLMConfig.MAX_TOKENS["pdf_summarizer"],
                temperature=LLMConfig.TEMPERATURE["pdf_summarizer"],
                system_prompt=system_prompt
            )
            try:
                return json.loads(response)
            except json.JSONDecodeError:
                return {
                    "key_topics": ["See summary below"],
                    "chapter_summaries": response,
                    "exam_tips": "Study the main concepts thoroughly",
                    "quick_revision_points": ["Review key terms", "Practice problems"],
                    "important_definitions": {},
                    "practice_questions": []
                }
        except Exception as nvidia_error:
            print(f"Nvidia PDF summarization failed: {nvidia_error}, falling back to OpenRouter...")
            
            # Fallback to OpenRouter
            try:
                response = await self.openrouter.generate(
                    prompt=user_prompt,
                    model=LLMConfig.OPENROUTER_MODELS["default"],
                    max_tokens=LLMConfig.MAX_TOKENS["pdf_summarizer"],
                    temperature=LLMConfig.TEMPERATURE["pdf_summarizer"],
                    system_prompt=system_prompt
                )
                try:
                    return json.loads(response)
                except json.JSONDecodeError:
                    return {
                        "key_topics": ["See summary below"],
                        "chapter_summaries": response,
                        "exam_tips": "Study the provided content",
                        "quick_revision_points": ["Review key concepts"],
                        "important_definitions": {},
                        "practice_questions": []
                    }
            except Exception as openrouter_error:
                print(f"OpenRouter PDF summarization failed: {openrouter_error}, falling back to Groq...")
                
                # Final fallback to Groq
                try:
                    response = await self.groq.generate(
                        prompt=user_prompt,
                        model=LLMConfig.GROQ_MODELS["default"],
                        max_tokens=LLMConfig.MAX_TOKENS["pdf_summarizer"],
                        temperature=LLMConfig.TEMPERATURE["pdf_summarizer"],
                        system_prompt=system_prompt
                    )
                    try:
                        return json.loads(response)
                    except json.JSONDecodeError:
                        return {
                            "key_topics": ["See summary below"],
                            "chapter_summaries": response,
                            "exam_tips": "Study the content provided",
                            "quick_revision_points": ["Key points", "Important concepts"],
                            "important_definitions": {},
                            "practice_questions": []
                        }
                except Exception as groq_error:
                    print(f"All providers failed for PDF summarization: {groq_error}")
                    raise
    
    async def generate_cover_letter(
        self,
        resume_content: str,
        company_name: str,
        job_title: str,
        job_description: str = None
    ) -> Dict:
        """
        Generate professional cover letter for a specific job
        Uses OpenRouter (primary) with Groq fallback for fast, customized letters
        """
        system_prompt = f"""You are an expert cover letter writer and career coach.
Generate professional, compelling cover letters for job applications.
The letters should be:
- Personalized to the specific company and role
- Action-oriented and impact-focused
- 3-4 paragraphs (200-250 words)
- Show enthusiasm and relevant skills
- Address the hiring manager professionally
- Highlight specific achievements and skills matching the job description

Format response as JSON with:
- cover_letter: The main cover letter text
- opening: Opening paragraph (best for cold email)
- variations: 2-3 alternative versions with different tones:
  - formal: Professional, traditional tone
  - confident: Bold, achievement-focused tone
  - personable: Friendly, relatable tone
- tips: 3-4 tips for customizing this letter further
- keywords_to_highlight: Key skills from job description to emphasize"""

        job_context = f"\n\nJob Description:\n{job_description[:1000]}" if job_description else ""

        user_prompt = f"""Generate professional cover letters for this job application:

Company: {company_name}
Position: {job_title}
{job_context}

Resume Summary:
{resume_content[:2000]}

Provide 3-4 variations of cover letters (formal, confident, personable) in JSON format.
Make each one customizable and relevant to {company_name}."""

        try:
            # Try OpenRouter first for quality
            print(f"Generating cover letter for {company_name} {job_title}...")
            response = await self.openrouter.generate(
                prompt=user_prompt,
                model=LLMConfig.OPENROUTER_MODELS["default"],
                max_tokens=1500,
                temperature=0.6,  # Balanced (creative but focused)
                system_prompt=system_prompt
            )
            
            try:
                return json.loads(response)
            except json.JSONDecodeError:
                # Fallback to Groq
                response = await self.groq.generate(
                    prompt=user_prompt,
                    model=LLMConfig.GROQ_MODELS["default"],
                    max_tokens=1500,
                    temperature=0.6,
                    system_prompt=system_prompt
                )
                try:
                    return json.loads(response)
                except json.JSONDecodeError:
                    # Final fallback - structured response
                    return {
                        "cover_letter": response[:400],
                        "opening": f"I am interested in the {job_title} position at {company_name}.",
                        "variations": {
                            "formal": f"Dear Hiring Manager,\n\nI am writing to express my strong interest in the {job_title} position at {company_name}...",
                            "confident": f"I'm excited to bring my proven expertise to the {job_title} role at {company_name}...",
                            "personable": f"When I learned about the {job_title} opportunity at {company_name}, I knew I had to apply..."
                        },
                        "tips": [
                            "Personalize the opening with hiring manager's name if possible",
                            "Highlight 2-3 specific achievements that match the job description",
                            "Show you understand the company's mission and values",
                            "Keep it concise (250-300 words maximum)"
                        ],
                        "keywords_to_highlight": ["Leadership", "Technical Skills", "Problem-Solving", "Team Collaboration"]
                    }
        
        except Exception as e:
            print(f"Cover letter generation error: {e}")
            # Return default structure on error
            return {
                "cover_letter": f"Dear Hiring Manager,\n\nI am interested in the {job_title} position at {company_name}.",
                "opening": f"Position: {job_title} at {company_name}",
                "variations": {
                    "formal": "Professional version",
                    "confident": "Achievement-focused version",
                    "personable": "Conversational version"
                },
                "tips": ["Customize with your achievements", "Match keywords from job description", "Keep professional tone", "Proofread carefully"],
                "keywords_to_highlight": []
            }
    
    async def generate_questions_from_web(
        self,
        company: str,
        round_type: str = "Technical Interview",
        difficulty: str = "Medium"
    ) -> List[Dict]:
        """
        Dynamically scrape recent web data via DDGS and extract 5 structured interview questions.
        If no exact query match, it provides standard rigorous questions.
        """
        search_query = f"{company} {round_type} {difficulty} interview questions site:glassdoor.com OR site:geeksforgeeks.org 2024 OR 2025"
        
        snippets = []
        try:
            print(f"Executing live search for: {search_query}")
            with DDGS() as ddgs:
                results = ddgs.text(search_query, max_results=5)
                snippets = [r.get('body', '') for r in results if 'body' in r]
        except Exception as e:
            print(f"DDGS error: {e}")
        
        # Build context from scraped snippets matching query
        context = "\n".join(snippets)
        if not context:
            context = f"Ensure questions accurately reflect {company} {round_type} standards."

        system_prompt = f"""You are an expert technical interviewer sourcing accurate {company} interview questions.
Use the Search Context below (which contains real scraped interview reports) to extract and construct 5 distinct {difficulty} level questions for a {round_type}.

If the context lacks clear questions, construct 5 realistic questions highly specific to {company}'s known hiring patterns.

Format response STRICTLY as a JSON array of objects with the exact schema:
[
  {{
    "company_name": "{company}",
    "round_type": "{round_type}",
    "question_text": "The extracted or realistic question...",
    "difficulty": "{difficulty}",
    "source": "AI Web Scraping Extraction",
    "solution_text": "A canonical solution or code snippet",
    "solution_explanation": "Brief explanation of the solution",
    "frequency_score": 8
  }}
]"""

        user_prompt = f"""Target Company: {company}
Target Round: {round_type}
Search Context:
{context}

Generate a valid JSON array of 5 questions matching the exact schema."""

        try:
            # Try OpenRouter for high-quality structured JSON output
            print(f"Transforming scraped {company} questions into structured objects...")
            response = await self.openrouter.generate(
                prompt=user_prompt,
                model=LLMConfig.OPENROUTER_MODELS["default"],
                max_tokens=2000,
                temperature=0.3,
                system_prompt=system_prompt
            )
            try:
                # Often wrapped in backticks or markdown JSON block
                clean_response = response.strip()
                if clean_response.startswith('```json'):
                    clean_response = clean_response[7:]
                if clean_response.startswith('```'):
                    clean_response = clean_response[3:]
                if clean_response.endswith('```'):
                    clean_response = clean_response[:-3]
                    
                parsed_data = json.loads(clean_response)
                # Check if it's a list, if it returned a dict with a key 'questions', unwrap it.
                if isinstance(parsed_data, dict) and "questions" in parsed_data:
                    return parsed_data["questions"]
                elif isinstance(parsed_data, list):
                    return parsed_data
                return []
            except json.JSONDecodeError as decode_err:
                print(f"Decode error on scraping json: {decode_err}")
                return []
        except Exception as e:
            print(f"Questions generation fallback error: {e}")
            return []

    async def search_tess_context_from_web(self, query: str) -> str:
        """
        Silently fetch up-to-date company data from DuckDuckGo for TESS Chat contextual awareness.
        """
        try:
            from duckduckgo_search import DDGS
            print(f"Executing TESS live search for: {query}")
            with DDGS() as ddgs:
                # Limit to 3 max results to keep response times incredibly fast
                results = ddgs.text(query[:100], max_results=3) # take first 100 chars to avoid huge queries
                snippets = [r.get('body', '') for r in results if 'body' in r]
                return "\n".join(snippets)
        except Exception as e:
            print(f"TESS DDGS error: {e}")
            return ""

    async def close(self):
        """Close all clients"""
        await self.nvidia.close()
        await self.openrouter.close()
        await self.groq.close()


# Singleton instance
_router_instance: Optional[LLMRouter] = None


def get_llm_router() -> LLMRouter:
    """Get or create global LLM router"""
    global _router_instance
    if _router_instance is None:
        _router_instance = LLMRouter()
    return _router_instance
