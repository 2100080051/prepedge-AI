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



**Built for**: Indian engineering students preparing for campus placements
**Timeline**: 4 weeks to MVP
**Revenue Goal**: ₹5,000/month
**Target Users**: TCS, Infosys, Wipro, Accenture prep
