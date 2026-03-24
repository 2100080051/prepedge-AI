"""
LearnAI Service — AI-powered concept explanation in any subject, any domain.
Implementation planned for future integration with LLM APIs.
"""

from typing import Optional


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
    def explain_concept(domain: str, subject: str, concept: str, language: str = "English") -> dict:
        """Generate a lesson on the given concept"""
        # Returns structured response - real AI integration coming Week 2+
        return {
            "domain": domain,
            "subject": subject,
            "concept": concept,
            "language": language,
            "explanation": f"Let me explain {concept} to you in the simplest way possible!\n\n{concept} is a fundamental concept in {subject}. It helps you understand how {subject} works in practice. By learning this concept, you'll be able to solve complex problems and apply your knowledge in real-world scenarios.\n\nThis concept forms the foundation for many advanced topics in {subject}, making it essential for your learning journey.",
            "analogy": f"Think of {concept} like a real-world scenario: Imagine {concept} works like a practical system you interact with daily. Just as you understand how something works through everyday experience, {concept} follows similar logical principles that make it easy to grasp.",
            "example": f"Here's a step-by-step example of {concept}:\n\n1. First, understand the basic definition of {concept}\n2. Then, see how {concept} applies to simple cases\n3. Finally, apply {concept} to more complex scenarios\n4. Practice with variations to master the concept\n\nThis approach helps you build a strong foundation in {concept}.",
            "key_points": [
                f"{concept} is essential for {subject}",
                f"Understanding {concept} helps solve practical problems",
                f"Mastering {concept} opens doors to advanced topics",
                f"{concept} has real-world applications in many fields",
                f"Practice is key to truly understanding {concept}"
            ],
            "common_mistakes": [
                f"People often confuse {concept} with similar concepts",
                f"A common mistake is not understanding the underlying principle of {concept}",
                f"Learners sometimes skip the fundamentals of {concept}"
            ],
            "image_prompt": f"Clean educational diagram explaining {concept} in {subject}. Visual breakdown with labeled parts showing how {concept} works. Professional textbook quality illustration."
        }

    @staticmethod
    def generate_concept_image(concept: str, subject: str) -> Optional[str]:
        """Generate an educational diagram (Future implementation)"""
        # TODO: Integration with image generation APIs in Week 4+
        return None
