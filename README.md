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

## Features

- **FlashLearn**: AI-powered flashcard learning system
- **LearnAI**: Intelligent concept explanations with real-world analogies and examples
- **ResumeAI**: Resume analysis and optimization with ATS scoring
- **MockMate**: AI-powered mock interview preparation with proctoring
- **Authentication**: Secure JWT-based user authentication
- **Payment Integration**: Razorpay payment gateway for subscriptions

## API Endpoints

### Authentication
```
POST   /api/v1/auth/register      - Register new user
POST   /api/v1/auth/login         - Login user
GET    /api/v1/auth/me            - Get current user
```

### FlashLearn
```
GET    /api/v1/flashlearn/flashcards          - Get flashcards
GET    /api/v1/flashlearn/flashcards/random   - Get random cards
GET    /api/v1/flashlearn/topics              - Get all topics
GET    /api/v1/flashlearn/companies           - Get all companies
POST   /api/v1/flashlearn/seed                - Seed database
```

### LearnAI
```
POST   /api/v1/learnai/explain    - Get concept explanation with analogies and examples
```

### ResumeAI
```
POST   /api/v1/resumeai/upload       - Upload and analyze resume
GET    /api/v1/resumeai/feedback     - Get resume feedback history
```

### MockMate
```
POST   /api/v1/mockmate/start-interview  - Start mock interview session
POST   /api/v1/mockmate/answer           - Submit answer to interview question
GET    /api/v1/mockmate/session/{id}     - Get interview session status
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

## Documentation

- **Backend Docs**: See `backend/README.md`
- **Frontend Docs**: See `frontend/README.md`
- **API Documentation**: Available at `http://localhost:8000/docs`
- **ReDoc Documentation**: Available at `http://localhost:8000/redoc`

## Architecture

PrepEdge AI is designed with a modern, scalable architecture:

- **Backend**: FastAPI microservices with modular structure
- **Frontend**: Next.js with server-side rendering and static generation
- **Database**: SQLite for development (easily migrate to PostgreSQL for production)
- **Authentication**: JWT tokens with secure storage
- **State Management**: Zustand for frontend state
- **Styling**: Tailwind CSS for responsive design

## License

This project is licensed under the MIT License. See LICENSE file for details.

## Support

For issues, questions, or contributions, please open an issue on GitHub.

---

Built with ❤️ for Indian engineering students preparing for campus placements.

**Built for**: Indian engineering students preparing for campus placements
**Timeline**: 4 weeks to MVP
**Revenue Goal**: ₹5,000/month
**Target Users**: TCS, Infosys, Wipro, Accenture prep
