from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
import os
from dotenv import load_dotenv

from database import engine, Base
from models import (
    User, Jeweler, PaymentMethod, Category, Product, ProductImage, 
    ProductCategory, Cart, CartItem, Order, OrderItem, 
    UserGeneratedDesign, DesignRequest
)
from routers.auth import router as auth_router
from routers.products import router as products_router
from routers.cart import router as cart_router, orders_router
from routers.admin import router as admin_router
from routers.ai_design import router as ai_design_router

load_dotenv()

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title="Luxury Jewelry API",
    description="Backend API for Jewelry E-commerce and AI Design Platform",
    version="1.0.0"
)

# Configure CORS for frontend compatibility
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create directories for uploads
os.makedirs("static/generated_designs", exist_ok=True)
os.makedirs("uploads/products", exist_ok=True)
os.makedirs("uploads/qr_codes", exist_ok=True)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Include routers
app.include_router(auth_router)
app.include_router(products_router)
app.include_router(cart_router)
app.include_router(orders_router)
app.include_router(admin_router)
app.include_router(ai_design_router)

@app.get("/")
def root():
    return {
        "message": "Welcome to Luxury Jewelry API",
        "docs": "/docs",
        "version": "1.0.0"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "Luxury Jewelry API"}

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"message": f"Internal server error: {str(exc)}"}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
