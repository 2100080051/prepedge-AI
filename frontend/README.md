# PrepEdge AI - Frontend

React/Next.js frontend for PrepEdge AI placement prep platform.

## Setup

1. Install dependencies:
```bash
npm install
```

2. Create `.env.local` file:
```
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

3. Run development server:
```bash
npm run dev
```

The app will be available at `http://localhost:3000`

## Project Structure

```
frontend/
├── src/
│   ├── pages/
│   │   ├── index.tsx          # Home page
│   │   ├── dashboard.tsx      # User dashboard
│   │   ├── flashlearn.tsx     # FlashLearn module
│   │   ├── resumeai.tsx       # ResumeAI module
│   │   ├── mockmate.tsx       # MockMate module
│   │   └── auth/
│   │       ├── login.tsx      # Login page
│   │       └── register.tsx   # Register page
│   ├── components/            # Reusable components
│   ├── store/                 # Zustand stores
│   └── lib/                   # API clients, utilities
├── package.json
├── tsconfig.json
└── tailwind.config.ts
```

## Features

- **Authentication**: User registration and login with JWT
- **FlashLearn**: Interactive flashcard system for aptitude, coding, and HR prep
- **ResumeAI**: (Coming Week 2) Resume analysis and optimization
- **MockMate**: (Coming Week 3) AI mock interviews
- **Responsive Design**: Works on mobile, tablet, and desktop
- **State Management**: Zustand for global state
- **API Integration**: Axios for API calls with auth headers

## Tech Stack

- Next.js 14
- React 18
- TypeScript
- Tailwind CSS
- Zustand (State Management)
- Axios (HTTP Client)
