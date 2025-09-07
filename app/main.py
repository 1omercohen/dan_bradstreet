import logging
from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.database import create_tables
from app.api.stock import router as stocks_router
from app.middleware import ErrorHandlingMiddleware

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_tables()
    yield
    pass

app = FastAPI(
    title="Stocks REST API",
    description="API for retrieving and managing stock data",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(ErrorHandlingMiddleware)

app.include_router(stocks_router)

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "stocks-api"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)