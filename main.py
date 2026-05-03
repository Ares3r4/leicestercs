import os
import time
from collections import deque
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from fastapi import FastAPI, Depends, HTTPException, Header, Request
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


products = []
events = [
    {
        "title": "Minecraft SMP",
        "date": "Ongoing",
        "description": "Join our community Minecraft server anytime. Chat, build, and play with fellow LeicesterCS members.",
        "location": "Minecraft SMP"
    }
]

SUBMISSION_LIMIT = 3
SUBMISSION_WINDOW = 15 * 60  # 15 minutes
SUBMISSION_COOLDOWN = 20  # seconds between submissions from same IP
idea_submission_log: dict[str, deque[float]] = {}

ADMIN_API_KEY = os.getenv("ADMIN_API_KEY", "")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "")
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN", "")
DISCORD_CHANNEL_ID = os.getenv("DISCORD_CHANNEL_ID", "")

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
async def submit_idea(item: Item, request: Request):
    ip = request.client.host if request.client else "unknown"
    now = time.time()
    queue = idea_submission_log.setdefault(ip, deque())

    # Clear old entries
    while queue and now - queue[0] > SUBMISSION_WINDOW:
        queue.popleft()

    if len(queue) >= SUBMISSION_LIMIT:
        raise HTTPException(status_code=429, detail="Too many submissions from this IP. Try again later.")

    if queue and now - queue[-1] < SUBMISSION_COOLDOWN:
        raise HTTPException(status_code=429, detail=f"Please wait {SUBMISSION_COOLDOWN} seconds between submissions.")

    idea_text = item.idea.strip() if item.idea else ""
    if len(idea_text) < 10:
        raise HTTPException(status_code=400, detail="Idea must be at least 10 characters.")
    if len(idea_text) > 1000:
        raise HTTPException(status_code=400, detail="Idea is too long.")

    queue.append(now)

    try:
        message_content = f"""🎯 **New Idea Submission**
👤 **Name:** {item.name}
📂 **Category:** {item.category}
💡 **Idea:** {idea_text}"""
        
        if DISCORD_BOT_TOKEN and DISCORD_CHANNEL_ID:
            headers = {
                "Authorization": f"Bot {DISCORD_BOT_TOKEN}",
                "Content-Type": "application/json"
            }
            payload = {
                "content": message_content
            }
            
            url = f"https://discord.com/api/v10/channels/{DISCORD_CHANNEL_ID}/messages"
            response = requests.post(url, json=payload, headers=headers, timeout=5)
            
            if response.status_code == 200:
                return {"message": "Idea submitted successfully!"}
            return {"message": "Idea submitted successfully!", "warning": f"Discord notification failed: {response.status_code}"}
        return {"message": "Idea submitted successfully!", "warning": "No Discord bot configured"}
    except requests.exceptions.RequestException as e:
        print(f"Error sending to Discord: {e}")
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