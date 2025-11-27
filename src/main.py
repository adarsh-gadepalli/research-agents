from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from pydantic import BaseModel
from typing import List
import asyncio
import logging
from datetime import datetime
import json
import os
import ollama
from duckduckgo_search import DDGS

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize free research agent (Ollama + DuckDuckGo)
# Check if Ollama is available
ollama_model = os.getenv("OLLAMA_MODEL", "llama3.2")  # Default to llama3.2, can use llama3.1, mistral, etc.
ollama_available = False
try:
    # Test Ollama connection
    logger.info(f"🔍 Checking Ollama availability (model: {ollama_model})...")
    test_response = ollama.list()
    # Ollama returns a ListResponse object with a models attribute containing Model objects
    # Each Model object has a 'model' attribute (not 'name') with the model name
    available_models = [model.model for model in test_response.models]
    logger.info(f"✅ Ollama is running. Available models: {', '.join(available_models) if available_models else 'None'}")
    
    # Check if the specified model is available (handle both "llama3.2" and "llama3.2:latest")
    matching_models = [model for model in available_models if ollama_model in model or model.startswith(ollama_model + ':')]
    if not matching_models:
        logger.warning(f"⚠️ Model '{ollama_model}' not found. Available models: {', '.join(available_models) if available_models else 'None'}")
        logger.warning(f"⚠️ Please install the model with: ollama pull {ollama_model}")
        logger.warning(f"⚠️ Or set OLLAMA_MODEL environment variable to an available model")
        logger.warning(f"⚠️ Research will work with DuckDuckGo search only (no AI analysis)")
    else:
        # Use the first matching model (prefer exact match, then any match)
        ollama_model = matching_models[0]  # Use the actual model name from Ollama
        logger.info(f"✅ Using Ollama model: {ollama_model}")
        ollama_available = True
except Exception as e:
    logger.warning(f"⚠️ Ollama not available: {e}")
    logger.warning("⚠️ Research will work with DuckDuckGo search only (no AI analysis)")
    logger.warning("⚠️ To enable AI analysis, install Ollama from https://ollama.ai")
    logger.warning("⚠️ Then run: ollama pull llama3.2")

logger.info("✅ Free research agent initialized (DuckDuckGo search" + (" + Ollama AI" if ollama_available else "") + ")")

# Print startup message immediately
print("=" * 60)
print("🚀 FastAPI Server Initializing")
print("=" * 60)

app = FastAPI(title="Research Agents API", version="1.0.0")

# Configure CORS FIRST - This must be added before other middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:3001"],  # Next.js dev server
    allow_credentials=False,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
    expose_headers=["*"],
)

# Add middleware to log all requests including OPTIONS (after CORS)
@app.middleware("http")
async def log_requests(request: Request, call_next):
    if request.method == "OPTIONS":
        logger.info(f"🔀 OPTIONS request to {request.url.path}")
        logger.info(f"   Origin: {request.headers.get('origin', 'None')}")
        logger.info(f"   Access-Control-Request-Method: {request.headers.get('access-control-request-method', 'None')}")
        logger.info(f"   Access-Control-Request-Headers: {request.headers.get('access-control-request-headers', 'None')}")
    response = await call_next(request)
    if request.method == "OPTIONS":
        logger.info(f"✅ OPTIONS response status: {response.status_code}")
    return response

# Log startup
@app.on_event("startup")
async def startup_event():
    print("\n" + "=" * 60)
    print("✅ FastAPI Server Started Successfully")
    print("=" * 60)
    print("Server running on: http://0.0.0.0:8000")
    print("API Documentation: http://localhost:8000/docs")
    print("Health Check: http://localhost:8000/health")
    print("=" * 60 + "\n")
    logger.info("FastAPI server started and ready to accept requests")


class ResearchRequest(BaseModel):
    question: str


class ResearchResponse(BaseModel):
    question: str
    summary: str
    findings: List[str]
    sources: List[str]
    timestamp: str


@app.get("/")
async def root():
    logger.info("📡 GET / - Root endpoint accessed")
    return {"message": "Research Agents API is running"}


