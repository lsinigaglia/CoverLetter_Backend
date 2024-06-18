from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordBearer
from fastapi.responses import RedirectResponse
import requests
from jose import jwt
from sqlalchemy.orm import Session
from database import get_db
from crud import get_or_create_user
from models import User

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Replace these with your own values from the Google Developer Console
GOOGLE_CLIENT_ID = "149484648932-utpmlu4c0cecqo8oo6tkd02qca9c91ja.apps.googleusercontent.com"
GOOGLE_CLIENT_SECRET = "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"
GOOGLE_REDIRECT_URI = "http://localhost:8000/"


@router.get("/login/google")
async def login_google():
    auth_url = f"https://accounts.google.com/o/oauth2/auth?response_type=code&client_id={GOOGLE_CLIENT_ID}&redirect_uri={GOOGLE_REDIRECT_URI}&scope=openid%20profile%20email&access_type=offline"
    return RedirectResponse(url=auth_url)

@router.get("/auth/google")
async def auth_google(code: str, db: Session = Depends(get_db)):
    token_url = "https://accounts.google.com/o/oauth2/token"
    data = {
        "code": code,
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_CLIENT_SECRET,
        "redirect_uri": GOOGLE_REDIRECT_URI,
        "grant_type": "authorization_code",
    }
    response = requests.post(token_url, data=data)
    access_token = response.json().get("access_token")
    user_info = requests.get("https://www.googleapis.com/oauth2/v1/userinfo", headers={"Authorization": f"Bearer {access_token}"})
    user_info = response.json()
    
    # Save to database
    user = get_or_create_user(
        db=db,
        google_id=user_info["id"],
        name=user_info["name"],
        email=user_info["email"],
        profile_picture=user_info.get("picture")
    )

    return user  # Return the saved user data
@router.get("/token")
async def get_token(token: str = Depends(oauth2_scheme)):
    return jwt.decode(token, GOOGLE_CLIENT_SECRET, algorithms=["HS256"])
