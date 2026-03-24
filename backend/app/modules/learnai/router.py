from fastapi import APIRouter, HTTPException, UploadFile, File
from app.modules.learnai.schemas import ConceptExplainRequest
from app.modules.learnai.service import LearnAIService
from app.config import settings
import io

router = APIRouter(prefix="/learnai", tags=["learnai"])

@router.get("/domains")
def get_domains():
    """Get all available learning domains and their subjects"""
    return LearnAIService.get_domains()

@router.get("/languages")
def get_languages():
    """Get all supported explanation languages"""
    return [
        {"code": "English",   "label": "English",             "flag": "🇬🇧"},
        {"code": "Telugu",    "label": "తెలుగు (Telugu)",     "flag": "🇮🇳"},
        {"code": "Hindi",     "label": "हिंदी (Hindi)",        "flag": "🇮🇳"},
        {"code": "Tamil",     "label": "தமிழ் (Tamil)",       "flag": "🇮🇳"},
        {"code": "Kannada",   "label": "ಕನ್ನಡ (Kannada)",    "flag": "🇮🇳"},
        {"code": "Malayalam", "label": "മലയാളം (Malayalam)", "flag": "🇮🇳"},
    ]

@router.post("/explain")
def explain_concept(req: ConceptExplainRequest):
    """
    Generate a full AI lesson for a given concept.
    - Domain → Subject → Concept
    - Language: English / Telugu / Hindi / Tamil / Kannada / Malayalam
    - Returns structured explanation with analogy, example, key points, mistakes
    """
    if not req.concept.strip():
        raise HTTPException(status_code=400, detail="Concept cannot be empty")
    if len(req.concept) > 200:
        raise HTTPException(status_code=400, detail="Concept too long (max 200 chars)")

    result = LearnAIService.explain_concept(
        domain=req.domain,
        subject=req.subject,
        concept=req.concept,
        language=req.language
    )
    return result

@router.post("/visualize")
def visualize_concept(req: ConceptExplainRequest):
    """Generate an AI image diagram for the given concept using Nvidia Sana"""
    image_b64 = LearnAIService.generate_concept_image(
        concept=req.concept,
        subject=req.subject
    )
    if not image_b64:
        raise HTTPException(
            status_code=503,
            detail="Image generation is temporarily unavailable. The text explanation still works!"
        )
    return {"image_base64": image_b64, "concept": req.concept}

@router.post("/explain-and-visualize")
def explain_and_visualize(req: ConceptExplainRequest):
    """
    Combined endpoint: explain concept + generate image in one call.
    Image generation is async-friendly — included when available, omitted otherwise.
    """
    if not req.concept.strip():
        raise HTTPException(status_code=400, detail="Concept cannot be empty")

    # Get AI explanation
    explanation = LearnAIService.explain_concept(
        domain=req.domain,
        subject=req.subject,
        concept=req.concept,
        language=req.language
    )
    # Try to get image (non-blocking — returns None if fails)
    image_b64 = LearnAIService.generate_concept_image(
        concept=req.concept,
        subject=req.subject
    )
    explanation["image_base64"] = image_b64
    return explanation


@router.post("/summarize-pdf")
async def summarize_pdf(file: UploadFile = File(...)):
    """
    Upload a PDF study material and get AI-generated structured exam notes.
    Returns: key_topics, chapter_summaries, exam_tips, quick_revision_points
    """
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported. Please upload a .pdf file.")

    try:
        import PyPDF2
    except ImportError:
        raise HTTPException(status_code=500, detail="PDF processing library not installed. Run: pip install PyPDF2")

    try:
        contents = await file.read()
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(contents))

        # Extract text from all pages (limit 30 pages to keep prompt manageable)
        text_parts = []
        max_pages = min(len(pdf_reader.pages), 30)
        for i in range(max_pages):
            page_text = pdf_reader.pages[i].extract_text()
            if page_text:
                text_parts.append(page_text.strip())

        full_text = "\n\n---PAGE BREAK---\n\n".join(text_parts)

        if not full_text.strip():
            raise HTTPException(status_code=422, detail="Could not extract text from this PDF. It may be a scanned image. Try a text-based PDF.")

        # Trim to 8000 chars to stay within token limits
        truncated_text = full_text[:8000]
        if len(full_text) > 8000:
            truncated_text += "\n\n[Note: Document was truncated for processing. Showing first 8000 characters.]"

        prompt = f"""You are an expert academic summarizer helping a student prepare for exams.

The following is extracted text from a PDF study material:

{truncated_text}

Generate a comprehensive, structured exam summary. Return ONLY valid JSON:
{{
  "title": "Inferred title or subject of this document",
  "total_pages_processed": {max_pages},
  "key_topics": ["List of 5-10 main topics covered in this document"],
  "chapter_summaries": [
    {{
      "chapter": "Chapter/Section name or number",
      "summary": "2-3 sentence summary of key points in this section"
    }}
  ],
  "important_definitions": [
    {{"term": "Technical term", "definition": "Clear definition in simple English"}}
  ],
  "exam_tips": ["5-7 things the student MUST know for exams from this material"],
  "quick_revision_points": ["10-15 single-line quick revision bullet points for last-minute study"],
  "formula_or_concepts": ["Any formulas, algorithms, or core concepts to memorize verbatim"]
}}"""

        client = get_nvidia_client()
        resp = client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "You are an expert exam tutor. Return only valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=2048
        )
        raw = resp.choices[0].message.content.strip()
        if raw.startswith("```"):
            raw = raw.split("```", 2)[1]
            if raw.startswith("json"):
                raw = raw[4:]
            raw = raw.rsplit("```", 1)[0]

        import json
        result = json.loads(raw.strip())
        result["filename"] = file.filename
        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to summarize PDF: {str(e)[:200]}")