@app.get("/health")
async def health():
    logger.info("💚 GET /health - Health check requested") 
    logger.info("✅ Health check passed - Server is healthy")
    return {"status": "healthy"}


async def perform_research(question: str) -> ResearchResponse:
    """
    Perform research using free tools: Ollama (local LLM) + DuckDuckGo (web search).
    Completely free - no API costs!
    """
    start_time = datetime.now()
    logger.info("🔍 [RESEARCH] Starting research process...")
    logger.info(f"🔍 [RESEARCH] Question received: {question}")
    logger.info(f"🔍 [RESEARCH] Start time: {start_time.isoformat()}")
    
    # Step 1: Initialization
    logger.info("📝 [RESEARCH] Step 1/4: Initializing free research agent...")
    logger.info("✅ [RESEARCH] Step 1/4: Research agent initialized (Ollama + DuckDuckGo)")
    
    # Step 2: Searching the web with DuckDuckGo
    logger.info("🔎 [RESEARCH] Step 2/4: Searching web with DuckDuckGo...")
    
    try:
        search_results = []
        sources = []
        
        try:
            with DDGS() as ddgs:
                # Search for relevant information
                search_results = list(ddgs.text(question, max_results=5))
                logger.info(f"✅ [RESEARCH] Found {len(search_results)} search results")
                
                # Extract sources (ensure we get strings)
                for result in search_results:
                    if isinstance(result, dict):
                        if 'href' in result:
                            sources.append(str(result['href']))
                        elif 'url' in result:
                            sources.append(str(result['url']))
                    elif isinstance(result, str):
                        sources.append(result)
        except Exception as e:
            logger.warning(f"⚠️ [RESEARCH] DuckDuckGo search error: {e}")
            logger.warning("⚠️ [RESEARCH] Continuing without web search results")
        
        # Step 3: Analyzing with Ollama
        logger.info("🧠 [RESEARCH] Step 3/4: Analyzing with Ollama LLM...")
        
        # Prepare context from search results
        search_context = ""
        if search_results:
            search_context = "\n\nWeb Search Results:\n"
            for i, result in enumerate(search_results[:3], 1):
                title = result.get('title', '')
                body = result.get('body', '')
                search_context += f"{i}. {title}\n{body}\n\n"
        
        # Create research prompt
        research_prompt = f"""You are an expert research assistant. Conduct thorough research on the following question and provide a comprehensive analysis.

Research Question: {question}
{search_context}

Please provide:
1. A concise summary (2-3 sentences) of the key findings
2. At least 3-5 specific findings, each as a clear, informative statement
3. List any relevant sources or references

Format your response as JSON with the following structure:
{{
    "summary": "A concise summary of the research findings",
    "findings": ["Finding 1", "Finding 2", "Finding 3", ...],
    "sources": ["Source 1", "Source 2", ...]
}}

Be thorough, accurate, and provide valuable insights about the topic."""

        # Step 3: Analyzing with Ollama (if available) or using search results directly
        if ollama_available:
            logger.info("🧠 [RESEARCH] Step 3/4: Analyzing with Ollama LLM...")
            # Call Ollama
            loop = asyncio.get_event_loop()
            logger.info(f"🤖 [RESEARCH] Querying Ollama model: {ollama_model}...")
            
            def call_ollama():
                try:
                    # Try using chat API first (better for structured responses)
                    response = ollama.chat(
                        model=ollama_model,
                        messages=[
                            {
                                'role': 'system',
                                'content': 'You are an expert research assistant. Provide well-structured, accurate research findings in JSON format when possible.'
                            },
                            {
                                'role': 'user',
                                'content': research_prompt
                            }
                        ]
                    )
                    return response.get('message', {}).get('content', '')
                except Exception as e:
                    logger.warning(f"⚠️ Chat API failed, trying generate: {e}")
                    # Fallback to generate API
                    response = ollama.generate(model=ollama_model, prompt=research_prompt)
                    return response.get('response', '')
            
            ai_response_text = await loop.run_in_executor(None, call_ollama)
            logger.info(f"✅ [RESEARCH] Step 3/4: Analysis completed ({len(ai_response_text)} characters)")
        else:
            # Fallback: Use search results directly without AI analysis
            logger.info("🧠 [RESEARCH] Step 3/4: Synthesizing search results (Ollama not available)...")
            logger.info("⚠️ [RESEARCH] Using search results directly - install Ollama for AI-powered analysis")
            
            # Create a summary from search results
            if search_results:
                ai_response_text = f"""Summary: Based on web search results, here are key findings about "{question}".

Findings:
"""
                for i, result in enumerate(search_results[:5], 1):
                    title = result.get('title', '')
                    body = result.get('body', '')
                    ai_response_text += f"- {title}: {body[:200]}\n"
                
                ai_response_text += "\nSources:\n"
                for source in sources[:5]:
                    ai_response_text += f"- {source}\n"
            else:
                ai_response_text = f'Research completed for "{question}". No specific search results found, but the question has been processed.'
            
            logger.info(f"✅ [RESEARCH] Step 3/4: Synthesis completed ({len(ai_response_text)} characters)")
        
        # Step 4: Parsing and synthesizing results
        logger.info("📊 [RESEARCH] Step 4/4: Parsing and synthesizing findings...")
        
        # Try to parse JSON from response
        summary = ""
        findings = []
        parsed_sources = []
        
        try:
            # Try to extract JSON from the response
            json_start = ai_response_text.find('{')
            json_end = ai_response_text.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = ai_response_text[json_start:json_end]
                ai_data = json.loads(json_str)
                summary = ai_data.get("summary", "")
                raw_findings = ai_data.get("findings", [])
                parsed_sources = ai_data.get("sources", [])
                
                # Normalize findings - convert dicts to strings
                def normalize_finding(finding):
                    """Convert any finding type to a string."""
                    if isinstance(finding, str):
                        return finding
                    elif isinstance(finding, dict):
                        # If it's a dict, try to extract title and description
                        title = finding.get('title', '')
                        description = finding.get('description', finding.get('body', finding.get('text', '')))
                        if title and description:
                            return f"{title}: {description}"
                        elif title:
                            return title
                        elif description:
                            return description
                        else:
                            return str(finding)
                    elif isinstance(finding, list):
                        return ', '.join(str(f) for f in finding)
                    else:
                        return str(finding)
                
                findings = [normalize_finding(f) for f in raw_findings]
            else:
                # If no JSON found, parse the text directly
                lines = ai_response_text.split('\n')
                summary_lines = []
                finding_lines = []
                
                for line in lines:
                    line = line.strip()
                    if not line:
                        continue
                    if 'summary' in line.lower() or 'finding' in line.lower() or 'key point' in line.lower():
                        if line.startswith('-') or line.startswith('•') or line.startswith('*'):
                            finding_lines.append(line.lstrip('- •*').strip())
                        else:
                            summary_lines.append(line)
                    elif line.startswith('-') or line.startswith('•') or line.startswith('*'):
                        finding_lines.append(line.lstrip('- •*').strip())
                    elif 'http' in line.lower():
                        parsed_sources.append(line)
                
                summary = ' '.join(summary_lines[:3]) if summary_lines else ai_response_text[:300]
                findings = finding_lines[:10] if finding_lines else [ai_response_text[i:i+150] for i in range(0, min(len(ai_response_text), 500), 150)][:5]
        except json.JSONDecodeError:
            # Fallback: parse as plain text
            logger.warning("⚠️ [RESEARCH] Could not parse JSON, using text parsing")
            summary = ai_response_text[:300] + "..." if len(ai_response_text) > 300 else ai_response_text
            sentences = ai_response_text.split('. ')
            findings = [s.strip() + '.' for s in sentences[:5] if len(s.strip()) > 20]
        
        # Combine sources from search and AI
        # Ensure all sources are strings (handle dicts, lists, etc.)
        def normalize_source(source):
            """Convert any source type to a string."""
            if isinstance(source, str):
                return source
            elif isinstance(source, dict):
                # If it's a dict, try to extract URL or convert to string
                return source.get('url', source.get('href', str(source)))
            elif isinstance(source, list):
                return ', '.join(str(s) for s in source)
            else:
                return str(source)
        
        # Normalize all sources to strings
        normalized_sources = [normalize_source(s) for s in sources]
        normalized_parsed_sources = [normalize_source(s) for s in parsed_sources]
        
        # Combine and deduplicate
        all_sources = list(set(normalized_sources + normalized_parsed_sources))[:10]
        if not all_sources:
            all_sources = ["DuckDuckGo Search", "Ollama Analysis"]
        
        # Ensure all findings are strings (final validation)
        findings = [str(f) for f in findings if f]  # Convert to strings and filter out empty values
        
        # Ensure we have findings
        if not findings:
            findings = [f"Research analysis completed for: {question}"]
        
        # Ensure summary exists
        if not summary:
            summary = f'Research findings about "{question}"'
        
        # Ensure summary is a string
        summary = str(summary) if summary else f'Research findings about "{question}"'
        
        research_results = ResearchResponse(
            question=question,
            summary=summary,
            findings=findings[:10],
            sources=all_sources[:10],
            timestamp=datetime.now().isoformat(),
        )
        
        logger.info("✅ [RESEARCH] Step 4/4: Synthesis completed")
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        logger.info(f"⏱️ [RESEARCH] Research completed in {duration:.2f} seconds")
        logger.info(f"📊 [RESEARCH] Generated {len(research_results.findings)} findings")
        logger.info(f"📚 [RESEARCH] Found {len(research_results.sources)} sources")
        logger.info("✅ [RESEARCH] Research process completed successfully")
        
        return research_results
        
    except Exception as e:
        logger.error(f"❌ [RESEARCH] Error during research: {type(e).__name__}: {str(e)}")
        logger.exception("Full error traceback:")
        # Return a fallback response instead of raising
        logger.warning("⚠️ [RESEARCH] Returning fallback response due to error")
        return ResearchResponse(
            question=question,
            summary=f'An error occurred while researching "{question}". Please ensure Ollama is installed and running.',
            findings=[
                f"Error: {str(e)}",
                "Please ensure Ollama is installed: https://ollama.ai",
                f"Install a model with: ollama pull {ollama_model}",
                "Check that Ollama is running and accessible."
            ],
            sources=["Error occurred during research"],
            timestamp=datetime.now().isoformat(),
        )


