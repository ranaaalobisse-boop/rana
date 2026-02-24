import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, Text, DateTime, ForeignKey, Enum, JSON, DECIMAL
from sqlalchemy.orm import relationship
from database import Base

class GenderEnum(enum.Enum):
    male = "male"
    female = "female"
    other = "other"

class OrderStatusEnum(enum.Enum):
    pending = "pending"
    confirmed = "confirmed"
    processing = "processing"
    shipped = "shipped"
    delivered = "delivered"
    cancelled = "cancelled"

class DesignRequestStatusEnum(enum.Enum):
    pending = "pending"
    reviewed = "reviewed"
    quoted = "quoted"
    accepted = "accepted"
    rejected = "rejected"
    in_progress = "in_progress"
    completed = "completed"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    password = Column(String(255), nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    first_name = Column(String(50), nullable=True)
    last_name = Column(String(50), nullable=True)
    phone = Column(String(20), nullable=True)
    dob = Column(DateTime, nullable=True)
    gender = Column(Enum(GenderEnum), nullable=True)
    address = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    cart = relationship("Cart", back_populates="user", uselist=False)
    orders = relationship("Order", back_populates="user")
    designs = relationship("UserGeneratedDesign", back_populates="user")
    design_requests = relationship("DesignRequest", back_populates="user")

class Jeweler(Base):
    __tablename__ = "jewelers"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    shop_name = Column(String(100), nullable=True)
    bio = Column(Text, nullable=True)
    address = Column(Text, nullable=True)
    phone = Column(String(20), nullable=True)
    email = Column(String(100), nullable=True)
    rating = Column(DECIMAL(3, 2), default=0.00)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    products = relationship("Product", back_populates="jeweler")
    design_requests = relationship("DesignRequest", back_populates="jeweler")

class PaymentMethod(Base):
    __tablename__ = "payment_methods"
    
    id = Column(Integer, primary_key=True, index=True)
    method_name = Column(String(50), nullable=False)
    qr_code_image = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    notes = Column(Text, nullable=True)
    
    orders = relationship("Order", back_populates="payment_method")

class Category(Base):
    __tablename__ = "categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    parent_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    
    parent = relationship("Category", remote_side=[id], backref="subcategories")
    product_categories = relationship("ProductCategory", back_populates="category")

class Product(Base):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    jeweler_id = Column(Integer, ForeignKey("jewelers.id"), nullable=False)
    name = Column(String(200), nullable=False)
    material = Column(String(50), nullable=True)
    karat = Column(String(10), nullable=True)
    weight = Column(DECIMAL(10, 3), nullable=True)
    price = Column(DECIMAL(12, 2), nullable=False)
    stock_quantity = Column(Integer, default=0)
    description = Column(Text, nullable=True)
    image_path = Column(String(255), nullable=True)
    
    jeweler = relationship("Jeweler", back_populates="products")
    images = relationship("ProductImage", back_populates="product", order_by="ProductImage.display_order")
    product_categories = relationship("ProductCategory", back_populates="product")
    cart_items = relationship("CartItem", back_populates="product")
    order_items = relationship("OrderItem", back_populates="product")

class ProductImage(Base):
    __tablename__ = "product_images"
    
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    image_path = Column(String(255), nullable=False)
    display_order = Column(Integer, default=0)
    
    product = relationship("Product", back_populates="images")

class ProductCategory(Base):
    __tablename__ = "product_categories"
    
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    
    product = relationship("Product", back_populates="product_categories")
    category = relationship("Category", back_populates="product_categories")

class Cart(Base):
    __tablename__ = "carts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = relationship("User", back_populates="cart")
    items = relationship("CartItem", back_populates="cart", cascade="all, delete-orphan")

class CartItem(Base):
    __tablename__ = "cart_items"
    
    id = Column(Integer, primary_key=True, index=True)
    cart_id = Column(Integer, ForeignKey("carts.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, default=1)
    
    cart = relationship("Cart", back_populates="items")
    product = relationship("Product", back_populates="cart_items")

class Order(Base):
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    payment_method_id = Column(Integer, ForeignKey("payment_methods.id"), nullable=True)
    order_date = Column(DateTime, default=datetime.utcnow)
    status = Column(Enum(OrderStatusEnum), default=OrderStatusEnum.pending)
    total_amount = Column(DECIMAL(12, 2), nullable=False)
    shipping_address = Column(Text, nullable=True)
    transfer_receipt = Column(String(255), nullable=True)
    
    user = relationship("User", back_populates="orders")
    payment_method = relationship("PaymentMethod", back_populates="orders")
    items = relationship("OrderItem", back_populates="order")

class OrderItem(Base):
    __tablename__ = "order_items"
    
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(DECIMAL(12, 2), nullable=False)
    subtotal = Column(DECIMAL(12, 2), nullable=False)
    
    order = relationship("Order", back_populates="items")
    product = relationship("Product", back_populates="order_items")

class UserGeneratedDesign(Base):
    __tablename__ = "user_generated_designs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    selected_options = Column(JSON, nullable=False)
    generated_image_url = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="designs")
    design_requests = relationship("DesignRequest", back_populates="generated_design")

class DesignRequest(Base):
    __tablename__ = "design_requests"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    jeweler_id = Column(Integer, ForeignKey("jewelers.id"), nullable=True)
    generated_design_id = Column(Integer, ForeignKey("user_generated_designs.id"), nullable=True)
    request_date = Column(DateTime, default=datetime.utcnow)
    description = Column(Text, nullable=True)
    attachment_url = Column(String(255), nullable=True)
    estimated_budget = Column(DECIMAL(12, 2), nullable=True)
    jeweler_price_offer = Column(DECIMAL(12, 2), nullable=True)
    status = Column(Enum(DesignRequestStatusEnum), default=DesignRequestStatusEnum.pending)
    
    user = relationship("User", back_populates="design_requests")
    jeweler = relationship("Jeweler", back_populates="design_requests")
    generated_design = relationship("UserGeneratedDesign", back_populates="design_requests")
