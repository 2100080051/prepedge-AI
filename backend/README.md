## PrepEdge AI - Backend

Python FastAPI backend for the PrepEdge AI placement preparation platform.

### Setup

1. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create `.env` file from `.env.example`:
```bash
cp .env.example .env
```

4. Update `.env` with your credentials:
- `OPENAI_API_KEY`: Your OpenAI API key
- `RAZORPAY_KEY_ID` and `RAZORPAY_KEY_SECRET`: Your Razorpay credentials

5. Run the server:
```bash
python main.py
# Or use: uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`
API documentation: `http://localhost:8000/docs`

### Project Structure

```
backend/
├── main.py                 # FastAPI app entry point
├── requirements.txt        # Python dependencies
├── .env.example           # Environment variables template
└── app/
    ├── config.py          # Configuration settings
    ├── database/
    │   ├── session.py     # Database session setup
    │   └── models.py      # SQLAlchemy models
    ├── auth/
    │   ├── utils.py       # JWT and password utilities
    │   ├── schemas.py     # Pydantic schemas
    │   ├── router.py      # Auth endpoints
    │   └── dependencies.py # Auth dependencies
    └── modules/
        ├── flashlearn/    # FlashLearn module (Week 1)
        ├── resumeai/      # ResumeAI module (Week 2)
        └── mockmate/      # MockMate module (Week 3)
```

### API Endpoints

#### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login user
- `GET /api/v1/auth/me` - Get current user

#### FlashLearn
- `GET /api/v1/flashlearn/flashcards` - Get flashcards
- `GET /api/v1/flashlearn/flashcards/random` - Get random flashcards
- `GET /api/v1/flashlearn/topics` - Get all topics
- `GET /api/v1/flashlearn/companies` - Get all companies
- `POST /api/v1/flashlearn/seed` - Seed database

#### ResumeAI (Coming Week 2)
- `POST /api/v1/resumeai/upload` - Upload resume
- `GET /api/v1/resumeai/feedback` - Get feedback

#### MockMate (Coming Week 3)
- `POST /api/v1/mockmate/start-interview` - Start interview
- `POST /api/v1/mockmate/answer` - Submit answer
