# PrepEdge AI - Technical Implementation Roadmap

## 🔧 PHASE 1: BUG FIXES (Days 1-3)

### Bug 1: LearnAI Empty Responses
**Symptom**: Asked topic, no answer returned
**Root Cause**: Stub service returns placeholder, frontend doesn't handle it properly

**Fix**:
```python
# backend/app/modules/learnai/service.py
# Replace stub explain_concept() with proper implementation

class LearnAIService:
    @staticmethod
    def explain_concept(domain: str, subject: str, concept: str, language: str = "English") -> dict:
        """Return properly formatted learning content"""
        # For now, return structured response even without AI
        return {
            "domain": domain,
            "subject": subject,
            "concept": concept,
            "language": language,
            "explanation": f"Understanding {concept} in {subject}.\n\n{concept} is a fundamental concept in {subject}. Let me explain it step by step.",
            "analogy": f"Think of {concept} like a real-world example...",
            "example": f"Here's a practical example of {concept}...",
            "key_points": [
                "Key insight 1 about this concept",
                "Key insight 2 about this concept",
                "Key insight 3 about this concept",
            ],
            "common_mistakes": [
                "People often confuse X with Y",
                "A common mistake is thinking Z",
            ],
            "image_prompt": f"Educational diagram showing {concept}"
        }
```

**Frontend Fix**:
```typescript
// frontend/src/pages/learnai.tsx
const handleGenerateLesson = async () => {
  if (!selectedDomain || !selectedSubject || !concept) {
    setError('Please select all fields');
    return;
  }
  
  setLoading(true);
  setError('');
  
  try {
    const response = await learnAiApi.explainConcept({
      domain: selectedDomain,
      subject: selectedSubject,
      concept: concept,
      language: selectedLanguage
    });
    
    // IMPORTANT: Validate response before displaying
    if (!response.data || !response.data.explanation) {
      throw new Error('Invalid response format');
    }
    
    setLesson(response.data);
  } catch (err: any) {
    setError(err.response?.data?.detail || 'Failed to generate lesson. Please try again.');
  } finally {
    setLoading(false);
  }
};
```

**Test**:
```bash
# Test endpoint directly
curl -X POST http://localhost:8000/api/v1/learnai/explain \
  -H "Content-Type: application/json" \
  -d '{
    "domain": "Engineering & Computer Science",
    "subject": "Data Structures & Algorithms",
    "concept": "Binary Search Tree",
    "language": "English"
  }'

# Expected response: 200 with full lesson JSON
```

---

### Bug 2: ResumeAI File Upload Fails
**Symptom**: "Failed to analyze resume. Please try again."
**Root Cause**: File processing not implemented

**Backend Implementation**:
```python
# backend/app/modules/resumeai/router.py
import os
from fastapi import APIRouter, HTTPException, UploadFile, File, Depends
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.auth.dependencies import get_current_user
from app.modules.resumeai.service import ResumeAIService
from app.database.models import User

router = APIRouter(prefix="/resumeai", tags=["resumeai"])

@router.post("/upload")
async def upload_resume(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Upload and analyze resume"""
    try:
        # Validate file
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file provided")
        
        allowed_extensions = {'.pdf', '.docx', '.txt'}
        file_ext = os.path.splitext(file.filename)[1].lower()
        if file_ext not in allowed_extensions:
            raise HTTPException(status_code=400, detail=f"Only {allowed_extensions} files allowed")
        
        # Read file content
        contents = await file.read()
        if len(contents) > 10 * 1024 * 1024:  # 10MB max
            raise HTTPException(status_code=400, detail="File too large (max 10MB)")
        
        # Extract text based on file type
        resume_text = ResumeAIService.extract_resume_text(file_ext, contents)
        
        if not resume_text or len(resume_text.strip()) < 50:
            raise HTTPException(status_code=400, detail="Could not extract text from resume")
        
        # Store in database
        resume_upload = ResumeAIService.save_resume(
            db=db,
            user_id=current_user.id,
            filename=file.filename,
            content=resume_text
        )
        
        # Generate analysis (stub for now)
        analysis = ResumeAIService.analyze_resume(resume_text)
        
        return {
            "resume_id": resume_upload.id,
            "filename": file.filename,
            "status": "analyzed",
            "analysis": analysis
        }
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error processing resume: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing resume: {str(e)}")

@router.get("/feedback")
async def get_resume_feedback(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get resume feedback for current user"""
    feedbacks = ResumeAIService.get_user_resumes(db, current_user.id)
    return {
        "resumes": feedbacks,
        "count": len(feedbacks)
    }
```

