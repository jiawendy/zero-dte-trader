from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from services.scheduler import start_scheduler, get_latest_analysis_data, job_analyze_market
import contextlib

@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    start_scheduler()
    yield

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/status")
def get_status():
    return {"status": "running"}

@app.get("/api/latest")
def get_latest_analysis():
    return get_latest_analysis_data()

@app.post("/api/analyze")
def trigger_analysis():
    job_analyze_market()
    return {"message": "Analysis triggered", "result": get_latest_analysis_data()}

@app.post("/api/share")
def share_analysis():
    from services.google_docs_service import append_or_create_analysis_doc
    import datetime
    
    data = get_latest_analysis_data()
    if not data or not data.get("text"):
        return {"error": "No analysis available to share"}
        
    try:
        # Title is now just the date
        today_str = datetime.date.today().strftime("%Y-%m-%d")
        title = f"0DTE Analysis - {today_str}"
        
        # Add timestamp to content
        timestamp = data.get('timestamp', 'Unknown Time')
        content = f"Analysis Time: {timestamp}\n\n{data.get('text')}"
        
        doc_url = append_or_create_analysis_doc(title, content)
        return {"url": doc_url}
    except Exception as e:
        return {"error": str(e)}

@app.post("/api/save_local")
def save_local_analysis():
    from services.storage_service import save_analysis_to_disk
    
    data = get_latest_analysis_data()
    filepath, error = save_analysis_to_disk(data)
    
    if error:
        return {"error": error}
        
    return {"message": f"Saved to {filepath}", "path": filepath}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
