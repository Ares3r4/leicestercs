from fastapi import FastAPI
from pydantic import BaseModel
import requests

app =FastAPI()

class Item(BaseModel):
    name: str | None = 'Anonymous'
    category: str | None = 'General'
    idea: str

@app.post("/submit_idea")
async def submit_idea(item: Item):

    message = {
        
        "content": f""" New idea submission 
    Name: {item.name}
    Category: {item.category}
    Idea: {item.idea}
    """
    }
    
    requests.post("https://discord.com/api/webhooks/your_webhook_url", json=message)
    return {"message": "Idea submitted successfully!"}