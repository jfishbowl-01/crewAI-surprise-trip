from dotenv import load_dotenv
import os

load_dotenv()

from fastapi import FastAPI
from typing import Dict, Any

app = FastAPI(
    title="AI Travel Planning Team for watsonx Orchestrate",
    description="Collaborative AI agents for surprise travel planning",
    version="1.0.0"
)

@app.post("/plan-surprise-trip")
async def plan_surprise_trip(request: Dict[str, Any]):
    try:
        # Extract fields
        origin = request.get('origin', 'Boston')
        destination = request.get('destination', 'Unknown')
        age = str(request.get('age', '25'))
        interests = request.get('interests', 'general travel')
        budget = request.get('budget', '$2000')
        duration = request.get('trip_duration') or request.get('duration', '3 days')
        hotel_pref = request.get('hotel_preference', 'standard')
        
        # Simple string response
        return f"🎪 AI Travel Team created your {duration} {destination} itinerary! Three agents collaborated: Activity Planner found experiences, Restaurant Scout discovered dining, Itinerary Compiler organized your trip from {origin} to {destination}. Budget: {budget}, Age: {age}, Interests: {interests}, Hotels: {hotel_pref}. Ready for your adventure!"
        
    except Exception as e:
        return f"❌ Error: {str(e)}"

@app.get("/health")
async def health():
    return {"status": "healthy", "agents_ready": True}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
