from datetime import timedelta
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app import crud, models, schemas
from app.api import deps
from app.core import security
from app.core.config import settings

router = APIRouter()

from datetime import timedelta
from typing import Any
import httpx
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from app import crud, models, schemas
from app.api import deps
from app.core import security
from app.core.config import settings
from app.core.x_auth import generate_pkce_pair, create_state

router = APIRouter()

X_AUTH_URL = "https://twitter.com/i/oauth2/authorize"
X_TOKEN_URL = "https://api.twitter.com/2/oauth2/token"
X_USER_ME_URL = "https://api.twitter.com/2/users/me"

@router.get("/login/x")
def login_x(request: Request):
    """
    Initiates the OAuth 2.0 flow with X.
    Redirects the user to X's authorization page.
    """
    if not settings.X_CLIENT_ID:
        raise HTTPException(status_code=500, detail="X_CLIENT_ID not configured")

    code_verifier, code_challenge = generate_pkce_pair()
    state = create_state()
    
    # Construct Authorization URL
    params = {
        "response_type": "code",
        "client_id": settings.X_CLIENT_ID,
        "redirect_uri": settings.X_REDIRECT_URI,
        "scope": "tweet.read tweet.write users.read offline.access",
        "state": state,
        "code_challenge": code_challenge,
        "code_challenge_method": "S256",
    }
    
    auth_url = httpx.URL(X_AUTH_URL).copy_with(params=params)
    
    response = RedirectResponse(url=str(auth_url))
    # Store verifier in a secure HTTP-only cookie
    response.set_cookie(key="x_oauth_verifier", value=code_verifier, httponly=True, secure=False) # secure=True in prod
    response.set_cookie(key="x_oauth_state", value=state, httponly=True, secure=False)
    
    return response

@router.get("/callback/x")
async def callback_x(request: Request, code: str, state: str, db: Session = Depends(deps.get_db)):
    """
    Handles the callback from X.
    Exchanges code for tokens and signs in the user.
    """
    # Verify State
    stored_state = request.cookies.get("x_oauth_state")
    if not stored_state or state != stored_state:
        raise HTTPException(status_code=400, detail="Invalid state parameter")
        
    # Retrieve Verifier
    code_verifier = request.cookies.get("x_oauth_verifier")
    if not code_verifier:
        raise HTTPException(status_code=400, detail="Missing code verifier")

    # Exchange Code for Token
    async with httpx.AsyncClient() as client:
        token_data = {
            "code": code,
            "grant_type": "authorization_code",
            "client_id": settings.X_CLIENT_ID,
            "redirect_uri": settings.X_REDIRECT_URI,
            "code_verifier": code_verifier,
        }
        # Include Client Secret if configured (Confidential Client), otherwise Public Client
        auth = None
        if settings.X_CLIENT_SECRET:
             auth = (settings.X_CLIENT_ID, settings.X_CLIENT_SECRET)

        try:
            token_response = await client.post(
                X_TOKEN_URL, 
                data=token_data, 
                auth=auth,
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            token_response.raise_for_status()
            tokens = token_response.json()
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Token exchange failed: {str(e)}")

        access_token = tokens["access_token"]
        refresh_token = tokens.get("refresh_token")
        
        # Get User Info
        try:
            user_response = await client.get(
                X_USER_ME_URL, 
                headers={"Authorization": f"Bearer {access_token}"}
            )
            user_response.raise_for_status()
            user_data = user_response.json()["data"]
        except Exception as e:
             raise HTTPException(status_code=400, detail=f"Failed to fetch user info: {str(e)}")

        x_user_id = user_data["id"]
        x_username = user_data["username"]

        # Create or Update User
        user = crud.user.get_by_x_user_id(db, x_user_id=x_user_id)
        if not user:
            # Create new user
            user_in = schemas.UserCreate(
                x_user_id=x_user_id,
                x_username=x_username,
                password=secrets.token_urlsafe(16), # Random password, not used
                access_token=access_token,
                refresh_token=refresh_token
            )
            user = crud.user.create(db, obj_in=user_in)
        else:
            # Update existing user
            user.access_token = access_token
            if refresh_token:
                user.refresh_token = refresh_token
            # Could also update username if changed
            user.x_username = x_username
            db.add(user)
            db.commit()
            db.refresh(user)

    # Generate App JWT
    access_token_expires = timedelta(minutes=security.ACCESS_TOKEN_EXPIRE_MINUTES)
    app_token = security.create_access_token(
        user.id, expires_delta=access_token_expires
    )
    
    # Redirect to Frontend
    frontend_url = f"http://localhost:3000/auth/success?token={app_token}"
    return RedirectResponse(url=frontend_url)
