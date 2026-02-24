from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional, List
from datetime import datetime
from decimal import Decimal
import enum

class GenderEnum(str, enum.Enum):
    male = "male"
    female = "female"
    other = "other"

class OrderStatusEnum(str, enum.Enum):
    pending = "pending"
    confirmed = "confirmed"
    processing = "processing"
    shipped = "shipped"
    delivered = "delivered"
    cancelled = "cancelled"

class DesignRequestStatusEnum(str, enum.Enum):
    pending = "pending"
    reviewed = "reviewed"
    quoted = "quoted"
    accepted = "accepted"
    rejected = "rejected"
    in_progress = "in_progress"
    completed = "completed"

# User Schemas
class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    first_name: Optional[str] = Field(None, max_length=50)
    last_name: Optional[str] = Field(None, max_length=50)
    phone: Optional[str] = Field(None, max_length=20)
    gender: Optional[GenderEnum] = None
    address: Optional[str] = None

class UserCreate(UserBase):
    password: str = Field(..., min_length=6)

class UserResponse(UserBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    username: Optional[str] = None

# Jeweler Schemas
class JewelerBase(BaseModel):
    name: str = Field(..., max_length=100)
    shop_name: Optional[str] = Field(None, max_length=100)
    bio: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = Field(None, max_length=20)
    email: Optional[EmailStr] = None

class JewelerCreate(JewelerBase):
    pass

class JewelerResponse(JewelerBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    rating: Decimal
    created_at: datetime

# Category Schemas
class CategoryBase(BaseModel):
    name: str = Field(..., max_length=100)
    parent_id: Optional[int] = None

class CategoryCreate(CategoryBase):
    pass

class CategoryResponse(CategoryBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    subcategories: Optional[List['CategoryResponse']] = None

# Product Image Schemas
class ProductImageBase(BaseModel):
    image_path: str
    display_order: int = 0

class ProductImageCreate(ProductImageBase):
    product_id: int

class ProductImageResponse(ProductImageBase):
    model_config = ConfigDict(from_attributes=True)
    id: int

# Product Schemas
class ProductBase(BaseModel):
    name: str = Field(..., max_length=200)
    material: Optional[str] = Field(None, max_length=50)
    karat: Optional[str] = Field(None, max_length=10)
    weight: Optional[Decimal] = None
    price: Decimal
    stock_quantity: int = 0
    description: Optional[str] = None
    image_path: Optional[str] = None

class ProductCreate(ProductBase):
    jeweler_id: int
    category_ids: Optional[List[int]] = []

class ProductFilter(BaseModel):
    category_id: Optional[int] = None
    material: Optional[str] = None
    min_price: Optional[Decimal] = None
    max_price: Optional[Decimal] = None
    search: Optional[str] = None

class ProductResponse(ProductBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    jeweler_id: int
    images: List[ProductImageResponse] = []
    categories: List[CategoryResponse] = []

class ProductDetailResponse(ProductResponse):
    jeweler: Optional[JewelerResponse] = None

# Cart Schemas
class CartItemBase(BaseModel):
    product_id: int
    quantity: int = Field(..., ge=1)

class CartItemCreate(CartItemBase):
    pass

class CartItemResponse(CartItemBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    cart_id: int
    product: Optional[ProductResponse] = None

class CartResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: int
    items: List[CartItemResponse] = []
    updated_at: datetime
    total_items: int = 0
    total_amount: Decimal = Decimal('0')

# Order Item Schemas
class OrderItemBase(BaseModel):
    product_id: int
    quantity: int
    unit_price: Decimal
    subtotal: Decimal

class OrderItemResponse(OrderItemBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    order_id: int
    product: Optional[ProductResponse] = None

# Order Schemas
class OrderBase(BaseModel):
    payment_method_id: Optional[int] = None
    shipping_address: Optional[str] = None

class OrderCreate(OrderBase):
    pass

class OrderResponse(OrderBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: int
    order_date: datetime
    status: OrderStatusEnum
    total_amount: Decimal
    transfer_receipt: Optional[str] = None
    items: List[OrderItemResponse] = []

class OrderStatusUpdate(BaseModel):
    status: OrderStatusEnum

# Payment Method Schemas
class PaymentMethodBase(BaseModel):
    method_name: str = Field(..., max_length=50)
    qr_code_image: Optional[str] = None
    is_active: bool = True
    notes: Optional[str] = None

class PaymentMethodCreate(PaymentMethodBase):
    pass

class PaymentMethodResponse(PaymentMethodBase):
    model_config = ConfigDict(from_attributes=True)
    id: int

# AI Design Schemas
class DesignOptions(BaseModel):
    type: str = Field(..., description="Ring, Necklace, Bracelet, Earrings, etc.")
    color: str = Field(..., description="Gold, Silver, Rose Gold, etc.")
    shape: str = Field(..., description="Round, Square, Oval, Heart, etc.")
    material: str = Field(..., description="Silver, Gold, Platinum, etc.")
    karat: str = Field(..., description="18k, 21k, 24k, etc.")
    gemstone_type: str = Field(..., description="Diamond, Ruby, Sapphire, Emerald, None, etc.")
    gemstone_color: str = Field(..., description="White, Red, Blue, Green, etc.")

class AIGenerateRequest(BaseModel):
    type: str
    color: str
    shape: str
    material: str
    karat: str
    gemstone_type: str
    gemstone_color: str

class AIGenerateResponse(BaseModel):
    success: bool
    design_id: int
    image_url: str
    message: str

class UserGeneratedDesignResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: int
    selected_options: dict
    generated_image_url: str
    created_at: datetime

# Design Request Schemas
class DesignRequestBase(BaseModel):
    jeweler_id: Optional[int] = None
    generated_design_id: Optional[int] = None
    description: Optional[str] = None
    attachment_url: Optional[str] = None
    estimated_budget: Optional[Decimal] = None

class DesignRequestCreate(DesignRequestBase):
    pass

class DesignRequestUpdate(BaseModel):
    status: Optional[DesignRequestStatusEnum] = None
    jeweler_price_offer: Optional[Decimal] = None

class DesignRequestResponse(DesignRequestBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: int
    request_date: datetime
    status: DesignRequestStatusEnum
    jeweler_price_offer: Optional[Decimal] = None
    user: Optional[UserResponse] = None
    jeweler: Optional[JewelerResponse] = None
    generated_design: Optional[UserGeneratedDesignResponse] = None