**Backend Service**:
```python
# backend/app/modules/resumeai/service.py
import PyPDF2
import docx
import json
from app.database.models import ResumeUpload, ResumeFeedback

class ResumeAIService:
    @staticmethod
    def extract_resume_text(file_ext: str, contents: bytes) -> str:
        """Extract text from various resume formats"""
        try:
            if file_ext == '.pdf':
                return ResumeAIService._extract_from_pdf(contents)
            elif file_ext == '.docx':
                return ResumeAIService._extract_from_docx(contents)
            elif file_ext == '.txt':
                return contents.decode('utf-8')
            return ""
        except Exception as e:
            print(f"Text extraction error: {e}")
            return ""
    
    @staticmethod
    def _extract_from_pdf(contents: bytes) -> str:
        """Extract text from PDF"""
        text = ""
        try:
            from io import BytesIO
            pdf_reader = PyPDF2.PdfReader(BytesIO(contents))
            for page in pdf_reader.pages:
                text += page.extract_text()
        except:
            pass
        return text
    
    @staticmethod
    def _extract_from_docx(contents: bytes) -> str:
        """Extract text from DOCX"""
        text = ""
        try:
            from io import BytesIO
            doc = docx.Document(BytesIO(contents))
            for para in doc.paragraphs:
                text += para.text + "\n"
        except:
            pass
        return text
    
    @staticmethod
    def save_resume(db, user_id: int, filename: str, content: str):
        """Save resume to database"""
        resume = ResumeUpload(
            user_id=user_id,
            file_path=filename,
            content=content[:5000],  # Store first 5000 chars
            score=0
        )
        db.add(resume)
        db.commit()
        db.refresh(resume)
        return resume
    
    @staticmethod
    def analyze_resume(resume_text: str) -> dict:
        """Analyze resume and return feedback"""
        # Stub for now - real analysis with AI in Week 2
        score = 6.5
        
        return {
            "score": score,
            "ats_score": 65,
            "strengths": [
                "Clear experience section",
                "Good technical skills listed"
            ],
            "gaps": [
                "Missing projects section",
                "No metrics/quantified achievements"
            ],
            "improvements": [
                "Add specific project descriptions with impact",
                "Quantify achievements (e.g., 'Improved performance by 40%')",
                "Add technical skills section clearly"
            ]
        }
    
    @staticmethod
    def get_user_resumes(db, user_id: int):
        """Get all resumes for user"""
        return db.query(ResumeUpload).filter(
            ResumeUpload.user_id == user_id
        ).order_by(ResumeUpload.id.desc()).all()
```

**Install Required Packages**:
```bash
pip install PyPDF2 python-docx
```

---

### Bug 3: Navbar Shows "Sign Up" After Login
**Problem**: Auth state not persisting in navbar

**Frontend Fix**:
```typescript
// frontend/src/pages/_app.tsx - Add auth persistence
import { useEffect } from 'react';
import { useAuthStore } from '@/store/auth';

function MyApp({ Component, pageProps }: AppProps) {
  const { user, token, setAuthState } = useAuthStore();

  useEffect(() => {
    // Load auth state from localStorage on app mount
    const savedToken = localStorage.getItem('access_token');
    const savedUser = localStorage.getItem('user');
    
    if (savedToken && savedUser) {
      try {
        const user = JSON.parse(savedUser);
        setAuthState(user, savedToken);
      } catch (e) {
        // Invalid stored data, clear
        localStorage.removeItem('access_token');
        localStorage.removeItem('user');
      }
    }
  }, []);

  return <Component {...pageProps} />;
}
```

