import os

from fastapi import FastAPI, Depends, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import requests
from typing import List, Optional
import uvicorn

app = FastAPI()

# CORS middleware for frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage
products = []
events = []

# Sensitive values are loaded from environment variables so they are not stored in Git.
ADMIN_API_KEY = os.getenv("ADMIN_API_KEY", "")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "")
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL", "")

class Item(BaseModel):
    name: str | None = 'Anonymous'
    category: str | None = 'General'
    idea: str

class Product(BaseModel):
    name: str
    price: float
    description: str
    image_url: Optional[str] = None

class Event(BaseModel):
    title: str
    date: str
    description: str
    location: Optional[str] = None

def verify_admin(api_key: str = Header(None, alias="X-API-Key")):
    if api_key != ADMIN_API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API key")
    return True

@app.post("/submit_idea")
async def submit_idea(item: Item):
    try:
        message = {
            "content": f"""🎯 **New Idea Submission**
👤 **Name:** {item.name}
📂 **Category:** {item.category}
💡 **Idea:** {item.idea}"""
        }
        
        if DISCORD_WEBHOOK_URL:
            response = requests.post(DISCORD_WEBHOOK_URL, json=message, timeout=5)
            if response.status_code == 204:
                return {"message": "Idea submitted successfully!"}
            return {"message": "Idea submitted successfully!", "warning": "Discord notification may have failed"}
        return {"message": "Idea submitted successfully!", "warning": "No webhook configured"}
    except requests.exceptions.RequestException as e:
        print(f"Error sending to Discord: {e}")
        # Still return success to user since we received the idea
        return {"message": "Idea submitted successfully!"}

@app.post("/login")
async def login(data: dict):
    if data.get("password") == ADMIN_PASSWORD:
        return {"token": ADMIN_API_KEY}
    raise HTTPException(status_code=401, detail="Invalid password")

@app.get("/products")
async def get_products():
    return products

@app.post("/products")
async def add_product(product: Product, admin: bool = Depends(verify_admin)):
    products.append(product)
    return {"message": "Product added successfully"}

@app.get("/events")
async def get_events():
    return events

@app.post("/events")
async def add_event(event: Event, admin: bool = Depends(verify_admin)):
    events.append(event)
    return {"message": "Event added successfully"}

# Serve static files after API routes are defined
app.mount("/", StaticFiles(directory=".", html=True), name="static")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)