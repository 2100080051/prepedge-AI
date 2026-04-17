"""
LearnAI Service — AI-powered concept explanation in any subject, any domain.
Powered by OpenRouter for powerful, precise concept explanations.
"""

from typing import Optional, Dict
import asyncio
from app.llm.provider import get_llm_router


# ─── Domain & Subject Catalog ────────────────────────────────────────────────
DOMAIN_CATALOG = {
    "Engineering & Computer Science": {
        "icon": "💻",
        "subjects": [
            "Data Structures & Algorithms",
            "Operating Systems",
            "Database Management (DBMS)",
            "Computer Networks",
            "Python Programming",
            "Java Programming",
            "Object-Oriented Programming",
            "System Design",
            "Machine Learning",
            "Web Development",
        ]
    },
    "Mathematics": {
        "icon": "📐",
        "subjects": [
            "Algebra",
            "Calculus",
            "Statistics & Probability",
            "Discrete Mathematics",
            "Linear Algebra",
            "Number Theory",
        ]
    },
    "Business & Management": {
        "icon": "📊",
        "subjects": [
            "Marketing Management",
            "Financial Accounting",
            "Human Resource Management",
            "Business Strategy",
            "Operations Management",
            "Entrepreneurship",
        ]
    },
    "Science": {
        "icon": "🔬",
        "subjects": [
            "Physics",
            "Chemistry",
            "Biology",
            "Environmental Science",
        ]
    },
    "Law": {
        "icon": "⚖️",
        "subjects": [
            "Constitutional Law",
            "Criminal Law",
            "Corporate Law",
            "Contract Law",
            "Intellectual Property",
        ]
    },
    "Medicine & Health": {
        "icon": "🏥",
        "subjects": [
            "Anatomy",
            "Pharmacology",
            "Pathology",
            "Physiology",
            "Medical Ethics",
        ]
    },
    "Arts & Humanities": {
        "icon": "🎨",
        "subjects": [
            "History",
            "Economics",
            "Psychology",
            "Political Science",
            "Sociology",
        ]
    },
}


class LearnAIService:
    """Service for AI-powered concept learning (Future implementation)"""

    @staticmethod
    def get_domains() -> list:
        """Return all available domains with subjects"""
        result = []
        for domain, info in DOMAIN_CATALOG.items():
            result.append({
                "domain": domain,
                "subjects": info["subjects"],
                "icon": info["icon"]
            })
        return result

    @staticmethod
    async def explain_concept(domain: str, subject: str, concept: str, language: str = "English") -> dict:
        """Generate a powerful lesson on the given concept using OpenRouter"""
        try:
            # Get the LLM router instance
            llm_router = get_llm_router()
            
            # Generate concept explanation using OpenRouter (Mistral 7B + Llama 70B)
            explanation_data = await llm_router.generate_learnai_concept(
                domain=domain,
                subject=subject,
                concept=concept,
                language=language
            )
            
            # Ensure all required fields are present
            result = {
                "domain": domain,
                "subject": subject,
                "concept": concept,
                "language": language,
                "explanation": explanation_data.get("explanation", ""),
                "analogy": explanation_data.get("analogy", ""),
                "example": explanation_data.get("example", ""),
                "key_points": explanation_data.get("key_points", []),
                "common_mistakes": explanation_data.get("common_mistakes", []),
                "interview_tips": explanation_data.get("interview_tips", ""),
                "image_prompt": f"Clean educational diagram explaining {concept} in {subject}. Visual breakdown with labeled parts showing how {concept} works. Professional textbook quality illustration."
            }
            
            return result
            
        except Exception as e:
            print(f"Error generating concept explanation: {e}")
            # Fallback to basic explanation
            return {
                "domain": domain,
                "subject": subject,
                "concept": concept,
                "language": language,
                "explanation": f"Unable to generate full explanation. {concept} is a key concept in {subject}.",
                "analogy": "Check the full explanation above",
                "example": "Check the full explanation above",
                "key_points": [f"{concept} is important in {subject}"],
                "common_mistakes": ["Not enough practice"],
                "interview_tips": "Prepare examples related to this concept",
                "image_prompt": f"Clean educational diagram explaining {concept} in {subject}. Visual breakdown with labeled parts showing how {concept} works. Professional textbook quality illustration."
            }

    @staticmethod
    def generate_concept_image(concept: str, subject: str) -> Optional[str]:
        """Generate an educational diagram (Future implementation)"""
        # TODO: Integration with image generation APIs in Week 4+
        return None
