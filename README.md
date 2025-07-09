# Research Assistant

AI-powered research assistant for semantic search, document analysis, and paper comparison using OpenAI embeddings and ChromaDB.

## Project Structure

```
research-assistant/
├── backend/                    # FastAPI backend
│   ├── src/
│   │   ├── main.py            # API endpoints
│   │   ├── models.py          # Data models
│   │   ├── embeddings.py      # OpenAI embeddings
│   │   ├── vector_store.py    # ChromaDB operations
│   │   ├── usage_tracker.py   # Redis analytics
│   │   └── auth.py            # JWT authentication
│   ├── chroma_db/             # Vector database storage
│   ├── requirements.txt       # Python dependencies
│   └── env.example           # Environment variables
├── frontend/                  # Next.js frontend
│   ├── src/
│   │   ├── app/              # App router pages
│   │   ├── components/       # React components
│   │   └── lib/              # Utilities
│   ├── package.json          # Node dependencies
│   └── env.example          # Environment variables
└── sample_data/              # Test data
```

## Quick Setup

### 1. Prerequisites
```bash
# Install required services
brew install redis          # macOS
# or
sudo apt install redis      # Ubuntu

# Start Redis server
redis-server
```

### 2. Backend Setup
```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp env.example .env
# Edit .env with your OpenAI API key

# Start backend
python run.py
```

### 3. Frontend Setup
```bash
cd frontend

# Install dependencies
npm install

# Configure environment
cp env.example .env.local
# Edit .env.local with backend URL

# Start frontend
npm run dev
```

## Environment Variables

### Backend (.env)
```bash
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=text-embedding-ada-002
OPENAI_CHAT_MODEL=gpt-3.5-turbo

# Database Configuration
CHROMA_DB_PATH=./chroma_db
CHROMA_COLLECTION_NAME=journal_chunks

# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=2

# JWT Authentication
JWT_SECRET_KEY=your-super-secret-jwt-key
JWT_EXPIRATION_HOURS=24

# Server Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=True
ALLOWED_ORIGINS=http://localhost:3000
```

### Frontend (.env.local)
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
OPENAI_API_KEY=your_openai_api_key_here
```

## API Endpoints

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/` | Health check | None |
| POST | `/api/auth/token` | Generate JWT token | None |
| GET | `/api/stats` | Database statistics | None |
| PUT | `/api/upload` | Upload papers | 🔒 Admin |
| POST | `/api/similarity_search` | Search papers | None |
| GET | `/api/{doc_id}` | Get document | None |
| POST | `/api/compare` | Compare papers | None |
| GET | `/api/popular` | Popular papers | 🔒 Analytics |
| GET | `/api/analytics` | Usage analytics | 🔒 Analytics |

## Testing

### Backend API
```bash
cd backend
python test_api.py          # Test all endpoints
python test_auth.py         # Test authentication
```

### Generate Auth Token
```bash
curl -X POST "http://localhost:8000/api/auth/token" \
  -H "Content-Type: application/json" \
  -d '{"user_id": "admin", "role": "admin"}'
```

## Features

- **Semantic Search**: OpenAI embeddings with ChromaDB
- **Paper Comparison**: AI-powered analysis using GPT-3.5-turbo
- **Analytics**: Redis-based usage tracking
- **Authentication**: JWT with role-based access control
- **File Upload**: Local files, URLs, and Google Drive support
- **Real-time**: WebSocket support for live updates

## Architecture

- **Backend**: FastAPI + ChromaDB + Redis + OpenAI
- **Frontend**: Next.js + TypeScript + Tailwind CSS
- **Database**: ChromaDB (vector) + Redis (analytics)
- **Authentication**: JWT tokens with role-based permissions
- **Deployment**: Docker support (optional)

## Usage

1. **Start Services**: Redis → Backend → Frontend
2. **Get Token**: Generate admin token via `/api/auth/token`
3. **Upload Data**: Use token to upload papers via `/api/upload`
4. **Search**: Query papers via `/api/similarity_search`
5. **Analytics**: View usage stats via `/api/analytics`

## Documentation

- **API Documentation**: `backend/API_DOCUMENTATION.md`
- **Frontend README**: `frontend/README.md`

