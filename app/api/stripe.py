from requests import Session
import stripe
from fastapi import APIRouter, Depends, HTTPException

from app.database import get_db
from app.models import User

router = APIRouter()

stripe.api_key = "sk_test_51PMdzMP5xPgjccehyKdHdhyVkeYQtbYPErJmWXhUGQYDNvw0VrJm3dDyRoOoQoqGzdVIdfeXpInLxWdJ9qnwhVZ5000vZoryJK"

@router.post("/create-checkout-session")
async def create_checkout_session(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
