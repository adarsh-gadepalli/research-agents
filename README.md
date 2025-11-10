# Research Agents 🔍

A modern research agent application built with Next.js and FastAPI. Enter a research question and get comprehensive findings with sources.

## Features

- 🎨 **Modern UI** - Beautiful dark-themed interface with animated background
- ⚡ **Fast Performance** - Built with Next.js 14 and FastAPI
- 🔄 **Real-time Research** - Asynchronous research processing
- 📊 **Structured Results** - Organized findings with sources
- 🎯 **Type-Safe** - Full TypeScript and Pydantic validation

## Tech Stack

### Frontend
- **Next.js 14** - React framework with App Router
- **TypeScript** - Type-safe development
- **Tailwind CSS** - Utility-first CSS framework
- **React Hooks** - Modern state management

### Backend
- **FastAPI** - Modern Python web framework
- **Uvicorn** - ASGI server
- **Pydantic** - Data validation

## Prerequisites

- **Node.js** 18+ and npm
- **Python** 3.8+
- **pip** (Python package manager)

## Quick Start

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd research-agents
```

### 2. Install Dependencies

**Python Backend:**
```bash
pip install -r requirements.txt
```

**Node.js Frontend:**
```bash
npm install
```

### 3. Run the Application

**Option A: Run both servers together (Recommended)**
```bash
npm run dev:all
```

**Option B: Run servers separately**

Terminal 1 - FastAPI Backend:
```bash
npm run dev:api
# or
cd src && python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Terminal 2 - Next.js Frontend:
```bash
npm run dev
```

### 4. Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs (FastAPI automatic documentation)

## API Endpoints

### Research Endpoint
```http
POST /api/research
Content-Type: application/json

{
  "question": "Your research question here"
}
```

**Response:**
```json
{
  "question": "Your research question here",
  "summary": "Research summary...",
  "findings": [
    "Finding 1...",
    "Finding 2...",
    "Finding 3..."
  ],
  "sources": [
    "Source 1",
    "Source 2",
    "Source 3"
  ],
  "timestamp": "2024-01-01T00:00:00"
}
```

### Other Endpoints
- `GET /` - API status
- `GET /health` - Health check
- `GET /docs` - Interactive API documentation (Swagger UI)
- `GET /redoc` - Alternative API documentation

## Environment Variables

Create a `.env.local` file in the root directory:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Project Structure

```
research-agents/
├── app/                      # Next.js app directory
│   ├── api/                  # Next.js API routes (optional)
│   │   └── research/
│   │       └── route.ts
│   ├── components/           # React components
│   │   └── AnimatedBackground.tsx
│   ├── globals.css           # Global styles
│   ├── layout.tsx            # Root layout
│   └── page.tsx              # Main page
├── src/                      # Python source
│   └── main.py              # FastAPI application
├── public/                   # Static assets
├── requirements.txt          # Python dependencies
├── package.json              # Node.js dependencies
├── tailwind.config.ts        # Tailwind configuration
├── tsconfig.json             # TypeScript configuration
└── next.config.js            # Next.js configuration
```

## Available Scripts

### Frontend (Next.js)
- `npm run dev` - Start Next.js development server
- `npm run build` - Build for production
- `npm run start` - Start production server
- `npm run lint` - Run ESLint

### Backend (FastAPI)
- `npm run dev:api` - Start FastAPI development server
- `npm run dev:all` - Run both frontend and backend

## Development

### Adding New Research Features

The research logic is in `src/main.py`. You can extend it with:

- Web scraping libraries (BeautifulSoup, Scrapy)
- Search APIs (Google Search, DuckDuckGo)
- AI/ML models (OpenAI, Anthropic, LangChain)
- Database queries
- External APIs

### Example Extension

```python
# In src/main.py
import requests
from bs4 import BeautifulSoup

async def perform_research(question: str):
    # Add your research logic here
    # e.g., web scraping, API calls, etc.
    pass
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is open source and available under the MIT License.

## Support

For issues and questions, please open an issue on GitHub.

