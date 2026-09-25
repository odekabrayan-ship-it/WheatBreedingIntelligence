from fastapi import FastAPI

app = FastAPI(
    title="WheatBreeding Intelligence API",
    description="Scientific and breeding decision-support backend for WheatBI",
    version="0.1.0",
)


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
