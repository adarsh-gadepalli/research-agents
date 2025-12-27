from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from pydantic import BaseModel
from typing import List, Dict, Any
import asyncio
import logging
from datetime import datetime
import json
import os
import ollama
# from duckduckgo_search import DDGS # Commented out

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize free research agent (Ollama)
# Check if Ollama is available
ollama_model = os.getenv("OLLAMA_MODEL", "llama3.2")
ollama_available = False

# Constants
CATEGORIES = ["Computer Science", "Biology", "Literature", "Music", "Politics", "Other"]

# In-memory history storage
# Structure: { "Category Name": [ { "question": "...", "timestamp": "...", "summary": "..." } ] }
research_history: Dict[str, List[Dict[str, Any]]] = {
    cat: [] for cat in CATEGORIES
}

try:
    # Test Ollama connection
    logger.info(f"🔍 Checking Ollama availability (model: {ollama_model})...")
    test_response = ollama.list()
    available_models = [model.model for model in test_response.models]
    logger.info(f"✅ Ollama is running. Available models: {', '.join(available_models) if available_models else 'None'}")
    
    # Check if the specified model is available
    matching_models = [model for model in available_models if ollama_model in model or model.startswith(ollama_model + ':')]
    if not matching_models:
        logger.warning(f"⚠️ Model '{ollama_model}' not found. Available models: {', '.join(available_models) if available_models else 'None'}")
        logger.warning(f"⚠️ Please install the model with: ollama pull {ollama_model}")
        logger.warning(f"⚠️ Or set OLLAMA_MODEL environment variable to an available model")
    else:
        # Use the first matching model
        ollama_model = matching_models[0]
        logger.info(f"✅ Using Ollama model: {ollama_model}")
        ollama_available = True
except Exception as e:
    logger.warning(f"⚠️ Ollama not available: {e}")

logger.info("✅ Direct LLM Agent initialized")

app = FastAPI(title="Research Agents API", version="1.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:3001"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

class ResearchRequest(BaseModel):
    question: str

class ResearchResponse(BaseModel):
    question: str
    summary: str
    findings: List[str]
    sources: List[str]
    timestamp: str
    category: str = "Other"

async def classify_question(question: str) -> str:
    """Classify the question into a predefined category using Ollama."""
    
    if not ollama_available:
        return "Other"
        
    prompt = f"""You are a classifier. Given the categories: {', '.join(CATEGORIES)}.
    Which category best fits the question: "{question}"?
    
    Rules:
    - "Creative writing", "Authors", "Books", "Novels", "Poems" -> Literature
    - "Coding", "AI", "Programming" -> Computer Science
    - "Songs", "Instruments", "Rap", "Hip Hop", "Music Theory" -> Music
    - "Government", "Elections" -> Politics
    - "Cells", "Animals", "Plants" -> Biology
    
    Return ONLY the category name from the list. Do not explain."""
    
    try:
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None, 
            lambda: ollama.generate(model=ollama_model, prompt=prompt)
        )
        category = response.get('response', '').strip()
        
        # Clean up response to ensure it matches a category
        for cat in CATEGORIES:
            if cat.lower() in category.lower():
                return cat
        return "Other"
    except Exception as e:
        logger.error(f"Classification failed: {e}")
        return "Other"

