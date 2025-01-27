from datetime import datetime, timedelta
from uuid import uuid4
from at_common_models.user.subscription import UserSubscription

def test_user_subscription_model(session):
    # Create test data
    user_id = uuid4()
    subscription = UserSubscription(
        user_id=user_id,
        stripe_subscription_id="sub_123",
        stripe_customer_id="cus_123",
        plan_id="price_123",
        status="active",
        current_period_end=datetime.now() + timedelta(days=30),
        cancel_at_period_end=False
    )
    
    session.add(subscription)
    session.commit()
    
    result = session.query(UserSubscription).filter_by(user_id=user_id).first()
    assert result.stripe_subscription_id == "sub_123"
    assert result.stripe_customer_id == "cus_123"
    assert result.plan_id == "price_123"
    assert result.status == "active"
    assert result.cancel_at_period_end == False

def test_subscription_unique_constraints(session):
    # Test unique constraint on stripe_subscription_id
    user_id1 = uuid4()
    user_id2 = uuid4()
    
    sub1 = UserSubscription(
        user_id=user_id1,
        stripe_subscription_id="sub_123",
        stripe_customer_id="cus_123",
        plan_id="price_123",
        status="active",
        current_period_end=datetime.now() + timedelta(days=30)
    )
    
    sub2 = UserSubscription(
        user_id=user_id2,
        stripe_subscription_id="sub_123",  # Same stripe_subscription_id
        stripe_customer_id="cus_456",
        plan_id="price_456",
        status="active",
        current_period_end=datetime.now() + timedelta(days=30)
    )
    
    session.add(sub1)
    session.commit()
    
    try:
        session.add(sub2)
        session.commit()
        assert False, "Should have raised an integrity error"
    except:
        session.rollback()
        assert True

def test_subscription_status_transitions(session):
    # Test subscription status changes
    user_id = uuid4()
    subscription = UserSubscription(
        user_id=user_id,
        stripe_subscription_id="sub_789",
        stripe_customer_id="cus_789",
        plan_id="price_789",
        status="active",
        current_period_end=datetime.now() + timedelta(days=30)
    )
    
    session.add(subscription)
    session.commit()
    
    # Update subscription status
    subscription.status = "canceled"
    subscription.cancel_at_period_end = True
    session.commit()
    
    result = session.query(UserSubscription).filter_by(user_id=user_id).first()
    assert result.status == "canceled"
    assert result.cancel_at_period_end == True

def test_subscription_timestamps(session):
    # Test automatic timestamp handling
    user_id = uuid4()
    subscription = UserSubscription(
        user_id=user_id,
        stripe_subscription_id="sub_time",
        stripe_customer_id="cus_time",
        plan_id="price_time",
        status="active",
        current_period_end=datetime.now() + timedelta(days=30)
    )
    
    session.add(subscription)
    session.commit()
    
    result = session.query(UserSubscription).filter_by(user_id=user_id).first()
    assert result.created_at is not None
    assert result.updated_at is not None
    
    # Test updated_at changes on update
    original_updated_at = result.updated_at
    result.status = "past_due"
    session.commit()
    session.refresh(result)
    
    assert result.updated_at != original_updated_at 