from fastapi import FastAPI
from app.routers import users, products

app = FastAPI()

# Root Endpoint
@app.get('/')
def root():
    return {"message": "Working"}

app = FastAPI(title="Boilerplate", version="1.0.0", docs_url="/docs", redoc_url="/redoc")

app.include_router(users.router)
app.include_router(products.router)




















