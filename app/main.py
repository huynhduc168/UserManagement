from fastapi import FastAPI
import uvicorn
from app.api.v1.api_route import api_router
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
app = FastAPI(title="User Management API")

app.include_router(api_router, prefix="/api/v1")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files for face_uploads
app.mount("/face_uploads", StaticFiles(directory="face_uploads"), name="face_uploads")


# if __name__ == "__main__":
#     uvicorn.run(app, host="127.0.0.1", port=8002)