from fastapi import FastAPI
import uvicorn
from app.api.v1.api_route import api_router

app = FastAPI(title="User Management API")

app.include_router(api_router, prefix="/api/v1")

# if __name__ == "__main__":
#     uvicorn.run(app, host="127.0.0.1", port=8002)