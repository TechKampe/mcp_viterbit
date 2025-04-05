from fastapi import FastAPI
from viterbit import full_summary, historical_comparison

app = FastAPI()

@app.get("/")
async def root():
    return {"status": "Enhanced MCP Viterbit server running"}

@app.get("/candidate-summary")
async def candidate_summary(days: int = 7):
    summary = full_summary(period_days=days)
    return summary

@app.get("/historical-comparison/{stage}")
async def comparison(stage: str, days: int = 30):
    comparison_result = historical_comparison(stage, period_days=days)
    return comparison_result
