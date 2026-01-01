import uvicorn
from fastapi import FastAPI

# Always import starting from the project root
from app.backend.routes import predict, health 

app = FastAPI(title="ASHRAE MLOps API")

app.include_router(predict.router)
app.include_router(health.router)

@app.get("/")
def root():
    return {"message": "API is running"}

if __name__ == "__main__":
    # Use the dot notation so uvicorn can find the app from the root
    uvicorn.run("app.backend.server:app", host="0.0.0.0", port=8000, reload=True)