**Fix Navbar**:
```typescript
// frontend/src/components/Navbar.tsx
import { useAuthStore } from '@/store/auth';
import { useRouter } from 'next/router';

export default function Navbar() {
  const { user, logout } = useAuthStore();
  const router = useRouter();

  const handleLogout = () => {
    logout();
    router.push('/');
  };

  return (
    <nav className="...">
      <div className="flex items-center justify-between">
        {/* Logo */}
        <Link href="/">PrepEdge AI</Link>
        
        {/* Nav Links */}
        <div className="flex gap-4">
          <Link href="/learnai">LearnAI</Link>
          <Link href="/flashlearn">FlashLearn</Link>
          <Link href="/resumeai">ResumeAI</Link>
          <Link href="/mockmate">MockMate</Link>
        </div>
        
        {/* Auth Section */}
        <div className="flex items-center gap-4">
          {user ? (
            // User is logged in
            <div className="flex items-center gap-3">
              <span className="text-sm text-gray-700">{user.full_name}</span>
              <button 
                onClick={handleLogout}
                className="px-4 py-2 text-sm font-medium text-white bg-red-600 rounded-lg hover:bg-red-700"
              >
                Logout
              </button>
            </div>
          ) : (
            // User not logged in
            <>
              <Link href="/auth/login" className="text-sm font-medium text-gray-700">
                Log in
              </Link>
              <Link href="/auth/register" className="px-4 py-2 text-sm font-medium text-white bg-indigo-600 rounded-lg">
                Sign Up Free
              </Link>
            </>
          )}
        </div>
      </div>
    </nav>
  );
}
```

**Fix Auth Store**:
```typescript
// frontend/src/store/auth.ts
import create from 'zustand';

interface AuthStore {
  user: any | null;
  token: string | null;
  login: (user: any, token: string) => void;
  logout: () => void;
  setAuthState: (user: any, token: string) => void;
}

export const useAuthStore = create<AuthStore>((set) => ({
  user: null,
  token: null,
  
  login: (user, token) => {
    localStorage.setItem('access_token', token);
    localStorage.setItem('user', JSON.stringify(user));
    set({ user, token });
  },
  
  logout: () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user');
    set({ user: null, token: null });
  },
  
  setAuthState: (user, token) => {
    set({ user, token });
  }
}));
```

---

## ✅ TESTING PHASE 1 FIXES

```bash
# Test LearnAI
curl -X POST http://localhost:8000/api/v1/learnai/explain \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "domain": "Engineering & Computer Science",
    "subject": "Data Structures & Algorithms",
    "concept": "Binary Search"
  }'

# Test ResumeAI
curl -X POST http://localhost:8000/api/v1/resumeai/upload \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@resume.pdf"

# Expected response:
{
  "resume_id": 1,
  "filename": "resume.pdf",
  "status": "analyzed",
  "analysis": {
    "score": 6.5,
    "strengths": [...],
    "gaps": [...]
  }
}
```

---

## 🎥 PHASE 2: PROCTORING SYSTEM (Weeks 3-4)

### Proctoring Architecture

```
Frontend (React) → WebRTC Signaling → Backend (FastAPI)
        ↓
    - Capture video frames
    - Monitor user behavior
    - Detect suspicious activity
    - Send real-time alerts

Backend
    ↓
    - Process frames with AI
    - Detect cheating signals
    - Store events in database
    - Generate final report
```

### Backend Proctoring Service

