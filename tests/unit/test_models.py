"""
Week 1 tests: verify DB models are correctly defined.
Run: pytest tests/unit/test_models.py -v
"""
import pytest
from api.db.models import (
    Product, User, Dispute, LoyaltyTransaction, Offer, Category,
    DisputeType, DisputeStatus, TransactionType
)


def test_product_fields_exist():
    """Product model must have all required fields."""
    required = ["id", "sku", "name", "description", "price",
                "stock_qty", "expiry_date", "embedding", "is_active"]
    for field in required:
        assert hasattr(Product, field), f"Product missing field: {field}"


def test_user_fields_exist():
    required = ["id", "telegram_id", "display_name", "points_balance", "registered_at"]
    for field in required:
        assert hasattr(User, field), f"User missing field: {field}"


def test_dispute_fields_exist():
    required = ["id", "user_id", "dispute_type", "status",
                "description", "image_url", "claimed_price"]
    for field in required:
        assert hasattr(Dispute, field), f"Dispute missing field: {field}"


def test_dispute_types_complete():
    types = [e.value for e in DisputeType]
    assert "price_mismatch" in types
    assert "expired_product" in types
    assert "wrong_item" in types
    assert "damaged_packaging" in types


def test_dispute_statuses_complete():
    statuses = [e.value for e in DisputeStatus]
    assert "open" in statuses
    assert "in_review" in statuses
    assert "resolved" in statuses
    assert "rejected" in statuses


def test_loyalty_transaction_fields():
    required = ["id", "user_id", "transaction_type",
                "purchase_amount", "points_earned", "points_redeemed"]
    for field in required:
        assert hasattr(LoyaltyTransaction, field), f"LoyaltyTransaction missing: {field}"


def test_offer_fields():
    required = ["id", "title", "description", "discount_percent",
                "min_purchase", "valid_from", "valid_until", "is_active"]
    for field in required:
        assert hasattr(Offer, field), f"Offer missing: {field}"


def test_points_rate_logic():
    """Business rule: $100 purchase must earn $5 points at 5% rate."""
    from api.config import get_settings
    s = get_settings()
    purchase = 100.0
    earned = purchase * s.loyalty_points_rate
    assert earned == 5.0, f"Expected $5.00 points for $100, got ${earned}"


def test_session_ttl_is_30_minutes():
    from api.config import get_settings
    s = get_settings()
    assert s.session_ttl_seconds == 1800


def test_scope_filter_threshold():
    from api.config import get_settings
    s = get_settings()
    assert 0.0 < s.scope_filter_min_score < 1.0


def test_confidence_threshold():
    from api.config import get_settings
    s = get_settings()
    assert 0.5 <= s.confidence_min_score <= 0.95
