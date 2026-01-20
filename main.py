import secrets
import datetime
import requests
from fastapi import FastAPI, Depends, HTTPException, Request, Header, status
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

import models
import schemas
from database import engine, get_db, SessionLocal


# Create all database tables on startup
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

OLLAMA_BASE_URL = "http://localhost:11434"

# --- API Endpoints for Dashboard ---

@app.get("/api/models")
def get_available_ollama_models():
    """Fetch the list of locally available models from Ollama."""
    try:
        response = requests.get(f"{OLLAMA_BASE_URL}/api/tags")
        response.raise_for_status()
        models_data = response.json().get("models", [])
        return [model["name"] for model in models_data]
    except requests.exceptions.RequestException:
        raise HTTPException(status_code=503, detail="Could not connect to Ollama server.")

@app.post("/api/keys", status_code=status.HTTP_201_CREATED)
def create_api_key(key_data: schemas.APIKeyCreate, db: Session = Depends(get_db)):
    """Create a new API key for a specific Ollama model."""
    available_models = get_available_ollama_models()
    if key_data.model_name not in available_models:
        raise HTTPException(status_code=400, detail=f"Model '{key_data.model_name}' not found in Ollama.")

    new_secret_key = f"sk-ollama-{secrets.token_hex(24)}"
    
    db_key = models.APIKey(
        key_name=key_data.name,
        secret_key=new_secret_key,
        allowed_model=key_data.model_name
    )
    db.add(db_key)
    db.commit()
    db.refresh(db_key)

    return {"name": db_key.key_name, "secret_key": db_key.secret_key, "model": db_key.allowed_model}

@app.get("/api/keys", response_model=list[schemas.APIKeyResponse])
def get_all_keys(db: Session = Depends(get_db)):
    """Get a list of all created API keys."""
    keys = db.query(models.APIKey).order_by(models.APIKey.created_at.desc()).all()
    response_keys = []
    for key in keys:
        response_keys.append({
            "id": key.id,
            "name": key.key_name,
            "secret_key_display": f"{key.secret_key[:12]}...{key.secret_key[-4:]}",
            "created_at": key.created_at,
            "project_access": key.allowed_model
        })
    return response_keys

@app.delete("/api/keys/{key_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_api_key(key_id: int, db: Session = Depends(get_db)):
    """Delete an API key by its ID."""
    key_to_delete = db.query(models.APIKey).filter(models.APIKey.id == key_id).first()
    if not key_to_delete:
        raise HTTPException(status_code=404, detail="API Key not found.")
    db.delete(key_to_delete)
    db.commit()
    return

# --- OpenAI-Compatible Gateway Endpoint ---

@app.post("/v1/chat/completions")
async def chat_proxy(request: Request, authorization: str = Header(...), db: Session = Depends(get_db)):
    """Acts as a secure proxy to the Ollama server."""
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization scheme.")
    
    token = authorization.split(" ")[1]
    
    api_key_record = db.query(models.APIKey).filter(models.APIKey.secret_key == token).first()
    if not api_key_record:
        raise HTTPException(status_code=401, detail="Invalid API Key.")

    body = await request.json()
    requested_model = body.get("model")
    
    if requested_model != api_key_record.allowed_model:
        raise HTTPException(
            status_code=403, 
            detail=f"This API key is not authorized for model '{requested_model}'. "
                   f"It is authorized for '{api_key_record.allowed_model}'."
        )

    def stream_response():
        try:
            with requests.post(f"{OLLAMA_BASE_URL}/v1/chat/completions", json=body, stream=True) as ollama_response:
                ollama_response.raise_for_status()
                for chunk in ollama_response.iter_content(chunk_size=8192):
                    yield chunk
        except requests.exceptions.RequestException:
            # This part is tricky to handle in a generator. Logging would be ideal here.
            # For the client, the stream will just end.
            print("Error connecting to Ollama while streaming.")

    return StreamingResponse(stream_response())


# --- Serve Frontend Files ---
# Mount the 'frontend' directory to serve static files like index.html, css, js
app.mount("/static", StaticFiles(directory="frontend"), name="static")

@app.get("/")
async def read_index():
    return FileResponse('frontend/index.html')



# uvicorn main:app --reload