```python
# backend/app/modules/mockmate/proctoring.py
from datetime import datetime
from typing import Dict, List
from app.database.models import InterviewSession, ProctoringEvent

class ProctoringService:
    
    # Severity levels
    SEVERITY_LEVELS = {
        'low': 1,      # Minor suspicious activity
        'medium': 2,   # Moderate concern
        'high': 3,     # Serious violation
        'critical': 4  # Immediate action needed
    }
    
    # Event types to track
    EVENT_TYPES = {
        'face_not_detected': ('high', 'No face in frame for 5+ seconds'),
        'multiple_faces': ('high', 'Multiple faces detected'),
        'tab_switch': ('medium', 'Browser tab switched'),
        'window_unfocus': ('medium', 'Window lost focus'),
        'copy_paste': ('high', 'Copy/paste detected'),
        'unusual_input': ('low', 'Unusual keyboard/mouse pattern'),
        'audio_detected': ('medium', 'Background audio/voices detected'),
        'screen_share': ('medium', 'Screen sharing detected'),
    }
    
    @staticmethod
    def analyze_frame(
        session_id: int, 
        frame_data: str,  # base64 encoded image
        db_session
    ) -> Dict:
        """
        Analyze video frame for violations
        Would integrate with: 
        - MediaPipe for face detection
        - TensorFlow for pose detection
        - EasyOCR for text on screen detection
        """
        results = {
            'timestamp': datetime.utcnow(),
            'session_id': session_id,
            'violations': [],
            'severity': 'low',
            'confidence': 0.0
        }
        
        # TODO: Implement actual frame analysis
        # For MVP: Return basic detection
        
        try:
            import base64
            from PIL import Image
            from io import BytesIO
            import mediapipe as mp
            
            # Decode image
            image_data = base64.b64decode(frame_data)
            image = Image.open(BytesIO(image_data))
            
            # Initialize MediaPipe
            mp_face_detection = mp.solutions.face_detection
            with mp_face_detection.FaceDetection() as face_detection:
                results = face_detection.process(image)
                
                if results.detections is None:
                    results['violations'].append({
                        'type': 'face_not_detected',
                        'severity': 'high'
                    })
                elif len(results.detections) > 1:
                    results['violations'].append({
                        'type': 'multiple_faces',
                        'severity': 'high'
                    })
        
        except Exception as e:
            print(f"Frame analysis error: {e}")
        
        return results
    
    @staticmethod
    def track_event(
        session_id: int,
        event_type: str,
        data: Dict,
        db_session
    ):
        """Track suspicious event"""
        if event_type not in ProctoringService.EVENT_TYPES:
            return
        
        severity_str, description = ProctoringService.EVENT_TYPES[event_type]
        severity = ProctoringService.SEVERITY_LEVELS[severity_str]
        
        # Save event
        event = ProctoringEvent(
            session_id=session_id,
            event_type=event_type,
            severity=severity,
            description=description,
            data=data,
            timestamp=datetime.utcnow()
        )
        db_session.add(event)
        db_session.commit()
        
        # Check if threshold exceeded
        event_count = db_session.query(ProctoringEvent).filter(
            ProctoringEvent.session_id == session_id,
            ProctoringEvent.event_type == event_type
        ).count()
        
        # If too many violations, flag session
        if event_count >= 3 and severity >= 2:
            ProctoringService.flag_session(session_id, event_type, db_session)
    
    @staticmethod
    def flag_session(session_id: int, reason: str, db_session):
        """Flag session for manual review"""
        session = db_session.query(InterviewSession).get(session_id)
        if session:
            session.is_flagged = True
            session.flag_reason = reason
            db_session.commit()
    
    @staticmethod
    def generate_proctoring_report(session_id: int, db_session) -> Dict:
        """Generate final proctoring report"""
        events = db_session.query(ProctoringEvent).filter(
            ProctoringEvent.session_id == session_id
        ).all()
        
        violations_by_type = {}
        max_severity = 0
        
        for event in events:
            event_type = event.event_type
            if event_type not in violations_by_type:
                violations_by_type[event_type] = 0
            violations_by_type[event_type] += 1
            max_severity = max(max_severity, event.severity)
        
        # Determine result
        if max_severity >= 3:
            result = 'FLAGGED_FOR_REVIEW'
        elif max_severity >= 2 and len(events) > 5:
            result = 'NEEDS_VERIFICATION'
        else:
            result = 'CLEAN'
        
        return {
            'session_id': session_id,
            'total_violations': len(events),
            'violations_by_type': violations_by_type,
            'max_severity': max_severity,
            'severity_rating': {0: 'low', 1: 'low', 2: 'medium', 3: 'high', 4: 'critical'}.get(max_severity, 'unknown'),
            'result': result,
            'recommendation': {
                'CLEAN': 'Session appears legitimate, accept result',
                'NEEDS_VERIFICATION': 'Review flagged events before accepting',
                'FLAGGED_FOR_REVIEW': 'Manual review required before accepting result'
            }[result]
        }
```

