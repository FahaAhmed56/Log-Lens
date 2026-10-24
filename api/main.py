from functools import lru_cache
from pathlib import Path
from typing import List
import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from loglens.engine import analyze_logs, load_model

app=FastAPI(title="LogLens AI API",version="1.0.0")
class Event(BaseModel):
    timestamp: str
    level: str
    service: str
    status: int = Field(ge=100,le=599)
    duration_ms: float = Field(ge=0)
    bytes_sent: float = Field(ge=0)
    message: str
class AnalyzeRequest(BaseModel):
    events: List[Event] = Field(min_length=1,max_length=500)
@lru_cache(maxsize=1)
def model():
    return load_model('models/isolation_forest.joblib')
@app.get('/health')
def health():
    return {'status':'ok'}
@app.post('/analyze')
def analyze(payload:AnalyzeRequest):
    try:
        df=pd.DataFrame([event.model_dump() for event in payload.events])
        result=analyze_logs(df,model())
        return {'total':len(result),'anomalies':int(result.is_anomaly.sum()),'events':result.to_dict(orient='records')}
    except (ValueError,FileNotFoundError) as ex:
        raise HTTPException(status_code=400,detail=str(ex)) from ex