@app.options("/api/research")
async def research_options():
    """Handle CORS preflight requests explicitly"""
    logger.info("🔀 OPTIONS /api/research - CORS preflight request handled")
    return Response(status_code=200)


@app.post("/api/research", response_model=ResearchResponse)
async def research(request: ResearchRequest):
    """
    Research agent endpoint that processes research questions using OpenDeepResearch.
    Has a configurable timeout (default: 60 seconds for deep research).
    """
    request_start_time = datetime.now()
    
    # Log incoming request
    logger.info("=" * 60)
    logger.info("📥 INCOMING REQUEST")
    logger.info("=" * 60)
    logger.info(f"📍 Endpoint: POST /api/research")
    logger.info(f"🕐 Request received at: {request_start_time.isoformat()}")
    logger.info(f"❓ Question: {request.question}")
    logger.info(f"📏 Question length: {len(request.question)} characters")
    
    # Validation
    logger.info("🔍 [VALIDATION] Validating request...")
    if not request.question or not request.question.strip():
        logger.error("❌ [VALIDATION] Validation failed: Question is required")
        logger.error("❌ [VALIDATION] Question is empty or whitespace only")
        raise ValueError("Question is required")
    
    logger.info("✅ [VALIDATION] Request validation passed")
    
    # Get timeout from environment or use default (60 seconds for deep research)
    timeout_seconds = float(os.getenv("RESEARCH_TIMEOUT", "60.0"))
    logger.info(f"⏱️ [TIMEOUT] Setting {timeout_seconds}-second timeout for research process")

    try:
        logger.info("🚀 [EXECUTION] Starting research execution with timeout wrapper...")
        execution_start = datetime.now()
        
        # Execute research with configurable timeout
        research_results = await asyncio.wait_for(
            perform_research(request.question),
            timeout=timeout_seconds
        )
        
        execution_end = datetime.now()
        execution_duration = (execution_end - execution_start).total_seconds()
        logger.info(f"⏱️ [EXECUTION] Research execution completed in {execution_duration:.2f} seconds")
        
        # Log outgoing response
        logger.info("=" * 60)
        logger.info("📤 OUTGOING RESPONSE")
        logger.info("=" * 60)
        logger.info(f"📍 Endpoint: POST /api/research")
        logger.info(f"🕐 Response sent at: {datetime.now().isoformat()}")
        logger.info(f"⏱️ Total request duration: {(datetime.now() - request_start_time).total_seconds():.2f} seconds")
        logger.info(f"❓ Question: {research_results.question}")
        logger.info(f"📝 Summary: {research_results.summary[:100]}..." if len(research_results.summary) > 100 else f"📝 Summary: {research_results.summary}")
        logger.info(f"📊 Findings Count: {len(research_results.findings)}")
        logger.info(f"📚 Sources Count: {len(research_results.sources)}")
        logger.info(f"🕐 Timestamp: {research_results.timestamp}")
        
        logger.info("\n📋 [RESPONSE] Full Response JSON:")
        logger.info(json.dumps(research_results.model_dump(), indent=2))
        
        logger.info("\n📊 [RESPONSE] Response Summary:")
        for i, finding in enumerate(research_results.findings, 1):
            logger.info(f"   Finding {i}: {finding[:80]}..." if len(finding) > 80 else f"   Finding {i}: {finding}")
        
        for i, source in enumerate(research_results.sources, 1):
            logger.info(f"   Source {i}: {source}")
        
        logger.info("=" * 60)
        logger.info("✅ Request completed successfully")
        logger.info(f"⏱️ Total time: {(datetime.now() - request_start_time).total_seconds():.2f} seconds")
        logger.info("=" * 60 + "\n")

        return research_results
        
    except asyncio.TimeoutError:
        timeout_time = datetime.now()
        total_duration = (timeout_time - request_start_time).total_seconds()
        
        logger.error("=" * 60)
        logger.error("⏱️ TIMEOUT ERROR")
        logger.error("=" * 60)
        logger.error(f"🕐 Timeout occurred at: {timeout_time.isoformat()}")
        logger.error(f"⏱️ Time elapsed before timeout: {total_duration:.2f} seconds")
        logger.error(f"❓ Question that timed out: {request.question}")
        logger.error(f"⚠️ Research took longer than {timeout_seconds} seconds and was terminated")
        logger.error("=" * 60)
        
        # Return a timeout response instead of raising an error
        timeout_response = ResearchResponse(
            question=request.question,
            summary=f'Research timeout: The research for "{request.question}" exceeded the {timeout_seconds}-second time limit.',
            findings=[
                'The research process was interrupted due to timeout.',
                'Please try again with a more specific question.',
            ],
            sources=[],
            timestamp=datetime.now().isoformat(),
        )
        
        logger.info("📤 [TIMEOUT] Returning timeout response to client")
        logger.info(f"📋 [TIMEOUT] Response: {json.dumps(timeout_response.model_dump(), indent=2)}")
        logger.info("=" * 60 + "\n")
        
        return timeout_response
    
    except Exception as e:
        error_time = datetime.now()
        total_duration = (error_time - request_start_time).total_seconds()
        
        logger.error("=" * 60)
        logger.error("❌ UNEXPECTED ERROR")
        logger.error("=" * 60)
        logger.error(f"🕐 Error occurred at: {error_time.isoformat()}")
        logger.error(f"⏱️ Time elapsed before error: {total_duration:.2f} seconds")
        logger.error(f"❓ Question: {request.question}")
        logger.error(f"💥 Error type: {type(e).__name__}")
        logger.error(f"💥 Error message: {str(e)}")
        logger.error(f"💥 Error details: {repr(e)}")
        logger.error("=" * 60)
        raise


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
