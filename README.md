# StorySpark AI — Where Ideas Become Stories

StorySpark AI is an AI-powered storytelling web application that turns text prompts and uploaded images into rich, immersive narratives.

## Technology Stack

- **Frontend:** React 19, TypeScript, Vite, Tailwind CSS v4, React Router, Lucide React
- **Backend:** Python 3.14, FastAPI, Uvicorn, Pydantic
- **AI Model:** Google Gemma 4 26B A4B Instruct (`gemma-4-26b-a4b-it`) *(Phase 4)*
- **Storage:** SQLite & Local File System *(Phase 3 & 4)*

---

## Getting Started (Phase 2 Development)

### 1. Backend Setup

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Start the FastAPI server:
```bash
uvicorn app.main:app --reload --port 8000
```
API Documentation will be available at: `http://localhost:8000/docs`  
Health check endpoint: `http://localhost:8000/api/health`

### 2. Frontend Setup

```bash
cd frontend
npm install
```

Configure environment:
```bash
cp .env.example .env
```

Start the Vite development server:
```bash
npm run dev
```
The application will run on `http://localhost:5173`.
