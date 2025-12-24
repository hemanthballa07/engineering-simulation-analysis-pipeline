from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
import logging
import time
import uuid

from api.db import list_runs_summary
from api.storage import get_run_metrics, get_run_insights

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("api")

app = FastAPI(
    title="Engineering Simulation Platform",
    description="API for accessing validated simulation artifacts and AI insights.",
    version="1.0.0"
)

# Middleware for observability
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    request_id = str(uuid.uuid4())
    start_time = time.time()
    
    response = await call_next(request)
    
    process_time = (time.time() - start_time) * 1000
    
    logger.info(
        f"Request: {request.method} {request.url.path} | "
        f"Status: {response.status_code} | "
        f"Latency: {process_time:.2f}ms | "
        f"ID: {request_id}"
    )
    
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Process-Time"] = str(process_time)
    return response

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "simulation-platform"}

@app.get("/runs")
def list_runs():
    """List all available runs from the database."""
    runs = list_runs_summary()
    return {"runs": runs, "count": len(runs)}

@app.get("/runs/{run_id}/metrics")
def get_metrics(run_id: str):
    """Get validated metrics for a specific run."""
    payload, error = get_run_metrics(run_id)
    
    if error:
        # Distinguish between not found and invalid
        if "not found" in error.lower():
            raise HTTPException(status_code=404, detail=error)
        else:
            raise HTTPException(status_code=422, detail=error)
            
    return payload

@app.get("/runs/{run_id}/insights")
def get_insights(run_id: str):
    """Get validated AI insights."""
    data, md, error = get_run_insights(run_id)
    
    if error:
        if "not found" in error.lower():
            raise HTTPException(status_code=404, detail=error)
        else:
            raise HTTPException(status_code=422, detail=error)
            
    return {
        "json": data,
        "markdown": md
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
