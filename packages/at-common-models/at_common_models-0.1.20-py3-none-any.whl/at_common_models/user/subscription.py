from sqlalchemy import Column, String, DateTime, Boolean, event
from at_common_models.base import BaseModel
from datetime import datetime
import uuid
from zoneinfo import ZoneInfo

class UserSubscription(BaseModel):
    __tablename__ = "user_subscriptions"

    user_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    stripe_subscription_id = Column(String(255), unique=True, nullable=False)
    stripe_customer_id = Column(String(255), nullable=False)
    price_id = Column(String(255), nullable=False)  # Stripe price ID
    status = Column(String(50), nullable=False)  # active, canceled, etc.
    current_period_end = Column(DateTime, nullable=False)
    cancel_at_period_end = Column(Boolean, default=False)
    
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(ZoneInfo("UTC")))
    updated_at = Column(DateTime, nullable=False, default=lambda: datetime.now(ZoneInfo("UTC")), onupdate=lambda: datetime.now(ZoneInfo("UTC")))

@event.listens_for(UserSubscription, 'before_update')
def receive_before_update(mapper, connection, target):
    target.updated_at = datetime.now(ZoneInfo("UTC"))