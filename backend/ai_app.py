from fastapi import FastAPI
import logging

from app.api.v1 import ai as ai_router_module

app = FastAPI(title="ProctoFlex AI - AI Service")

app.include_router(ai_router_module.router, prefix="/api/ai")


@app.get('/health')
async def health():
    return {"status": "healthy", "service": "ai-service"}


if __name__ == '__main__':
    import uvicorn
    uvicorn.run('ai_app:app', host='0.0.0.0', port=8001, log_level='info')
