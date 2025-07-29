from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import sys
import os
import json

# Add the src directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from surprise_travel.crew import SurpriseTravelCrew

app = FastAPI(
    title="AI Travel Planning Team for watsonx Orchestrate",
    description="Collaborative AI agents for surprise travel planning",
    version="1.0.0"
)

# Enable CORS for Watson x Orchestrate
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TravelRequest(BaseModel):
    origin: str
    destination: str
    age: str = "31"
    interests: str
    budget: str
    dates: str
    trip_duration: str = "7 days"
    hotel_preference: str = "boutique"

@app.post("/plan-surprise-trip")
async def plan_surprise_trip(request: TravelRequest):
    """
    AI Travel Planning Team - Creates surprise travel itineraries
    """
    try:
        # Prepare inputs exactly as your working system expects
        inputs = {
            'origin': request.origin,
            'destination': request.destination, 
            'age': request.age,
            'hotel_location': f"{request.hotel_preference} hotel in {request.destination}",
            'flight_information': f"Round-trip flights from {request.origin} to {request.destination} on {request.dates}",
            'trip_duration': request.trip_duration
        }
        
        # Run your proven AI agent system
        crew = SurpriseTravelCrew()
        result = crew.crew().kickoff(inputs=inputs)
        
        return {
            "success": True,
            "message": f"✅ AI Travel Team created amazing {request.trip_duration} itinerary for {request.destination}!",
            "itinerary": result,
            "agents_used": ["Activity Planner", "Restaurant Scout", "Itinerary Compiler"]
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": "❌ AI Travel Team encountered an issue",
            "error": str(e)
        }

@app.get("/")
async def home():
    return {
        "service": "AI Travel Planning Team",
        "description": "Collaborative AI agents for Watson x Orchestrate",
        "agents": [
            "🎯 Activity Planner - Finds unique experiences",
            "🍽️ Restaurant Scout - Discovers amazing dining", 
            "📋 Itinerary Compiler - Creates comprehensive plans"
        ],
        "status": "ready"
    }

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "AI Travel Planning Team"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 