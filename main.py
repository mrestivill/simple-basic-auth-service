import os
from typing import Annotated
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import secrets

app = FastAPI()
security = HTTPBasic()

def get_env_credentials():
    """Get credentials from environment variables"""
    username = os.getenv("USER", "admin")
    password = os.getenv("PASSWORD", "secret")
    return username, password

def authenticate_user(credentials: HTTPBasicCredentials):
    """Authenticate user against environment variables"""
    correct_username, correct_password = get_env_credentials()
    
    # Use constant-time comparison to prevent timing attacks
    correct_username_bytes = correct_username.encode("utf8")
    provided_username_bytes = credentials.username.encode("utf8")
    is_correct_username = secrets.compare_digest(
        correct_username_bytes, provided_username_bytes
    )
    
    correct_password_bytes = correct_password.encode("utf8")
    provided_password_bytes = credentials.password.encode("utf8")
    is_correct_password = secrets.compare_digest(
        correct_password_bytes, provided_password_bytes
    )
    
    if not (is_correct_username and is_correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    
    return credentials.username

@app.get("/")
def read_current_user(
    username: Annotated[str, Depends(authenticate_user)]
):
    return {
        "message": f"Hello {username}",
        "authenticated": True
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}