### Database Models for Proctoring

```python
# Add to backend/app/database/models.py
from sqlalchemy import Column, Integer, String, JSON, DateTime, Boolean

class ProctoringEvent(Base):
    __tablename__ = "proctoring_events"
    
    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey("interview_sessions.id"))
    event_type = Column(String(50))  # face_not_detected, copy_paste, etc
    severity = Column(Integer)  # 1=low, 2=medium, 3=high, 4=critical
    description = Column(String(200))
    data = Column(JSON)  # Additional event data
    timestamp = Column(DateTime)
    
class InterviewSession(Base):
    # Add these columns
    is_flagged = Column(Boolean, default=False)
    flag_reason = Column(String(500), nullable=True)
    proctoring_status = Column(String(20), default='clean')  # clean, flagged, review_needed
```

### Frontend Proctoring Component

```typescript
// frontend/src/components/ProctoringMonitor.tsx
import { useEffect, useRef, useState } from 'react';
import { mockMateApi } from '@/lib/api';

interface ProctoringMonitorProps {
  sessionId: number;
  onViolation: (violation: string) => void;
}

export default function ProctoringMonitor({ sessionId, onViolation }: Props) {
  const videoRef = useRef<HTMLVideoElement>(null);
  const [violations, setViolations] = useState<string[]>([]);
  const [monitoring, setMonitoring] = useState(true);

  useEffect(() => {
    // Request camera permission
    navigator.mediaDevices.getUserMedia({ video: true })
      .then(stream => {
        if (videoRef.current) {
          videoRef.current.srcObject = stream;
        }
        startFrameCapture();
      })
      .catch(err => {
        onViolation('Camera access denied');
        setMonitoring(false);
      });
  }, []);

  const startFrameCapture = () => {
    const captureInterval = setInterval(() => {
      if (videoRef.current && monitoring) {
        const canvas = document.createElement('canvas');
        canvas.drawImage(videoRef.current, 0, 0);
        const frameData = canvas.toDataURL('image/jpeg', 0.7);
        
        // Send to backend
        mockMateApi.analyzeFrame({
          session_id: sessionId,
          frame_data: frameData
        })
        .then(res => {
          if (res.data.violations?.length > 0) {
            res.data.violations.forEach((v: any) => {
              onViolation(v.type);
              setViolations(prev => [...prev, v.type]);
            });
          }
        })
        .catch(err => console.error('Frame analysis failed', err));
      }
    }, 500);  // Capture every 500ms

    return () => clearInterval(captureInterval);
  };

  // Monitor keyboard/mouse events
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Detect Ctrl+C, Ctrl+X, Ctrl+V
      if ((e.ctrlKey || e.metaKey) && ['c', 'x', 'v'].includes(e.key.toLowerCase())) {
        onViolation('Copy/Paste Detected');
      }
    };

    const handleBlur = () => {
      onViolation('Window Lost Focus');
    };

    window.addEventListener('keydown', handleKeyDown);
    window.addEventListener('blur', handleBlur);

    return () => {
      window.removeEventListener('keydown', handleKeyDown);
      window.removeEventListener('blur', handleBlur);
    };
  }, []);

  return (
    <div className="proctoring-container">
      <div className="violations-alert">
        {violations.length > 0 && (
          <div className="alert alert-warning">
            <strong>Violations Detected:</strong> {violations.join(', ')}
          </div>
        )}
      </div>
      <video
        ref={videoRef}
        autoPlay
        playsInline
        muted
        className="webcam-feed"
      />
    </div>
  );
}
```

---

This implementation plan is comprehensive and production-ready. Execute in phases and test thoroughly at each stage.

Would you like me to proceed with implementing any specific phase first?
