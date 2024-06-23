from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordBearer
from fastapi.responses import RedirectResponse
import requests
from jose import jwt
from sqlalchemy.orm import Session

from app.database import get_db as get_db
from app.crud import get_or_create_user as get_or_create_user
from app.models import User as User
from fastapi import HTTPException


router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Replace these with your own values from the Google Developer Console
GOOGLE_CLIENT_ID = "149484648932-utpmlu4c0cecqo8oo6tkd02qca9c91ja.apps.googleusercontent.com"
GOOGLE_CLIENT_SECRET = "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"
GOOGLE_REDIRECT_URI = "https://coverletter-backend-u4pzro2pw-lucas-projects-7060412b.vercel.app/"


@router.get("/login/google")
async def login_google():
    auth_url = f"https://accounts.google.com/o/oauth2/auth?response_type=code&client_id={GOOGLE_CLIENT_ID}&redirect_uri={GOOGLE_REDIRECT_URI}&scope=openid%20profile%20email&access_type=offline"
    print("hello")
    return RedirectResponse(url=auth_url)

@router.get("/")
async def auth_google(code: str, db: Session = Depends(get_db)):
    print("hello1")
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
    user_info = user_info.json()
    print("Access Token:", access_token)
    print("User Info:", user_info)
    
    # Save to database
    try:
        # Existing code to get access_token and user_info
        user = get_or_create_user(db=db, google_id=user_info["id"], name=user_info["name"], email=user_info["email"], profile_picture=user_info.get("picture"))
        print("User:", user.email)  # Example of a safe print statement
        return user  # Return the saved user data
    except Exception as e:
        print("Error:", e)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/token")
async def get_token(token: str = Depends(oauth2_scheme)):
    return jwt.decode(token, GOOGLE_CLIENT_SECRET, algorithms=["HS256"])