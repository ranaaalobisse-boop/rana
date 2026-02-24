from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional
from decimal import Decimal

from database import get_db
from models import Product, ProductImage, ProductCategory, Category, Jeweler
from schemas import (
    ProductCreate, ProductResponse, ProductDetailResponse, 
    ProductFilter, CategoryResponse
)

router = APIRouter(prefix="/api/products", tags=["Products"])

@router.get("/", response_model=List[ProductResponse])
def get_products(
    category_id: Optional[int] = Query(None),
    material: Optional[str] = Query(None),
    min_price: Optional[Decimal] = Query(None),
    max_price: Optional[Decimal] = Query(None),
    search: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Get all products with optional filters
    """
    query = db.query(Product)
    
    # Apply filters
    if category_id:
        query = query.join(ProductCategory).filter(ProductCategory.category_id == category_id)
    
    if material:
        query = query.filter(Product.material.ilike(f"%{material}%"))
    
    if min_price is not None:
        query = query.filter(Product.price >= min_price)
    
    if max_price is not None:
        query = query.filter(Product.price <= max_price)
    
    if search:
        query = query.filter(Product.name.ilike(f"%{search}%"))
    
    products = query.offset(skip).limit(limit).all()
    return products

@router.get("/{product_id}", response_model=ProductDetailResponse)
def get_product(product_id: int, db: Session = Depends(get_db)):
    """
    Get a single product with all details including images and jeweler info
    """
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@router.get("/categories/all", response_model=List[CategoryResponse])
def get_categories(
    parent_id: Optional[int] = Query(None),
    db: Session = Depends(get_db)
):
    """
    Get all categories, optionally filtered by parent
    """
    query = db.query(Category)
    if parent_id is not None:
        query = query.filter(Category.parent_id == parent_id)
    else:
        query = query.filter(Category.parent_id == None)
    
    categories = query.all()
    return categories

@router.get("/featured/list", response_model=List[ProductResponse])
def get_featured_products(
    limit: int = Query(8, ge=1, le=20),
    db: Session = Depends(get_db)
):
    """
    Get featured products (newest products)
    """
    products = db.query(Product).order_by(Product.id.desc()).limit(limit).all()
    return products
