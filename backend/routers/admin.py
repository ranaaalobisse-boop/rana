from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional
from decimal import Decimal
import os
import shutil

from database import get_db
from models import (
    User, Jeweler, Product, ProductImage, Category, ProductCategory,
    Order, OrderStatusEnum, PaymentMethod, DesignRequest, DesignRequestStatusEnum
)
from schemas import (
    ProductCreate, ProductResponse, CategoryCreate, CategoryResponse,
    PaymentMethodCreate, PaymentMethodResponse, JewelerCreate, JewelerResponse,
    OrderResponse, OrderStatusUpdate, DesignRequestResponse, DesignRequestUpdate
)
from routers.auth import get_current_user

router = APIRouter(prefix="/api/admin", tags=["Admin"])

# Helper function to check if user is admin
async def get_admin_user(current_user: User = Depends(get_current_user)):
    # For simplicity, we'll check if user ID is in a list of admin IDs
    # In production, you'd have an is_admin flag on the User model
    admin_ids = [1, 2, 3]  # First 3 users are admins
    if current_user.id not in admin_ids:
        raise HTTPException(status_code=403, detail="Not authorized. Admin access required.")
    return current_user

# Jeweler Management
@router.get("/jewelers", response_model=List[JewelerResponse])
def get_jewelers(
    skip: int = 0,
    limit: int = 100,
    admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Get all jewelers (admin only)"""
    jewelers = db.query(Jeweler).offset(skip).limit(limit).all()
    return jewelers

@router.post("/jewelers", response_model=JewelerResponse)
def create_jeweler(
    jeweler: JewelerCreate,
    admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Create a new jeweler (admin only)"""
    db_jeweler = Jeweler(**jeweler.model_dump())
    db.add(db_jeweler)
    db.commit()
    db.refresh(db_jeweler)
    return db_jeweler

@router.put("/jewelers/{jeweler_id}", response_model=JewelerResponse)
def update_jeweler(
    jeweler_id: int,
    jeweler: JewelerCreate,
    admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Update a jeweler (admin only)"""
    db_jeweler = db.query(Jeweler).filter(Jeweler.id == jeweler_id).first()
    if not db_jeweler:
        raise HTTPException(status_code=404, detail="Jeweler not found")
    
    for key, value in jeweler.model_dump().items():
        setattr(db_jeweler, key, value)
    
    db.commit()
    db.refresh(db_jeweler)
    return db_jeweler

@router.delete("/jewelers/{jeweler_id}")
def delete_jeweler(
    jeweler_id: int,
    admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Delete a jeweler (admin only)"""
    db_jeweler = db.query(Jeweler).filter(Jeweler.id == jeweler_id).first()
    if not db_jeweler:
        raise HTTPException(status_code=404, detail="Jeweler not found")
    
    db.delete(db_jeweler)
    db.commit()
    return {"message": "Jeweler deleted successfully"}

# Category Management
@router.get("/categories", response_model=List[CategoryResponse])
def get_all_categories(
    admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Get all categories (admin only)"""
    categories = db.query(Category).all()
    return categories

@router.post("/categories", response_model=CategoryResponse)
def create_category(
    category: CategoryCreate,
    admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Create a new category (admin only)"""
    db_category = Category(**category.model_dump())
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category

@router.put("/categories/{category_id}", response_model=CategoryResponse)
def update_category(
    category_id: int,
    category: CategoryCreate,
    admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Update a category (admin only)"""
    db_category = db.query(Category).filter(Category.id == category_id).first()
    if not db_category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    for key, value in category.model_dump().items():
        setattr(db_category, key, value)
    
    db.commit()
    db.refresh(db_category)
    return db_category

@router.delete("/categories/{category_id}")
def delete_category(
    category_id: int,
    admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Delete a category (admin only)"""
    db_category = db.query(Category).filter(Category.id == category_id).first()
    if not db_category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    db.delete(db_category)
    db.commit()
    return {"message": "Category deleted successfully"}

# Product Management
@router.post("/products", response_model=ProductResponse)
def create_product(
    product: ProductCreate,
    admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Create a new product (admin only)"""
    # Check if jeweler exists
    jeweler = db.query(Jeweler).filter(Jeweler.id == product.jeweler_id).first()
    if not jeweler:
        raise HTTPException(status_code=404, detail="Jeweler not found")
    
    # Create product
    product_data = product.model_dump(exclude={'category_ids'})
    db_product = Product(**product_data)
    db.add(db_product)
    db.flush()
    
    # Add categories
    if product.category_ids:
        for cat_id in product.category_ids:
            category = db.query(Category).filter(Category.id == cat_id).first()
            if category:
                product_category = ProductCategory(
                    product_id=db_product.id,
                    category_id=cat_id
                )
                db.add(product_category)
    
    db.commit()
    db.refresh(db_product)
    return db_product

@router.put("/products/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: int,
    product: ProductCreate,
    admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Update a product (admin only)"""
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Update basic fields
    product_data = product.model_dump(exclude={'category_ids'})
    for key, value in product_data.items():
        setattr(db_product, key, value)
    
    # Update categories
    if product.category_ids is not None:
        # Remove existing categories
        db.query(ProductCategory).filter(ProductCategory.product_id == product_id).delete()
        
        # Add new categories
        for cat_id in product.category_ids:
            category = db.query(Category).filter(Category.id == cat_id).first()
            if category:
                product_category = ProductCategory(
                    product_id=product_id,
                    category_id=cat_id
                )
                db.add(product_category)
    
    db.commit()
    db.refresh(db_product)
    return db_product

@router.delete("/products/{product_id}")
def delete_product(
    product_id: int,
    admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Delete a product (admin only)"""
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    db.delete(db_product)
    db.commit()
    return {"message": "Product deleted successfully"}

@router.post("/products/{product_id}/images")
def upload_product_image(
    product_id: int,
    file: UploadFile = File(...),
    display_order: int = 0,
    admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Upload product image (admin only)"""
    # Check if product exists
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Save file
    upload_dir = "uploads/products"
    os.makedirs(upload_dir, exist_ok=True)
    
    file_extension = os.path.splitext(file.filename)[1]
    filename = f"product_{product_id}_{display_order}{file_extension}"
    file_path = os.path.join(upload_dir, filename)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Save to database
    product_image = ProductImage(
        product_id=product_id,
        image_path=file_path,
        display_order=display_order
    )
    db.add(product_image)
    db.commit()
    db.refresh(product_image)
    
    return {
        "message": "Image uploaded successfully",
        "image_id": product_image.id,
        "path": file_path
    }

# Payment Methods Management
@router.get("/payment-methods", response_model=List[PaymentMethodResponse])
def get_payment_methods(
    admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Get all payment methods (admin only)"""
    methods = db.query(PaymentMethod).all()
    return methods

@router.post("/payment-methods", response_model=PaymentMethodResponse)
def create_payment_method(
    method: PaymentMethodCreate,
    admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Create a new payment method (admin only)"""
    db_method = PaymentMethod(**method.model_dump())
    db.add(db_method)
    db.commit()
    db.refresh(db_method)
    return db_method

@router.put("/payment-methods/{method_id}", response_model=PaymentMethodResponse)
def update_payment_method(
    method_id: int,
    method: PaymentMethodCreate,
    admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Update a payment method (admin only)"""
    db_method = db.query(PaymentMethod).filter(PaymentMethod.id == method_id).first()
    if not db_method:
        raise HTTPException(status_code=404, detail="Payment method not found")
    
    for key, value in method.model_dump().items():
        setattr(db_method, key, value)
    
    db.commit()
    db.refresh(db_method)
    return db_method

@router.delete("/payment-methods/{method_id}")
def delete_payment_method(
    method_id: int,
    admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Delete a payment method (admin only)"""
    db_method = db.query(PaymentMethod).filter(PaymentMethod.id == method_id).first()
    if not db_method:
        raise HTTPException(status_code=404, detail="Payment method not found")
    
    db.delete(db_method)
    db.commit()
    return {"message": "Payment method deleted successfully"}

# Order Management
@router.get("/orders", response_model=List[OrderResponse])
def get_all_orders(
    status: Optional[OrderStatusEnum] = None,
    admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Get all orders with optional status filter (admin only)"""
    query = db.query(Order)
    if status:
        query = query.filter(Order.status == status)
    orders = query.order_by(Order.order_date.desc()).all()
    return orders

@router.put("/orders/{order_id}/status", response_model=OrderResponse)
def update_order_status(
    order_id: int,
    status_update: OrderStatusUpdate,
    admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Update order status (admin only)"""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    order.status = status_update.status
    db.commit()
    db.refresh(order)
    return order

# Design Requests Management
@router.get("/design-requests", response_model=List[DesignRequestResponse])
def get_design_requests(
    status: Optional[DesignRequestStatusEnum] = None,
    admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Get all design requests with optional status filter (admin only)"""
    query = db.query(DesignRequest)
    if status:
        query = query.filter(DesignRequest.status == status)
    requests = query.order_by(DesignRequest.request_date.desc()).all()
    return requests

@router.put("/design-requests/{request_id}", response_model=DesignRequestResponse)
def update_design_request(
    request_id: int,
    update_data: DesignRequestUpdate,
    admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Update design request status and price offer (admin only)"""
    design_request = db.query(DesignRequest).filter(DesignRequest.id == request_id).first()
    if not design_request:
        raise HTTPException(status_code=404, detail="Design request not found")
    
    if update_data.status:
        design_request.status = update_data.status
    if update_data.jeweler_price_offer is not None:
        design_request.jeweler_price_offer = update_data.jeweler_price_offer
    
    db.commit()
    db.refresh(design_request)
    return design_request
