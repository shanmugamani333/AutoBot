"""
Seed the database with sample categories, products, and offers.
Run: docker compose exec api python -m db.seed
"""
import asyncio
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from api.db.session import AsyncSessionLocal
from api.db.models import Category, Product, Offer, User

CATEGORIES = ["Grains & Cereals", "Dairy", "Beverages", "Snacks", "Proteins", "Fruits & Vegetables"]

PRODUCTS = [
    # Grains
    {"sku": "GR001", "name": "Basmati Rice 1kg", "description": "Long grain basmati rice, aged 2 years", "price": 3.50, "stock_qty": 80, "category": "Grains & Cereals", "expiry_days": 365},
    {"sku": "GR002", "name": "Rolled Oats 500g", "description": "Whole grain rolled oats, high in fiber", "price": 2.20, "stock_qty": 60, "category": "Grains & Cereals", "expiry_days": 180},
    {"sku": "GR003", "name": "Wheat Flour 1kg", "description": "All-purpose wheat flour for baking", "price": 1.80, "stock_qty": 100, "category": "Grains & Cereals", "expiry_days": 270},
    {"sku": "GR004", "name": "Brown Bread 400g", "description": "Whole wheat brown bread, freshly baked", "price": 2.50, "stock_qty": 30, "category": "Grains & Cereals", "expiry_days": 5},
    # Dairy
    {"sku": "DA001", "name": "Full Cream Milk 1L", "description": "Fresh full cream cow milk", "price": 1.50, "stock_qty": 50, "category": "Dairy", "expiry_days": 7},
    {"sku": "DA002", "name": "Greek Yogurt 200g", "description": "Thick creamy greek yogurt, high in protein", "price": 2.80, "stock_qty": 40, "category": "Dairy", "expiry_days": 14},
    {"sku": "DA003", "name": "Cheddar Cheese 250g", "description": "Aged cheddar cheese block", "price": 4.20, "stock_qty": 25, "category": "Dairy", "expiry_days": 60},
    {"sku": "DA004", "name": "Butter 100g", "description": "Unsalted cow butter", "price": 1.90, "stock_qty": 35, "category": "Dairy", "expiry_days": 30},
    # Beverages
    {"sku": "BV001", "name": "Orange Juice 1L", "description": "100% pure squeezed orange juice, no sugar added", "price": 3.00, "stock_qty": 45, "category": "Beverages", "expiry_days": 10},
    {"sku": "BV002", "name": "Green Tea 20 bags", "description": "Premium green tea with antioxidants", "price": 2.40, "stock_qty": 70, "category": "Beverages", "expiry_days": 365},
    {"sku": "BV003", "name": "Mineral Water 1.5L", "description": "Natural mineral water from mountain spring", "price": 0.90, "stock_qty": 120, "category": "Beverages", "expiry_days": 365},
    # Snacks
    {"sku": "SN001", "name": "Mixed Nuts 200g", "description": "Roasted mixed nuts: almonds, cashews, walnuts", "price": 5.50, "stock_qty": 30, "category": "Snacks", "expiry_days": 90},
    {"sku": "SN002", "name": "Dark Chocolate 100g", "description": "70% dark chocolate bar", "price": 3.20, "stock_qty": 40, "category": "Snacks", "expiry_days": 180},
    {"sku": "SN003", "name": "Rice Crackers 150g", "description": "Light rice crackers, low calorie snack", "price": 1.80, "stock_qty": 55, "category": "Snacks", "expiry_days": 120},
    # Proteins
    {"sku": "PR001", "name": "Chicken Breast 500g", "description": "Boneless skinless chicken breast, high protein", "price": 6.50, "stock_qty": 20, "category": "Proteins", "expiry_days": 3},
    {"sku": "PR002", "name": "Eggs 12 pack", "description": "Free range large eggs, dozen pack", "price": 3.80, "stock_qty": 40, "category": "Proteins", "expiry_days": 21},
    {"sku": "PR003", "name": "Lentils 500g", "description": "Red lentils, high protein plant-based option", "price": 2.10, "stock_qty": 65, "category": "Proteins", "expiry_days": 365},
    {"sku": "PR004", "name": "Tuna Can 185g", "description": "Tuna in springwater, high protein", "price": 2.60, "stock_qty": 80, "category": "Proteins", "expiry_days": 730},
    # Fruits & Veg
    {"sku": "FV001", "name": "Banana 1kg", "description": "Fresh ripe bananas, natural energy source", "price": 1.40, "stock_qty": 60, "category": "Fruits & Vegetables", "expiry_days": 5},
    {"sku": "FV002", "name": "Spinach 250g", "description": "Fresh baby spinach leaves, iron-rich", "price": 2.00, "stock_qty": 30, "category": "Fruits & Vegetables", "expiry_days": 4},
    {"sku": "FV003", "name": "Tomatoes 500g", "description": "Ripe red tomatoes, fresh from farm", "price": 1.60, "stock_qty": 50, "category": "Fruits & Vegetables", "expiry_days": 6},
]

OFFERS = [
    {
        "title": "Buy 2 Get 10% Off Dairy",
        "description": "Purchase any 2 dairy products and get 10% discount",
        "discount_percent": 10.0,
        "min_purchase": 3.0,
        "valid_days": 30,
        "category": "Dairy",
    },
    {
        "title": "Weekend Special — 15% Off Snacks",
        "description": "All snack products at 15% off this weekend",
        "discount_percent": 15.0,
        "min_purchase": None,
        "valid_days": 7,
        "category": "Snacks",
    },
    {
        "title": "Earn Double Points This Week",
        "description": "Earn 10% instead of 5% points on all purchases above $20",
        "discount_percent": None,
        "min_purchase": 20.0,
        "valid_days": 7,
        "category": None,
    },
]


async def seed():
    async with AsyncSessionLocal() as db:
        # Categories
        cat_map = {}
        for cat_name in CATEGORIES:
            cat = Category(name=cat_name)
            db.add(cat)
            await db.flush()
            cat_map[cat_name] = cat.id

        # Products
        for p in PRODUCTS:
            product = Product(
                sku=p["sku"],
                name=p["name"],
                description=p["description"],
                price=p["price"],
                stock_qty=p["stock_qty"],
                category_id=cat_map.get(p["category"]),
                expiry_date=datetime.now() + timedelta(days=p["expiry_days"]),
            )
            db.add(product)

        # Offers
        now = datetime.now()
        for o in OFFERS:
            offer = Offer(
                title=o["title"],
                description=o["description"],
                discount_percent=o["discount_percent"],
                min_purchase=o["min_purchase"],
                valid_from=now,
                valid_until=now + timedelta(days=o["valid_days"]),
                category_id=cat_map.get(o["category"]) if o["category"] else None,
            )
            db.add(offer)

        # Demo user
        demo_user = User(
            telegram_id="000000000",
            display_name="Demo User",
            points_balance=12.50,
        )
        db.add(demo_user)

        await db.commit()
        print(f"Seeded {len(PRODUCTS)} products, {len(CATEGORIES)} categories, {len(OFFERS)} offers.")


if __name__ == "__main__":
    asyncio.run(seed())
