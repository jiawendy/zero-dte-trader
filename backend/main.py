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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