async def perform_research(question: str) -> ResearchResponse:
    """
    Perform research using ONLY the LLM (Direct Model Query).
    """
    start_time = datetime.now()
    logger.info(f"🔍 [DIRECT LLM] Starting query for: {question}")
    
    # Classify the question first
    category = await classify_question(question)
    logger.info(f"🏷️ [DIRECT LLM] Classified as: {category}")
    
    # Skip Web Search (Direct LLM Mode)
    logger.info("⏩ [DIRECT LLM] Skipping web search (Direct Mode enabled)...")
    search_results = []
    sources = [] # No external sources in direct mode
    
    # Direct LLM Prompt
    research_prompt = f"""You are an expert AI assistant. Answer the following question comprehensively using your own knowledge.
    
    Question: {question}
    
    Please provide:
    1. A concise summary (2-3 sentences)
    2. At least 3-5 specific key points or findings
    3. If you cite specific books, papers, or works, list them as sources.
    
    Format as JSON:
    {{
        "summary": "...",
        "findings": ["...", "...", ...],
        "sources": ["...", ...]
    }}
    """

    ai_response_text = ""
    if ollama_available:
        try:
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: ollama.chat(
                    model=ollama_model,
                    messages=[
                        {'role': 'system', 'content': 'You are a helpful AI assistant. Return valid JSON.'},
                        {'role': 'user', 'content': research_prompt}
                    ]
                )
            )
            ai_response_text = response.get('message', {}).get('content', '')
        except Exception as e:
            logger.error(f"Ollama generation failed: {e}")
            
    # Parse results
    summary = ""
    findings = []
    parsed_sources = []
    
    try:
        # Pre-cleaning: Remove markdown code blocks if present
        clean_text = ai_response_text.strip()
        if clean_text.startswith("```json"):
            clean_text = clean_text[7:]
        if clean_text.startswith("```"):
            clean_text = clean_text[3:]
        if clean_text.endswith("```"):
            clean_text = clean_text[:-3]
        clean_text = clean_text.strip()

        # Try to extract JSON from the response
        json_start = clean_text.find('{')
        json_end = clean_text.rfind('}') + 1
        
        if json_start >= 0 and json_end > json_start:
            json_str = clean_text[json_start:json_end]
            ai_data = json.loads(json_str)
            summary = ai_data.get("summary", "")
            findings = ai_data.get("findings", [])
            parsed_sources = ai_data.get("sources", [])
        else:
            # Fallback: parse the text directly
            logger.warning("⚠️ [DIRECT LLM] No JSON found in response, parsing text manually")
            lines = ai_response_text.split('\n')
            summary_lines = []
            finding_lines = []
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                # Simple heuristic to identify sections or bullet points
                if line.startswith('-') or line.startswith('•') or line.startswith('*') or (line[0].isdigit() and line[1] == '.'):
                    finding_lines.append(line.lstrip('- •*1234567890.').strip())
                elif len(line) > 50: # Assume long lines are summary or content
                    summary_lines.append(line)
            
            summary = ' '.join(summary_lines[:2]) if summary_lines else "Response received."
            findings = finding_lines[:5]
            
    except Exception as e:
        logger.error(f"Parsing error: {e}")
        # Last resort fallback if JSON parse fails mid-way
        summary = ai_response_text[:300] + "..." if ai_response_text else "Error parsing results."
        findings = ["Could not parse structured findings from AI response.", f"Raw response excerpt: {ai_response_text[:100]}..."]

    # Combine sources
    all_sources = list(set(sources + parsed_sources))[:10]
    if not all_sources:
        all_sources = ["Direct AI Knowledge"]

    # Ensure findings is not empty
    if not findings:
        findings = ["No specific findings could be extracted."]

    result = ResearchResponse(
        question=question,
        summary=summary,
        findings=[str(f) for f in findings],
        sources=[str(s) for s in all_sources],
        timestamp=datetime.now().isoformat(),
        category=category
    )
    
    # Save to history
    if category not in research_history:
        # Should not happen given init, but safe fallback
        research_history[category] = []
    
    # Store full version in history
    history_item = {
        "question": question,
        "summary": summary,
        "findings": result.findings,
        "sources": result.sources,
        "timestamp": result.timestamp,
        "category": category
    }
    research_history[category].insert(0, history_item) # Prepend
    
    return result

@app.get("/")
async def root():
    return {"message": "Research Agents API is running"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.get("/api/history")
async def get_history():
    """Get research history grouped by category."""
    logger.info("📚 GET /api/history - Fetching research history")
    # Ensure all categories are present even if empty
    response_history = {cat: [] for cat in CATEGORIES}
    response_history.update(research_history)
    return response_history

@app.post("/api/research", response_model=ResearchResponse)
async def research(request: ResearchRequest):
    request_start_time = datetime.now()
    logger.info(f"📥 Request: {request.question}")
    
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question is required")
        
    try:
        # Use a timeout wrapper
        timeout_seconds = float(os.getenv("RESEARCH_TIMEOUT", "60.0"))
        result = await asyncio.wait_for(
            perform_research(request.question),
            timeout=timeout_seconds
        )
        return result
    except asyncio.TimeoutError:
        logger.error("⏱️ Research timeout")
        raise HTTPException(status_code=504, detail="Research timeout")
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
