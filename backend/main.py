from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from dataset_versions import router as dataset_versions_router
from datasets import router as datasets_router
from projects import router as projects_router


app = FastAPI(
    title="WheatBreeding Intelligence API",
    description="Scientific and breeding decision-support backend for WheatBI",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(projects_router)
app.include_router(datasets_router)
app.include_router(dataset_versions_router)


@app.get("/")
def root():
    return {
        "product": "WheatBreeding Intelligence",
        "status": "operational",
        "version": "0.1.0",
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }
