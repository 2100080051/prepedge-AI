"""
TESS Chat Service - AI Conversation Engine
Uses existing free LLM providers: Groq, Nvidia, OpenRouter
Cost: $0/month
"""

import asyncio
from datetime import datetime
from typing import Optional, Dict, List
import logging

logger = logging.getLogger(__name__)


class TESSChatService:
    """
    Main TESS conversation engine
    - Routes to best available LLM (Groq → Nvidia → OpenRouter)
    - Maintains conversation context
    - Provides mentoring, interviewing, coaching modes
    """
    
    def __init__(self):
        """Initialize with LLM clients from app.llm.provider"""
        # These are imported here to avoid circular imports
        self.groq_available = False
        self.nvidia_available = False
        self.openrouter_available = False
        
        # Load LLM clients
        self._init_llm_clients()
        
        # TESS personality system prompts
        self.system_prompts = {
            "mentor": """You are TESS, an Educational Support System - an AI mentor for interview preparation.

Your role is to:
1. Explain complex interview concepts clearly and simply using detailed technical context
2. Provide real examples from actual interview questions
3. Guide learning without directly giving answers - encourage thinking
4. Be encouraging, empathetic, and patient
5. Adapt your explanation style to the student's level

CRITICAL FORMATTING RULES:
- ALWAYS structure your response beautifully using Markdown.
- Use H3 (###) headers to separate different topics or sections.
- Use bullet points (-) for lists.
- Use bold text (**text**) for key terms and concepts.
- Use code blocks (```language) for any syntax or coding questions.
- Keep paragraphs short and scannable.""",
            
            "interviewer": """You are conducting a professional mock interview.

Your role is to:
1. Ask ONE clear question at a time
2. Allow 30-60 seconds thinking time before asking follow-ups
3. Give constructive feedback on the quality of answers
4. Note areas for improvement
5. Keep a professional but warm tone

Start with: 'Ready for the interview? Let me ask you the first question.'""",
            
            "coach": """You are a career coach specializing in interview preparation.

Your role is to:
1. Analyze the candidate's strengths and areas for improvement
2. Provide targeted, actionable recommendations
3. Build confidence through encouraging feedback
4. Suggest next practice areas
5. Track progress and improvement over time

Be supportive but honest about areas needing work."""
        }
        
        logger.info("✅ TESS Chat Service initialized")
    
    def _init_llm_clients(self):
        """Initialize available LLM clients"""
        try:
            from app.llm.provider import GroqClient
            self.groq = GroqClient()
            self.groq_available = True
            logger.info("✅ Groq client ready (fastest)")
        except Exception as e:
            logger.warning(f"⚠️  Groq client unavailable: {e}")
        
        try:
            from app.llm.provider import NvidiaClient
            self.nvidia = NvidiaClient()
            self.nvidia_available = True
            logger.info("✅ Nvidia client ready (fallback)")
        except Exception as e:
            logger.warning(f"⚠️  Nvidia client unavailable: {e}")
        
        try:
            from app.llm.provider import OpenRouterClient
            self.openrouter = OpenRouterClient()
            self.openrouter_available = True
            logger.info("✅ OpenRouter client ready (secondary fallback)")
        except Exception as e:
            logger.warning(f"⚠️  OpenRouter client unavailable: {e}")
    
    async def chat(
        self,
        user_message: str,
        user_id: int,
        session_id: str,
        mode: str = "mentor",
        context: Optional[Dict] = None
    ) -> Dict:
        """
        Main chat endpoint for TESS
        
        Args:
            user_message: Student's question or response
            user_id: Database user ID
            session_id: Conversation session ID
            mode: "mentor", "interviewer", or "coach"
            context: Previous conversation context
        
        Returns:
            {
                "response": "AI response text",
                "mode": "mentor",
                "session_id": "session_123",
                "timestamp": "2026-03-30T...",
                "success": True
            }
        """
        
        start_time = datetime.now()
        
        try:
            # Validate mode
            if mode not in self.system_prompts:
                mode = "mentor"
            
            logger.info(f"📝 Processing message in '{mode}' mode (session: {session_id})")
            
            # --- DYNAMIC INTERNET SEARCH INJECTION ---
            # Automatically fetch up-to-date internet context to supplement the LLM
            from app.llm.provider import get_llm_router
            try:
                llm_router = get_llm_router()
                live_context = await llm_router.search_tess_context_from_web(user_message)
                if live_context:
                    if context is None:
                        context = {}
                    context["live_web_data"] = live_context
            except Exception as search_err:
                logger.warning(f"Live search failed: {search_err}")
                
            # Build enriched prompt
            enhanced_prompt = self._build_prompt(
                user_message=user_message,
                mode=mode,
                context=context
            )

            
            # Get LLM response (try providers in order of speed)
            response_text = await self._get_llm_response(
                prompt=enhanced_prompt,
                system_prompt=self.system_prompts[mode],
                mode=mode
            )
            
            # Calculate response time
            response_time = (datetime.now() - start_time).total_seconds()
            
            logger.info(f"✅ Response generated in {response_time:.2f}s")
            
            return {
                "response": response_text,
                "mode": mode,
                "session_id": session_id,
                "timestamp": datetime.now().isoformat(),
                "response_time_seconds": response_time,
                "success": True
            }
        
        except Exception as e:
            logger.error(f"❌ Chat error: {str(e)}")
            return {
                "response": "I encountered an issue processing your message. Please try again.",
                "mode": mode,
                "session_id": session_id,
                "timestamp": datetime.now().isoformat(),
                "success": False,
                "error": str(e)
            }
    
    async def _get_llm_response(
        self,
        prompt: str,
        system_prompt: str,
        mode: str
    ) -> str:
        """
        Get response from LLM with automatic provider fallback
        Priority: Groq (fastest) → Nvidia (free cloud) → OpenRouter
        """
        
        # Configure parameters based on mode
        if mode == "interviewer":
            max_tokens = 300
            temperature = 0.8  # More conversational
        elif mode == "coach":
            max_tokens = 400
            temperature = 0.6  # More analytical
        else:  # mentor
            max_tokens = 500
            temperature = 0.7  # Balanced
        
        # Try Groq first (fastest, 100 tokens/sec)
        if self.groq_available:
            try:
                logger.info("🚀 Trying Groq (fastest)...")
                response = await self.groq.generate(
                    prompt=prompt,
                    system_prompt=system_prompt,
                    max_tokens=max_tokens,
                    temperature=temperature
                )
                logger.info("✅ Groq response received")
                return response
            except Exception as e:
                logger.warning(f"⚠️  Groq failed: {e}, trying fallback...")
        
        # Try Nvidia (free cloud GPU)
        if self.nvidia_available:
            try:
                logger.info("☁️ Trying Nvidia NIM (free cloud)...")
                response = await self.nvidia.generate(
                    prompt=prompt,
                    system_prompt=system_prompt,
                    max_tokens=max_tokens,
                    temperature=temperature
                )
                logger.info("✅ Nvidia response received")
                return response
            except Exception as e:
                logger.warning(f"⚠️  Nvidia failed: {e}, trying fallback...")
        
        # Try OpenRouter
        if self.openrouter_available:
            try:
                logger.info("🔄 Trying OpenRouter (last resort)...")
                response = await self.openrouter.generate(
                    prompt=prompt,
                    system_prompt=system_prompt,
                    max_tokens=max_tokens,
                    temperature=temperature
                )
                logger.info("✅ OpenRouter response received")
                return response
            except Exception as e:
                logger.error(f"❌ OpenRouter failed: {e}")
        
        # All providers failed
        logger.error("❌ All LLM providers failed!")
        raise Exception("No LLM providers available")
    
    def _build_prompt(
        self,
        user_message: str,
        mode: str,
        context: Optional[Dict] = None
    ) -> str:
        """
        Build enriched prompt with context
        """
        
        prompt_parts = []
        
        # Add context if available
        if context:
            if context.get("previous_messages"):
                prompt_parts.append("Recent conversation context:")
                for msg in context["previous_messages"][-3:]:  # Last 3 messages
                    prompt_parts.append(f"- {msg}")
                prompt_parts.append("")
            
            if context.get("topic"):
                prompt_parts.append(f"Current topic: {context['topic']}")
                prompt_parts.append("")
            
            if context.get("level"):
                prompt_parts.append(f"Student level: {context['level']}")
                prompt_parts.append("")
                
            if context.get("live_web_data"):
                prompt_parts.append("--- RECENT LIVE INTERNET DATA FOR CONTEXT ---")
                prompt_parts.append(context["live_web_data"])
                prompt_parts.append("--- END LIVE DATA ---\n")
                
            if context.get("language"):
                prompt_parts.append(f"IMPORTANT: Respond completely in {context['language']} language.")
                prompt_parts.append("")
        
        # Add the user message
        if mode == "interviewer":
            prompt_parts.append(f"Student's interview answer/question: {user_message}")
            prompt_parts.append("\nProvide feedback and ask follow-up or next question.")
        else:
            prompt_parts.append(f"Student question: {user_message}")
        
        return "\n".join(prompt_parts)
    
    async def get_explanation(
        self,
        concept: str,
        depth: str = "beginner",
        examples: int = 2
    ) -> Dict:
        """
        Get detailed explanation of a concept
        
        Args:
            concept: What to explain (e.g., "Binary Search Tree")
            depth: "beginner", "intermediate", or "advanced"
            examples: Number of code examples to include
        
        Returns:
            {"explanation": "...", "examples": [...], "key_points": [...]}
        """
        
        prompt = f"""
Explain the concept: {concept}

Requirements:
- Level: {depth}
- Include {examples} practical code examples
- Key learning points at the end
- Time complexity if applicable
- Real interview context

Be clear and concise.
        """
        
        try:
            response = await self._get_llm_response(
                prompt=prompt,
                system_prompt=self.system_prompts["mentor"],
                mode="mentor"
            )
            
            return {
                "concept": concept,
                "explanation": response,
                "depth": depth,
                "success": True
            }
        
        except Exception as e:
            return {
                "concept": concept,
                "success": False,
                "error": str(e)
            }


# Singleton instance
_chat_service: Optional[TESSChatService] = None


def get_chat_service() -> TESSChatService:
    """Get or create chat service singleton"""
    global _chat_service
    if _chat_service is None:
        _chat_service = TESSChatService()
    return _chat_service
