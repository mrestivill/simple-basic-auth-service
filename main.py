import os
from typing import Dict
from fastapi import Depends, FastAPI, HTTPException, status, Request
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import secrets

app = FastAPI()
security = HTTPBasic()

def get_env_credentials():
    """Get credentials from environment variables"""
    username = os.getenv("APP_USER", "admin")
    password = os.getenv("APP_PASSWORD", "secret")
    return username, password

def should_echo_headers() -> bool:
    """Check if we should echo headers based on ECHO_VARIABLES env var"""
    echo_var = os.getenv("ECHO_VARIABLES", "false").lower()
    return echo_var in ["true", "1", "yes", "y", "on"]

def authenticate_user(credentials: HTTPBasicCredentials = Depends(security)):
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
async def read_current_user(
    request: Request,
    username: str = Depends(authenticate_user)
):
    """Main endpoint with conditional header echo"""
    response_data = {
        "message": f"Hello {username}",
        "authenticated": True,
        "client_ip": request.client.host if request.client else None,
        "request_method": request.method,
        "request_path": request.url.path
    }
    
    # Only add headers if ECHO_VARIABLES is true
    if should_echo_headers():
        headers = {}
        for name, value in request.headers.items():
            # Skip sensitive headers
            if name.lower() not in ['authorization', 'cookie', 'x-api-key']:
                headers[name] = value
            else:
                headers[name] = "******"
        
        response_data["echo_variables_enabled"] = True
        response_data["your_headers"] = headers
    else:
        response_data["echo_variables_enabled"] = False
        response_data["note"] = "Set ECHO_VARIABLES=true to see headers"
    
    return response_data

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "echo_variables_enabled": should_echo_headers()
    }

@app.get("/config")
async def show_config():
    """Endpoint to show current configuration (no auth required)"""
    return {
        "echo_variables_enabled": should_echo_headers(),
        "echo_variables_value": os.getenv("ECHO_VARIABLES", "not set"),
        "app_user_set": bool(os.getenv("USER")),
        "app_password_set": bool(os.getenv("PASSWORD"))
    }
    
if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app,port=8000)
