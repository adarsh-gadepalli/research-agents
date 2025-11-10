from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from pydantic import BaseModel
from typing import List
import asyncio
import logging
from datetime import datetime
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

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
    Perform the actual research work.
    Returns placeholder results immediately without any delay.
    """
    start_time = datetime.now()
    logger.info("🔍 [RESEARCH] Starting research process...")
    logger.info(f"🔍 [RESEARCH] Question received: {question}")
    logger.info(f"🔍 [RESEARCH] Start time: {start_time.isoformat()}")
    
    # Step 1: Initialization
    logger.info("📝 [RESEARCH] Step 1/4: Initializing research agent...")
    logger.info("✅ [RESEARCH] Step 1/4: Research agent initialized")
    
    # Step 2: Searching
    logger.info("🔎 [RESEARCH] Step 2/4: Searching databases and sources...")
    logger.info("✅ [RESEARCH] Step 2/4: Search completed - Found relevant sources")
    
    # Step 3: Analyzing
    logger.info("🧠 [RESEARCH] Step 3/4: Analyzing information...")
    logger.info("✅ [RESEARCH] Step 3/4: Analysis completed")
    
    # Step 4: Synthesizing
    logger.info("📊 [RESEARCH] Step 4/4: Synthesizing findings...")
    logger.info("✅ [RESEARCH] Step 4/4: Synthesis completed")
    
    # Simulate research agent processing
    # In a real implementation, this would:
    # 1. Search the web or databases
    # 2. Analyze information using AI/ML models
    # 3. Synthesize findings
    # 4. Return structured results

    logger.info("📦 [RESEARCH] Preparing research results...")
    
    # Mock research results - returned immediately
    research_results = ResearchResponse(
        question=question,
        summary=f'Based on research about "{question}", here are the key findings...',
        findings=[
            f'Finding 1: This is a simulated research result related to "{question}".',
            f'Finding 2: Additional information and insights about the topic.',
            f'Finding 3: Further analysis and conclusions.',
        ],
        sources=[
            'Source 1: Research Database',
            'Source 2: Academic Papers',
            'Source 3: Expert Analysis',
        ],
        timestamp=datetime.now().isoformat(),
    )
    
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    logger.info(f"⏱️ [RESEARCH] Research completed in {duration:.4f} seconds (instant)")
    logger.info(f"📊 [RESEARCH] Generated {len(research_results.findings)} findings")
    logger.info(f"📚 [RESEARCH] Found {len(research_results.sources)} sources")
    logger.info("✅ [RESEARCH] Research process completed successfully")

    return research_results


@app.options("/api/research")
async def research_options():
    """Handle CORS preflight requests explicitly"""
    logger.info("🔀 OPTIONS /api/research - CORS preflight request handled")
    return Response(status_code=200)


@app.post("/api/research", response_model=ResearchResponse)
async def research(request: ResearchRequest):
    """
    Research agent endpoint that processes research questions.
    Has a maximum timeout of 5 seconds.
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
    logger.info(f"⏱️ [TIMEOUT] Setting 5-second timeout for research process")

    try:
        logger.info("🚀 [EXECUTION] Starting research execution with timeout wrapper...")
        execution_start = datetime.now()
        
        # Execute research with a 5-second timeout
        research_results = await asyncio.wait_for(
            perform_research(request.question),
            timeout=5.0
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
        logger.error("⚠️ Research took longer than 5 seconds and was terminated")
        logger.error("=" * 60)
        
        # Return a timeout response instead of raising an error
        timeout_response = ResearchResponse(
            question=request.question,
            summary=f'Research timeout: The research for "{request.question}" exceeded the 5-second time limit.',
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
