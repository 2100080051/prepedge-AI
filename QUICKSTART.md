# 🚀 Quick Start Guide - PrepEdge AI

## 5-Minute Quick Start

### Step 1: Backend Setup (Windows)
```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
REM Update .env with your OpenAI API key
python main.py
```

**Backend should now be running at**: `http://localhost:8000`

### Step 2: Frontend Setup (New Terminal)
```bash
cd frontend
npm install
npm run dev
```

**Frontend should now be running at**: `http://localhost:3000`

### Step 3: Test the App
1. Open `http://localhost:3000` in your browser
2. Click **"Sign Up Free"**
3. Fill in registration form:
   - Full Name: Your Name
   - Username: testuser123
   - Email: test@example.com
   - Password: password123
4. Click **Sign Up**
5. You'll be logged in and redirected to dashboard
6. Click **FlashLearn**
7. Select a topic from dropdown
8. Click **Seed Database** (if this is first time)
9. Start studying! Click cards to flip them

## What's Built (Week 1 - FlashLearn)

✅ **FlashLearn Module** - Complete
- Interactive flashcard system
- Multiple topics: Aptitude, Coding, HR Interview
- Companies: TCS, Infosys, Wipro
- Seed database with sample questions

✅ **Authentication**
- User registration
- User login
- JWT tokens
- Protected endpoints

✅ **Backend API**
- FastAPI with auto-documentation
- SQLing database
- RESTful endpoints

✅ **Frontend**
- Next.js with TypeScript
- Tailwind CSS styling
- Zustand state management
- API client with auth headers

## Sample Login After Signup
```
Email: test@example.com
Password: password123
```

## API Endpoints (http://localhost:8000/docs)

### Auth
- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`
- `GET /api/v1/auth/me`

### FlashLearn (Available Now!)
- `GET /api/v1/flashlearn/flashcards` - Get all flashcards
- `GET /api/v1/flashlearn/flashcards/random` - Random cards
- `GET /api/v1/flashlearn/topics` - All topics
- `GET /api/v1/flashlearn/companies` - All companies
- `POST /api/v1/flashlearn/seed` - Add sample data

### ResumeAI (Coming Week 2)
- `POST /api/v1/resumeai/upload`
- `GET /api/v1/resumeai/feedback`

### MockMate (Coming Week 3)
- `POST /api/v1/mockmate/start-interview`
- `POST /api/v1/mockmate/answer`

## Troubleshooting

### Backend won't start
```bash
# Wrong directory?
cd backend

# Python version?
python --version  # Should be 3.10+

# Virtual env not activated?
venv\Scripts\activate

# Dependencies not installed?
pip install -r requirements.txt
```

### Frontend won't start
```bash
# Wrong directory?
cd frontend

# Node installed?
node --version  # Should be 18+

# Dependencies not installed?
npm install

# Port 3000 in use?
# Kill existing process or use different port: npm run dev -- -p 3001
```

### Can't connect backend to frontend
- Check backend is running at http://localhost:8000
- Check frontend .env.local has correct API URL:
  ```
  NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
  ```
- Reload frontend page (Ctrl+Shift+R)

### Login fails
- Make sure you registered first
- Check email and password match
- Backend must be running
- Check database file exists: `backend/prepedge.db`

## Next Steps

1. **Test all modules** at http://localhost:3000
2. **Check API docs** at http://localhost:8000/docs
3. **Read product document** (PrepEdge_AI_Product_Document_v1.0.docx)
4. **Plan Week 2**: ResumeAI module development

## File Locations

- **Backend main file**: `backend/main.py`
- **Frontend main page**: `frontend/src/pages/index.tsx`
- **FlashLearn API**: `backend/app/modules/flashlearn/`
- **FlashLearn UI**: `frontend/src/pages/flashlearn.tsx`
- **Database file**: `backend/prepedge.db` (auto-created)

## Database Structure

**Users Table**: email, username, password, subscription plan
**Flashcards Table**: question, answer, topic, difficulty, company
**Study Sessions**: track user learning progress
**Interview Sessions**: track mock interview data
**Resumes**: store uploaded resumes
**Payments**: payment tracking for subscriptions

## Revenue Model (Implemented in Week 4)
- **Free**: 5 cards/day
- **Pro**: ₹499/month - Unlimited
- **Premium**: ₹999/month - All features

---

**Status**: Week 1 Complete - MVP Ready! 🎉
**Built in**: FastAPI + Next.js + SQLite
**Time to Production**: Week 4
