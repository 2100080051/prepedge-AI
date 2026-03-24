# 🚀 PrepEdge AI - Complete Project Setup

## Overview

PrepEdge AI is an all-in-one AI-powered placement preparation platform built for Indian engineering students. This is a full-stack application with:

- **Backend**: FastAPI (Python) with SQLAlchemy ORM
- **Frontend**: Next.js (React/TypeScript) with Tailwind CSS
- **Database**: SQLite (easily replaceable with PostgreSQL)
- **Authentication**: JWT-based auth
- **Payment**: Razorpay integration

## Project Structure

```
prepedge-ai/
├── backend/                    # FastAPI backend
│   ├── app/
│   │   ├── config.py          # Configuration
│   │   ├── auth/              # Authentication modules
│   │   ├── database/          # Database models & session
│   │   └── modules/           # Feature modules
│   │       ├── flashlearn/    # Week 1: Study tool
│   │       ├── resumeai/      # Week 2: Resume optimizer
│   │       └── mockmate/      # Week 3: Mock interviewer
│   ├── main.py                # App entry point
│   ├── requirements.txt        # Python dependencies
│   ├── .env.example           # Environment template
│   └── README.md              # Backend docs
│
└── frontend/                   # Next.js frontend
    ├── src/
    │   ├── pages/             # Next.js pages
    │   ├── components/        # React components
    │   ├── store/             # Zustand state management
    │   └── lib/               # Utilities & API clients
    ├── package.json
    ├── tsconfig.json
    ├── tailwind.config.ts
    ├── next.config.js
    └── README.md              # Frontend docs
```

## Build Instructions

### Prerequisites
- Python 3.10+
- Node.js 18+
- npm or yarn

### Backend Setup

1. **Navigate to backend directory**:
```bash
cd backend
```

2. **Create and activate virtual environment**:
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

3. **Install Python dependencies**:
```bash
pip install -r requirements.txt
```

4. **Create `.env` file**:
```bash
cp .env.example .env
```

5. **Update `.env` with your credentials**:
```
OPENAI_API_KEY=your-key-here
RAZORPAY_KEY_ID=your-key
RAZORPAY_KEY_SECRET=your-secret
```

6. **Run the development server**:
```bash
python main.py
# Or using uvicorn:
uvicorn main:app --reload
```

The API will be available at: `http://localhost:8000`
- Swagger docs: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Frontend Setup

1. **Navigate to frontend directory**:
```bash
cd frontend
```

2. **Install dependencies**:
```bash
npm install
```

3. **Create `.env.local`**:
```
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

4. **Run development server**:
```bash
npm run dev
```

The app will be available at: `http://localhost:3000`

## 4-Week Build Plan

### Week 1: Foundation + FlashLearn (✅ Complete)
- [x] Project structure setup
- [x] Database models and schemas
- [x] Authentication (JWT)
- [x] FlashLearn API endpoints
- [x] FlashLearn web UI
- [x] Sample flashcard data seeding

**Current Status**: Start your backend and frontend to test FlashLearn

### Week 2: ResumeAI Module
- [ ] Resume file upload API
- [ ] PDF/DOCX parsing
- [ ] OpenAI integration for analysis
- [ ] Resume feedback endpoints
- [ ] Frontend resume upload UI
- [ ] Feedback display component

### Week 3: MockMate Module
- [ ] Interview session management
- [ ] LangChain ConversationChain integration
- [ ] Chroma vector database setup
- [ ] Question generation from RAG
- [ ] Interview UI with chat interface
- [ ] Session scoring system

### Week 4: Payments & Launch
- [ ] Razorpay payment integration
- [ ] Subscription plan logic
- [ ] Payment webhook handling
- [ ] Deployment setup
- [ ] Performance optimization
- [ ] Launch monitoring

## Quick Start (Testing Both Servers)

### Terminal 1 - Backend:
```bash
cd backend
source venv/bin/activate  # or venv\Scripts\activate on Windows
python main.py
```

### Terminal 2 - Frontend:
```bash
cd frontend
npm run dev
```

### Testing the App:
1. Open `http://localhost:3000` in browser
2. Click "Sign Up Free" or go to `/auth/register`
3. Create test account
4. Navigate to FlashLearn
5. Click "Seed Database" (first time)
6. Start studying!

## API Endpoints

### Authentication
```
POST   /api/v1/auth/register      - Register new user
POST   /api/v1/auth/login         - Login user
GET    /api/v1/auth/me            - Get current user
```

### FlashLearn (Week 1 - Available Now)
```
GET    /api/v1/flashlearn/flashcards          - Get flashcards
GET    /api/v1/flashlearn/flashcards/random   - Get random cards
GET    /api/v1/flashlearn/topics              - Get all topics
GET    /api/v1/flashlearn/companies           - Get all companies
POST   /api/v1/flashlearn/seed                - Seed database
```

### ResumeAI (Week 2)
```
POST   /api/v1/resumeai/upload       - Upload resume
GET    /api/v1/resumeai/feedback     - Get feedback
```

### MockMate (Week 3)
```
POST   /api/v1/mockmate/start-interview  - Start interview
POST   /api/v1/mockmate/answer           - Submit answer
GET    /api/v1/mockmate/session/{id}     - Get session status
```

## Database Models

### User
- Email, username, password
- Full name
- Subscription plan (free/pro/premium)
- Timestamps

### Flashcard
- Question & answer
- Topic & company
- Difficulty level
- Created timestamp

### Interview Session
- User ID
- Company & role
- Duration & score
- Status (active/completed)

### Resume Upload
- User ID
- File path & content
- Score & feedback

### Payment
- Razorpay order/payment IDs
- Amount & currency
- Status & subscription plan

## Environment Variables

**Backend (.env)**:
```
DATABASE_URL=sqlite:///./prepedge.db
OPENAI_API_KEY=your-api-key
SECRET_KEY=your-secret-key
RAZORPAY_KEY_ID=your-key
RAZORPAY_KEY_SECRET=your-secret
```

**Frontend (.env.local)**:
```
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

## Testing Checklist

- [ ] Backend starts without errors
- [ ] Frontend connects to backend
- [ ] Registration works
- [ ] Login works
- [ ] FlashLearn loads flashcards
- [ ] Card flipping works
- [ ] Navigation between cards works

## Performance Targets

- API response time: < 200ms
- Page load time: < 2s
- Flashcard flip: < 100ms
- Supporting 100 concurrent users

## Revenue Model

- **Free**: Limited to 5 flashcards/day
- **Pro**: ₹499/month - Unlimited flashcards + 5 mock interviews
- **Premium**: ₹999/month - Everything + resume analysis + priority support

Target: ₹5,000/month by Month 2 (10+ paying users)

## Next Steps

1. **Run both servers** (see Quick Start above)
2. **Test the FlashLearn module**
3. **Create sample user account**
4. **Verify API endpoints** at `http://localhost:8000/docs`
5. **Plan Week 2 ResumeAI implementation**

## Support & Documentation

- Backend docs: `backend/README.md`
- Frontend docs: `frontend/README.md`
- API swagger: `http://localhost:8000/docs`
- Architecture: See product document (.docx)

---

**Built for**: Indian engineering students preparing for campus placements
**Timeline**: 4 weeks to MVP
**Revenue Goal**: ₹5,000/month
**Target Users**: TCS, Infosys, Wipro, Accenture prep
