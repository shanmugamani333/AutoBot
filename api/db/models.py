"""
All database models.
Week 1 focus: define every table upfront so migrations are clean.
"""
import uuid
from datetime import datetime
from sqlalchemy import (
    String, Integer, Float, Boolean, Text, DateTime,
    ForeignKey, Enum as SAEnum, func
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from pgvector.sqlalchemy import Vector
import enum

from api.db.session import Base


# ── Enums ─────────────────────────────────────────────────────────────────


class DisputeType(str, enum.Enum):
    price_mismatch = "price_mismatch"
    expired_product = "expired_product"
    wrong_item = "wrong_item"
    damaged_packaging = "damaged_packaging"


class DisputeStatus(str, enum.Enum):
    open = "open"
    in_review = "in_review"
    resolved = "resolved"
    rejected = "rejected"


class TransactionType(str, enum.Enum):
    earned = "earned"
    redeemed = "redeemed"


# ── Models ────────────────────────────────────────────────────────────────


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    products: Mapped[list["Product"]] = relationship(back_populates="category")


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    sku: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    stock_qty: Mapped[int] = mapped_column(Integer, default=0)
    expiry_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    category_id: Mapped[int | None] = mapped_column(ForeignKey("categories.id"), nullable=True)

    # pgvector: 768-dim embedding of name + description
    embedding: Mapped[list[float] | None] = mapped_column(Vector(768), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    category: Mapped["Category | None"] = relationship(back_populates="products")


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    telegram_id: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    display_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    points_balance: Mapped[float] = mapped_column(Float, default=0.0)
    registered_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    disputes: Mapped[list["Dispute"]] = relationship(back_populates="user")
    loyalty_transactions: Mapped[list["LoyaltyTransaction"]] = relationship(back_populates="user")


class Dispute(Base):
    __tablename__ = "disputes"

    id: Mapped[str] = mapped_column(
        String(20), primary_key=True,
        default=lambda: f"D-{str(uuid.uuid4())[:8].upper()}"
    )
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    dispute_type: Mapped[DisputeType] = mapped_column(SAEnum(DisputeType), nullable=False)
    status: Mapped[DisputeStatus] = mapped_column(
        SAEnum(DisputeStatus), default=DisputeStatus.open
    )
    description: Mapped[str] = mapped_column(Text, nullable=False)
    image_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    product_sku: Mapped[str | None] = mapped_column(String(50), nullable=True)
    claimed_price: Mapped[float | None] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    resolution_note: Mapped[str | None] = mapped_column(Text, nullable=True)

    user: Mapped["User"] = relationship(back_populates="disputes")


class LoyaltyTransaction(Base):
    __tablename__ = "loyalty_transactions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    transaction_type: Mapped[TransactionType] = mapped_column(SAEnum(TransactionType))
    purchase_amount: Mapped[float | None] = mapped_column(Float, nullable=True)
    points_earned: Mapped[float] = mapped_column(Float, default=0.0)
    points_redeemed: Mapped[float] = mapped_column(Float, default=0.0)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    user: Mapped["User"] = relationship(back_populates="loyalty_transactions")


class Offer(Base):
    __tablename__ = "offers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    discount_percent: Mapped[float | None] = mapped_column(Float, nullable=True)
    min_purchase: Mapped[float | None] = mapped_column(Float, nullable=True)
    valid_from: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    valid_until: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    category_id: Mapped[int | None] = mapped_column(ForeignKey("categories.id"), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
