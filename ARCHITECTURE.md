# PrepEdge AI - Architecture Overview

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Web Browser                              │
│                    (http://localhost:3000)                       │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ HTTP/REST
                             │
┌────────────────────────────┴────────────────────────────────────┐
│                       Frontend Layer                             │
│                    (Next.js + React 18)                         │
├─────────────────────────────────────────────────────────────────┤
│ ┌─────────────┐  ┌──────────────┐  ┌───────────────────────┐   │
│ │  Pages      │  │  Components  │  │  State Management     │   │
│ ├─────────────┤  ├──────────────┤  ├───────────────────────┤   │
│ │ - index     │  │ - Auth UI    │  │  Zustand Store        │   │
│ │ - login     │  │ - Navbar     │  │  - Auth state         │   │
│ │ - register  │  │ - Forms      │  │  - User data          │   │
│ │ - dashboard │  │ - Cards      │  │  - UI state           │   │
│ │ - flashlearn│  │ - Layout     │  │                       │   │
│ │ - resumeai  │  │              │  │                       │   │
│ │ - mockmate  │  │              │  │                       │   │
│ └─────────────┘  └──────────────┘  └───────────────────────┘   │
│                           │                                     │
│                    API Client (Axios)                           │
│                    + Auth Interceptor                           │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ HTTP/REST
                             │ (http://localhost:8000/api/v1)
┌────────────────────────────┴────────────────────────────────────┐
│                        Backend Layer                            │
│                    (FastAPI + Python 3.10)                      │
├─────────────────────────────────────────────────────────────────┤
│ ┌────────────────────────────────────────────────────────────┐  │
│ │                    FastAPI Application                     │  │
│ │  - CORS Middleware                                         │  │
│ │  - Request/Response Logging                                │  │
│ │  - Error Handling                                          │  │
│ └────────────────────────────────────────────────────────────┘  │
│                                                                 │
│ ┌─────────────────────────────────────────────────────────┐    │
│ │                API Routes Layer                         │    │
│ ├─────────────────────────────────────────────────────────┤    │
│ │ ┌──────────────┐ ┌──────────────┐ ┌────────────────┐   │    │
│ │ │ auth/        │ │ flashlearn/   │ │ resumeai/      │   │    │
│ │ ├──────────────┤ ├──────────────┤ ├────────────────┤   │    │
│ │ │ - register   │ │ - GET cards  │ │ - upload (WIP) │   │    │
│ │ │ - login      │ │ - GET random │ │ - feedback (WIP)   │    │
│ │ │ - get_me     │ │ - GET topics │ │                    │    │
│ │ │              │ │ - GET co's   │ │  mockmate/         │    │
│ │ │              │ │ - POST seed  │ │ ├────────────────┤ │    │
│ │ │              │ │              │ │ │ - start (WIP)  │ │    │
│ │ └──────────────┘ └──────────────┘ │ - answer (WIP) │ │    │
│ │                                    │                │ │    │
│ │                                    └────────────────┘ │    │
│ └─────────────────────────────────────────────────────────┘    │
│                           │                                    │
│                           │ Dependencies Injection              │
│                           │ (Auth, Database)                   │
│                           ▼                                    │
│ ┌─────────────────────────────────────────────────────────┐    │
│ │              Business Logic Layer                       │    │
│ ├─────────────────────────────────────────────────────────┤    │
│ │ ┌──────────────┐ ┌──────────────┐ ┌────────────────┐   │    │
│ │ │ AuthService  │ │ FlashLService│ │ ResumeAIServ.  │   │    │
│ │ │              │ │              │ │                │   │    │
│ │ │ - hash pwd   │ │ - get cards  │ │ (Coming)       │   │    │
│ │ │ - verify pwd │ │ - random sel │ │                │   │    │
│ │ │ - gen tokens │ │ - filter     │ │ MockMate Serv. │   │    │
│ │ └──────────────┘ └──────────────┘ └────────────────┘   │    │
│ │                                         - gen qs      │    │
│ │                                         - score       │    │
│ └─────────────────────────────────────────────────────────┘    │
│                           │                                    │
│                           │ ORM (SQLAlchemy)                   │
│                           │                                    │
│ ┌─────────────────────────────────────────────────────────┐    │
│ │              Database Layer                            │    │
│ ├─────────────────────────────────────────────────────────┤    │
│ │                  Pydantic Schemas                       │    │
│ │          SQLAlchemy Models & Session                   │    │
│ └─────────────────────────────────────────────────────────┘    │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ SQL
                             │
┌────────────────────────────┴────────────────────────────────────┐
│                     Data Layer                                  │
├─────────────────────────────────────────────────────────────────┤
│ ┌────────────────────────────────────────────────────────────┐  │
│ │              SQLite Database                              │  │
│ │          (backend/prepedge.db)                            │  │
│ ├────────────────────────────────────────────────────────────┤  │
│ │ Tables:                                                  │  │
│ │  - users (email, username, hashed_pwd, subscription)     │  │
│ │  - flashcards (question, answer, topic, difficulty)      │  │
│ │  - study_sessions (user_id, topic, performance)          │  │
│ │  - interview_sessions (user_id, company, role, score)    │  │
│ │  - interview_messages (session_id, role, content)        │  │
│ │  - resume_uploads (user_id, file_path, score)            │  │
│ │  - resume_feedback (resume_id, feedback, improvements)   │  │
│ │  - payments (user_id, amount, status)                    │  │
│ └────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘

                           │
                   (Future Integration)
                           │
            ┌──────────────┬────────────────┐
            │              │                │
        OpenAI         Chroma Vector    Razorpay
        (Week 2-3)   Database          (Week 4)
                      (Week 3)
```

## Module Architecture

### Week 1: FlashLearn ✅ Complete
```
User (Frontend)
    │
    ├─ /flashcards         [GET] → List all cards
    ├─ /flashcards/random  [GET] → Random study session
    ├─ /topics             [GET] → Available topics
    ├─ /companies          [GET] → Available companies
    └─ /seed               [POST] → Populate DB
    
Service Layer
    └─ FlashLearnService.get_flashcards()
       FlashLearnService.get_random_flashcards()
       FlashLearnService.get_topics()
       FlashLearnService.get_companies()
       FlashLearnService.seed_flashcards()

Data Layer
    └─ Flashcard Model
       - question (str)
       - answer (str)
       - topic (str)
       - company (str)
       - difficulty (easy/medium/hard)
```

### Week 2: ResumeAI (Stub Ready)
```
User (Frontend)
    │
    ├─ /upload             [POST] → Upload resume
    └─ /feedback           [GET] → Get analysis
    
Service Layer (To be implemented)
    └─ ResumeAIService
       - parse_resume()
       - analyze_with_llm()
       - generate_feedback()

Integration
    └─ OpenAI API
       - gpt-4 model
       - structured output
```

### Week 3: MockMate (Stub Ready)
```
User (Frontend)
    │
    ├─ /start-interview    [POST] → Create interview
    │   ├─ company
    │   └─ role
    │
    ├─ /answer             [POST] → Submit answer
    │   └─ message
    │
    └─ /session/{id}       [GET] → Session status

Service Layer (To be implemented)
    └─ MockMateService
       - start_session()
       - generate_question()
       - evaluate_answer()
       - score_interview()

Integration
    ├─ LangChain
    │  └─ ConversationChain with memory
    │
    ├─ Chroma Vector DB
    │  └─ Question bank RAG
    │
    └─ OpenAI
       └─ Interview questions & evaluation
```

### Week 4: Payments (Stub Ready)
```
User (Frontend)
    │
    └─ Upgrade Plan [POST] → /upgrade
       └─ Razorpay Payment Gateway
           ├─ Order Creation
           ├─ Payment Processing
           └─ Webhook Handling

Service Layer
    └─ PaymentService
       - create_order()
       - verify_payment()
       - update_subscription()

Data Layer
    └─ Payment Model
       - razorpay_order_id
       - razorpay_payment_id
       - amount
       - subscription_plan
       - status
```

## Data Flow Examples

### Example 1: User Registration Flow
```
Frontend                              Backend                    Database
    │                                   │                            │
    │─── Register Form ────────────────>│                            │
    │    {email, pwd, username}         │                            │
    │                                   │─ Hash Password             │
    │                                   │─ Create User Record ──────>│
    │                              < ────────────────────────────────│
    │<──── JWT Token + User ID ────────│                            │
    │                                   │                            │
    └─ Store Token in LocalStorage      │                            │
    └─ Redirect to Dashboard            │                            │
```

### Example 2: FlashLearn Study Flow
```
User Clicks FlashLearn
    │
    ├─ Frontend: fetchFlashcards()
    │   └─ GET /api/v1/flashlearn/flashcards/random
    │       ├─ Authorization Header: Bearer {token}
    │       └─ Query: count=10, difficulty="medium"
    │
    ├─ Backend: Router → Service → Database
    │   ├─ Validate token
    │   ├─ Query: SELECT * FROM flashcards WHERE ... LIMIT 10
    │   └─ Return JSON array
    │
    ├─ Frontend: Render cards with React
    │   ├─ Display question
    │   ├─ Click to flip
    │   └─ Navigate with prev/next buttons
    │
    └─ User learns!
```

### Example 3: Login Flow
```
Frontend                      Backend                Database
    │                            │                      │
    │─ Login Form ──────────────>│                      │
    │  {email, password}         │                      │
    │                            │─ Find User ────────>│
    │                      <──User Record───           │
    │                            │                      │
    │                            │─ Verify Password     │
    │                            │  (bcrypt compare)    │
    │                            │                      │
    │<─ JWT Token + User ID ─────│                      │
    │                            │                      │
    └─ Store & Redirect         │                      │
```

## Technology Stack

```
Frontend                          Backend                    Database
├─ Next.js 14                     ├─ FastAPI                ├─ SQLite3
├─ React 18                       ├─ Python 3.10            ├─ SQLAlchemy ORM
├─ TypeScript                     ├─ Pydantic              ├─ Alembic (migrations)
├─ Tailwind CSS                   ├─ SQLAlchemy            └─ prepedge.db
├─ Zustand (state)                ├─ Uvicorn              
├─ Axios (HTTP client)            ├─ python-jose (JWT)    
└─ React Icons                    ├─ bcrypt (passwords)   
                                  ├─ CORS middleware      
                                  └─ uvicorn (server)     

Future Integrations
├─ OpenAI API (GPT-4)
├─ Chroma (Vector DB)
├─ LangChain
└─ Razorpay Payment Gateway
```

## Environment Variables

**Backend (.env)**
```
DATABASE_URL=sqlite:///./prepedge.db
OPENAI_API_KEY=sk-...
SECRET_KEY=your-secret-key
ALGORITHM=HS256
RAZORPAY_KEY_ID=key_...
RAZORPAY_KEY_SECRET=secret_...
```

**Frontend (.env.local)**
```
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

## Deployment Architecture (Future)

```
Vercel                          AWS / Render              AWS RDS
├─ Frontend                     ├─ FastAPI Backend       ├─ PostgreSQL
│  (Next.js)                    │  (Docker container)     │  (Production DB)
│  ├─ SSR/SSG                   │  ├─ Auto-scaling       └─ Automated backups
│  ├─ CDN                        │  ├─ Load balancing    
│  └─ Edge functions            │  └─ CI/CD             
│                                │                      
└─ API Routes                    └─ VPC + Security Groups
   (edge middleware for auth)
```

---

**Current Status**: Week 1 Complete - MVP Architecture Ready! 🏗️
