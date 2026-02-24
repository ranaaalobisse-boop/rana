from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from decimal import Decimal

from database import get_db
from models import Cart, CartItem, Product, Order, OrderItem, OrderStatusEnum, PaymentMethod
from schemas import (
    CartItemCreate, CartItemResponse, CartResponse, 
    OrderCreate, OrderResponse, OrderStatusUpdate, PaymentMethodResponse
)
from routers.auth import get_current_user
from models import User

router = APIRouter(prefix="/api/cart", tags=["Cart"])

def get_or_create_cart(db: Session, user_id: int) -> Cart:
    """Get existing cart or create new one for user"""
    cart = db.query(Cart).filter(Cart.user_id == user_id).first()
    if not cart:
        cart = Cart(user_id=user_id)
        db.add(cart)
        db.commit()
        db.refresh(cart)
    return cart

def calculate_cart_totals(cart: Cart) -> tuple:
    """Calculate total items and amount in cart"""
    total_items = 0
    total_amount = Decimal('0')
    
    for item in cart.items:
        total_items += item.quantity
        if item.product:
            total_amount += item.product.price * item.quantity
    
    return total_items, total_amount

@router.get("/", response_model=CartResponse)
def get_cart(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Get current user's cart with all items
    """
    cart = get_or_create_cart(db, current_user.id)
    total_items, total_amount = calculate_cart_totals(cart)
    
    response = CartResponse(
        id=cart.id,
        user_id=cart.user_id,
        items=cart.items,
        updated_at=cart.updated_at,
        total_items=total_items,
        total_amount=total_amount
    )
    return response

@router.post("/items", response_model=CartResponse)
def add_to_cart(
    item: CartItemCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Add a product to cart
    """
    # Check if product exists and has stock
    product = db.query(Product).filter(Product.id == item.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    if product.stock_quantity < item.quantity:
        raise HTTPException(status_code=400, detail="Insufficient stock")
    
    cart = get_or_create_cart(db, current_user.id)
    
    # Check if item already in cart
    cart_item = db.query(CartItem).filter(
        CartItem.cart_id == cart.id,
        CartItem.product_id == item.product_id
    ).first()
    
    if cart_item:
        # Update quantity
        cart_item.quantity += item.quantity
    else:
        # Add new item
        cart_item = CartItem(
            cart_id=cart.id,
            product_id=item.product_id,
            quantity=item.quantity
        )
        db.add(cart_item)
    
    db.commit()
    db.refresh(cart)
    
    total_items, total_amount = calculate_cart_totals(cart)
    return CartResponse(
        id=cart.id,
        user_id=cart.user_id,
        items=cart.items,
        updated_at=cart.updated_at,
        total_items=total_items,
        total_amount=total_amount
    )

@router.put("/items/{item_id}", response_model=CartResponse)
def update_cart_item(
    item_id: int,
    quantity: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update cart item quantity
    """
    if quantity < 1:
        raise HTTPException(status_code=400, detail="Quantity must be at least 1")
    
    cart = get_or_create_cart(db, current_user.id)
    
    cart_item = db.query(CartItem).filter(
        CartItem.id == item_id,
        CartItem.cart_id == cart.id
    ).first()
    
    if not cart_item:
        raise HTTPException(status_code=404, detail="Cart item not found")
    
    # Check stock
    if cart_item.product and cart_item.product.stock_quantity < quantity:
        raise HTTPException(status_code=400, detail="Insufficient stock")
    
    cart_item.quantity = quantity
    db.commit()
    db.refresh(cart)
    
    total_items, total_amount = calculate_cart_totals(cart)
    return CartResponse(
        id=cart.id,
        user_id=cart.user_id,
        items=cart.items,
        updated_at=cart.updated_at,
        total_items=total_items,
        total_amount=total_amount
    )

@router.delete("/items/{item_id}", response_model=CartResponse)
def remove_from_cart(
    item_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Remove an item from cart
    """
    cart = get_or_create_cart(db, current_user.id)
    
    cart_item = db.query(CartItem).filter(
        CartItem.id == item_id,
        CartItem.cart_id == cart.id
    ).first()
    
    if not cart_item:
        raise HTTPException(status_code=404, detail="Cart item not found")
    
    db.delete(cart_item)
    db.commit()
    db.refresh(cart)
    
    total_items, total_amount = calculate_cart_totals(cart)
    return CartResponse(
        id=cart.id,
        user_id=cart.user_id,
        items=cart.items,
        updated_at=cart.updated_at,
        total_items=total_items,
        total_amount=total_amount
    )

@router.delete("/", response_model=dict)
def clear_cart(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Clear all items from cart
    """
    cart = db.query(Cart).filter(Cart.user_id == current_user.id).first()
    if cart:
        for item in cart.items:
            db.delete(item)
        db.commit()
    
    return {"message": "Cart cleared successfully"}

# Orders Router
orders_router = APIRouter(prefix="/api/orders", tags=["Orders"])

@orders_router.get("/payment-methods", response_model=List[PaymentMethodResponse])
def get_payment_methods(db: Session = Depends(get_db)):
    """
    Get all active payment methods
    """
    methods = db.query(PaymentMethod).filter(PaymentMethod.is_active == True).all()
    return methods

@orders_router.post("/checkout", response_model=OrderResponse)
def checkout(
    order_data: OrderCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Convert cart to order (checkout)
    """
    # Get user's cart
    cart = db.query(Cart).filter(Cart.user_id == current_user.id).first()
    if not cart or not cart.items:
        raise HTTPException(status_code=400, detail="Cart is empty")
    
    # Calculate total
    total_amount = Decimal('0')
    for item in cart.items:
        if not item.product:
            raise HTTPException(status_code=400, detail="Invalid product in cart")
        total_amount += item.product.price * item.quantity
    
    # Validate payment method
    if order_data.payment_method_id:
        payment_method = db.query(PaymentMethod).filter(
            PaymentMethod.id == order_data.payment_method_id,
            PaymentMethod.is_active == True
        ).first()
        if not payment_method:
            raise HTTPException(status_code=400, detail="Invalid payment method")
    
    # Create order
    order = Order(
        user_id=current_user.id,
        payment_method_id=order_data.payment_method_id,
        total_amount=total_amount,
        shipping_address=order_data.shipping_address,
        status=OrderStatusEnum.pending
    )
    db.add(order)
    db.flush()  # Get order ID
    
    # Create order items
    for cart_item in cart.items:
        order_item = OrderItem(
            order_id=order.id,
            product_id=cart_item.product_id,
            quantity=cart_item.quantity,
            unit_price=cart_item.product.price,
            subtotal=cart_item.product.price * cart_item.quantity
        )
        db.add(order_item)
        
        # Reduce stock
        cart_item.product.stock_quantity -= cart_item.quantity
    
    # Clear cart
    for item in cart.items:
        db.delete(item)
    
    db.commit()
    db.refresh(order)
    
    return order

@orders_router.get("/", response_model=List[OrderResponse])
def get_user_orders(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get current user's orders
    """
    orders = db.query(Order).filter(Order.user_id == current_user.id).order_by(Order.order_date.desc()).all()
    return orders

@orders_router.get("/{order_id}", response_model=OrderResponse)
def get_order(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get order details by ID
    """
    order = db.query(Order).filter(
        Order.id == order_id,
        Order.user_id == current_user.id
    ).first()
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    return order
