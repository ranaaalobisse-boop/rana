import os
import sys
from datetime import datetime, timedelta
from decimal import Decimal
from passlib.context import CryptContext

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import SessionLocal, engine, Base
from models import (
    User, Jeweler, PaymentMethod, Category, Product, ProductImage,
    ProductCategory, Cart, CartItem, Order, OrderItem,
    UserGeneratedDesign, DesignRequest,
    GenderEnum, OrderStatusEnum, DesignRequestStatusEnum
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password):
    return pwd_context.hash(password)

def seed_database():
    print("🌱 Starting database seeding...")
    
    db = SessionLocal()
    
    try:
        # Clear existing data (optional - comment out if you want to keep existing data)
        print("🧹 Clearing existing data...")
        db.query(OrderItem).delete()
        db.query(Order).delete()
        db.query(CartItem).delete()
        db.query(Cart).delete()
        db.query(ProductCategory).delete()
        db.query(ProductImage).delete()
        db.query(Product).delete()
        db.query(DesignRequest).delete()
        db.query(UserGeneratedDesign).delete()
        db.query(Category).delete()
        db.query(PaymentMethod).delete()
        db.query(Jeweler).delete()
        db.query(User).delete()
        db.commit()
        print("✅ Existing data cleared")
        
        # Create Users (5 users, first 3 are admins)
        print("👥 Creating users...")
        users = [
            User(
                username="admin1",
                email="admin1@luxurygems.com",
                password=get_password_hash("admin123"),
                first_name="Admin",
                last_name="One",
                phone="+966501111111",
                gender=GenderEnum.male,
                address="Riyadh, Saudi Arabia"
            ),
            User(
                username="admin2",
                email="admin2@luxurygems.com",
                password=get_password_hash("admin123"),
                first_name="Admin",
                last_name="Two",
                phone="+966502222222",
                gender=GenderEnum.female,
                address="Jeddah, Saudi Arabia"
            ),
            User(
                username="admin3",
                email="admin3@luxurygems.com",
                password=get_password_hash("admin123"),
                first_name="Admin",
                last_name="Three",
                phone="+966503333333",
                gender=GenderEnum.male,
                address="Dammam, Saudi Arabia"
            ),
            User(
                username="customer1",
                email="customer1@gmail.com",
                password=get_password_hash("customer123"),
                first_name="Ahmed",
                last_name="Al-Rashid",
                phone="+966504444444",
                gender=GenderEnum.male,
                address="Riyadh, Al-Olaya District"
            ),
            User(
                username="customer2",
                email="customer2@gmail.com",
                password=get_password_hash("customer123"),
                first_name="Sara",
                last_name="Al-Amoudi",
                phone="+966505555555",
                gender=GenderEnum.female,
                address="Jeddah, Al-Andalus District"
            ),
        ]
        
        for user in users:
            db.add(user)
        db.commit()
        
        for user in users:
            db.refresh(user)
        
        print(f"✅ Created {len(users)} users")
        
        # Create Jewelers (3 jewelers)
        print("💎 Creating jewelers...")
        jewelers = [
            Jeweler(
                name="Al-Majed Jewelry",
                shop_name="Al-Majed Luxury Watches & Jewelry",
                bio="Over 50 years of excellence in crafting the finest gold and diamond jewelry. Specializing in traditional Arabic designs with modern elegance.",
                address="King Fahd Road, Riyadh, Saudi Arabia",
                phone="+966114444444",
                email="info@almajed.com",
                rating=Decimal("4.9")
            ),
            Jeweler(
                name="L'azurde",
                shop_name="L'azurde Jewelry",
                bio="Saudi Arabia's leading jewelry brand, offering contemporary designs with the highest quality gold and precious stones.",
                address="Red Sea Mall, Jeddah, Saudi Arabia",
                phone="+966126666666",
                email="contact@lazurde.com",
                rating=Decimal("4.7")
            ),
            Jeweler(
                name="Damas Jewelry",
                shop_name="Damas - House of Luxury",
                bio="International luxury jewelry brand offering exquisite diamond and gold collections with timeless elegance.",
                address="Kingdom Centre, Riyadh, Saudi Arabia",
                phone="+966113333333",
                email="saudi@damas.com",
                rating=Decimal("4.8")
            ),
        ]
        
        for jeweler in jewelers:
            db.add(jeweler)
        db.commit()
        
        for jeweler in jewelers:
            db.refresh(jeweler)
        
        print(f"✅ Created {len(jewelers)} jewelers")
        
        # Create Payment Methods (2 methods)
        print("💳 Creating payment methods...")
        payment_methods = [
            PaymentMethod(
                method_name="Bank Transfer",
                qr_code_image="uploads/qr_codes/bank_transfer_qr.png",
                is_active=True,
                notes="Transfer to Saudi National Bank (SNB). Account: 1234567890. Upload receipt after payment."
            ),
            PaymentMethod(
                method_name="STC Pay",
                qr_code_image="uploads/qr_codes/stc_pay_qr.png",
                is_active=True,
                notes="Scan QR code with STC Pay app or transfer to number: 0555555555"
            ),
        ]
        
        for method in payment_methods:
            db.add(method)
        db.commit()
        print(f"✅ Created {len(payment_methods)} payment methods")
        
        # Create Categories (3 main categories with subcategories)
        print("📂 Creating categories...")
        
        # Main categories
        rings_cat = Category(name="Rings", parent_id=None)
        necklaces_cat = Category(name="Necklaces", parent_id=None)
        bracelets_cat = Category(name="Bracelets", parent_id=None)
        earrings_cat = Category(name="Earrings", parent_id=None)
        
        main_categories = [rings_cat, necklaces_cat, bracelets_cat, earrings_cat]
        for cat in main_categories:
            db.add(cat)
        db.commit()
        
        for cat in main_categories:
            db.refresh(cat)
        
        # Subcategories for Rings
        subcategories = [
            Category(name="Engagement Rings", parent_id=rings_cat.id),
            Category(name="Wedding Bands", parent_id=rings_cat.id),
            Category(name="Fashion Rings", parent_id=rings_cat.id),
            Category(name="Gold Chains", parent_id=necklaces_cat.id),
            Category(name="Pendant Necklaces", parent_id=necklaces_cat.id),
            Category(name="Pearl Necklaces", parent_id=necklaces_cat.id),
            Category(name="Gold Bracelets", parent_id=bracelets_cat.id),
            Category(name="Diamond Bracelets", parent_id=bracelets_cat.id),
            Category(name="Charm Bracelets", parent_id=bracelets_cat.id),
            Category(name="Stud Earrings", parent_id=earrings_cat.id),
            Category(name="Hoop Earrings", parent_id=earrings_cat.id),
            Category(name="Drop Earrings", parent_id=earrings_cat.id),
        ]
        
        for sub in subcategories:
            db.add(sub)
        db.commit()
        
        all_categories = main_categories + subcategories
        print(f"✅ Created {len(all_categories)} categories")
        
        # Create Products (10 products)
        print("📦 Creating products...")
        products_data = [
            {
                "name": "18K Gold Diamond Solitaire Engagement Ring",
                "material": "Gold",
                "karat": "18k",
                "weight": Decimal("5.500"),
                "price": Decimal("15000.00"),
                "stock_quantity": 10,
                "description": "Elegant 18K gold engagement ring featuring a stunning 1-carat diamond solitaire. Classic six-prong setting for maximum brilliance.",
                "jeweler_id": jewelers[0].id,
                "categories": [rings_cat.id, subcategories[0].id],  # Rings, Engagement
            },
            {
                "name": "21K Gold Traditional Wedding Band",
                "material": "Gold",
                "karat": "21k",
                "weight": Decimal("8.200"),
                "price": Decimal("12500.00"),
                "stock_quantity": 15,
                "description": "Traditional 21K gold wedding band with intricate Arabic calligraphy engraving. Perfect for couples seeking cultural elegance.",
                "jeweler_id": jewelers[0].id,
                "categories": [rings_cat.id, subcategories[1].id],  # Rings, Wedding
            },
            {
                "name": "Natural Pearl Necklace with 18K Gold Clasp",
                "material": "Gold",
                "karat": "18k",
                "weight": Decimal("12.300"),
                "price": Decimal("8500.00"),
                "stock_quantity": 8,
                "description": "Exquisite natural pearl necklace featuring perfectly matched white pearls with an elegant 18K gold clasp.",
                "jeweler_id": jewelers[1].id,
                "categories": [necklaces_cat.id, subcategories[5].id],  # Necklaces, Pearl
            },
            {
                "name": "Diamond Tennis Bracelet 18K White Gold",
                "material": "White Gold",
                "karat": "18k",
                "weight": Decimal("15.600"),
                "price": Decimal("28500.00"),
                "stock_quantity": 5,
                "description": "Stunning diamond tennis bracelet with 3 carats of brilliant cut diamonds set in 18K white gold. Secure box clasp with safety catch.",
                "jeweler_id": jewelers[2].id,
                "categories": [bracelets_cat.id, subcategories[7].id],  # Bracelets, Diamond
            },
            {
                "name": "Ruby and Diamond Drop Earrings 18K",
                "material": "Gold",
                "karat": "18k",
                "weight": Decimal("6.800"),
                "price": Decimal("18500.00"),
                "stock_quantity": 6,
                "description": "Elegant drop earrings featuring vibrant Burmese rubies surrounded by brilliant diamonds. Perfect for special occasions.",
                "jeweler_id": jewelers[2].id,
                "categories": [earrings_cat.id, subcategories[11].id],  # Earrings, Drop
            },
            {
                "name": "Emerald Cut Emerald Ring 18K Gold",
                "material": "Gold",
                "karat": "18k",
                "weight": Decimal("7.200"),
                "price": Decimal("22000.00"),
                "stock_quantity": 4,
                "description": "Magnificent ring featuring a 2-carat emerald cut Colombian emerald, surrounded by a halo of diamonds.",
                "jeweler_id": jewelers[0].id,
                "categories": [rings_cat.id, subcategories[2].id],  # Rings, Fashion
            },
            {
                "name": "Classic Gold Chain 21K",
                "material": "Gold",
                "karat": "21k",
                "weight": Decimal("25.000"),
                "price": Decimal("38000.00"),
                "stock_quantity": 12,
                "description": "Classic Cuban link chain in 21K gold. Bold and masculine design perfect for everyday wear or special occasions.",
                "jeweler_id": jewelers[1].id,
                "categories": [necklaces_cat.id, subcategories[3].id],  # Necklaces, Gold Chains
            },
            {
                "name": "Sapphire Halo Stud Earrings 18K",
                "material": "White Gold",
                "karat": "18k",
                "weight": Decimal("4.500"),
                "price": Decimal("16500.00"),
                "stock_quantity": 7,
                "description": "Beautiful stud earrings featuring Ceylon blue sapphires surrounded by diamond halos. Elegant and versatile.",
                "jeweler_id": jewelers[2].id,
                "categories": [earrings_cat.id, subcategories[9].id],  # Earrings, Stud
            },
            {
                "name": "Gold Charm Bracelet with Arabic Letters",
                "material": "Gold",
                "karat": "18k",
                "weight": Decimal("10.400"),
                "price": Decimal("9500.00"),
                "stock_quantity": 20,
                "description": "Personalizable charm bracelet in 18K gold with Arabic letter charms. Create your name or meaningful words.",
                "jeweler_id": jewelers[1].id,
                "categories": [bracelets_cat.id, subcategories[8].id],  # Bracelets, Charm
            },
            {
                "name": "Diamond Pendant Necklace Heart Shape",
                "material": "White Gold",
                "karat": "18k",
                "weight": Decimal("5.800"),
                "price": Decimal("12000.00"),
                "stock_quantity": 9,
                "description": "Romantic heart-shaped diamond pendant with 0.5 carat center diamond. Includes 18-inch white gold chain.",
                "jeweler_id": jewelers[0].id,
                "categories": [necklaces_cat.id, subcategories[4].id],  # Necklaces, Pendant
            },
        ]
        
        created_products = []
        for product_data in products_data:
            category_ids = product_data.pop("categories")
            
            product = Product(**product_data)
            db.add(product)
            db.flush()
            db.refresh(product)
            
            # Add category associations
            for cat_id in category_ids:
                product_category = ProductCategory(
                    product_id=product.id,
                    category_id=cat_id
                )
                db.add(product_category)
            
            created_products.append(product)
        
        db.commit()
        print(f"✅ Created {len(created_products)} products")
        
        # Create some sample orders
        print("📋 Creating sample orders...")
        
        # Create carts for users
        for i, user in enumerate(users[3:], 1):  # For customer users only
            cart = Cart(user_id=user.id)
            db.add(cart)
            db.flush()
            
            # Add items to cart
            cart_item = CartItem(
                cart_id=cart.id,
                product_id=created_products[i % len(created_products)].id,
                quantity=1
            )
            db.add(cart_item)
        
        db.commit()
        
        # Create one sample order
        sample_order = Order(
            user_id=users[3].id,  # customer1
            payment_method_id=payment_methods[0].id,
            total_amount=Decimal("15000.00"),
            shipping_address="Riyadh, Al-Olaya District, Building 123",
            status=OrderStatusEnum.pending
        )
        db.add(sample_order)
        db.flush()
        db.refresh(sample_order)
        
        # Add order items
        order_item = OrderItem(
            order_id=sample_order.id,
            product_id=created_products[0].id,
            quantity=1,
            unit_price=Decimal("15000.00"),
            subtotal=Decimal("15000.00")
        )
        db.add(order_item)
        
        db.commit()
        print("✅ Created sample order")
        
        print("\n🎉 Database seeding completed successfully!")
        print("\n--- Login Credentials ---")
        print("Admin Users:")
        for i in range(3):
            print(f"  Username: {users[i].username}, Password: admin123")
        print("\nCustomer Users:")
        for i in range(3, 5):
            print(f"  Username: {users[i].username}, Password: customer123")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error seeding database: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    print("=" * 50)
    print("   LUXURY JEWELRY API - DATABASE SEEDER")
    print("=" * 50)
    
    # Confirm with user
    response = input("\nThis will clear existing data and populate the database. Continue? (yes/no): ")
    if response.lower() in ["yes", "y"]:
        seed_database()
    else:
        print("Seeding cancelled.")
