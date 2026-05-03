from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import requests

app = FastAPI()

# CORS middleware for frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Item(BaseModel):
    name: str | None = 'Anonymous'
    category: str | None = 'General'
    idea: str

@app.post("/submit_idea")
async def submit_idea(item: Item):
    try:
        message = {
            "content": f"""🎯 **New Idea Submission**
👤 **Name:** {item.name}
📂 **Category:** {item.category}
💡 **Idea:** {item.idea}"""
        }
        
        response = requests.post("https://discord.com/api/webhooks/your_webhook_url", json=message, timeout=5)
        
        if response.status_code == 204:
            return {"message": "Idea submitted successfully!"}
        else:
            return {"message": "Idea submitted successfully!", "warning": "Discord notification may have failed"}
    
    except requests.exceptions.RequestException as e:
        print(f"Error sending to Discord: {e}")
        # Still return success to user since we received the idea
        return {"message": "Idea submitted successfully!"}