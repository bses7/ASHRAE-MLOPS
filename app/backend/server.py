# app/backend/server.py
from fastapi import FastAPI
import uvicorn

# Use absolute imports from the project root
from app.backend.routes import predict, health 

app = FastAPI(title="ASHRAE MLOps API")

app.include_router(predict.router)
app.include_router(health.router)

@app.get("/")
def root():
    return {"message": "API is running"}

if __name__ == "__main__":
    # Use the string import path so reload works correctly
    uvicorn.run("app.backend.server:app", host="0.0.0.0", port=8000, reload=True)