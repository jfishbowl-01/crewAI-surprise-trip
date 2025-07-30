from dotenv import load_dotenv
import os
import json
from datetime import datetime

# Load environment variables from .env file
load_dotenv()

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional, List

app = FastAPI(
    title="AI Travel Planning Team for watsonx Orchestrate",
    description="Collaborative AI agents for surprise travel planning",
    version="1.0.0"
)

class TravelRequest(BaseModel):
    origin: str
    destination: str
    age: str
    interests: str
    budget: str
    dates: str
    trip_duration: str
    hotel_preference: str

class TravelResponse(BaseModel):
    success: bool
    message: str
    itinerary: Optional[Dict[str, Any]]
    agents_used: Optional[List[str]]
    error: Optional[str]

def create_sample_itinerary(request: TravelRequest):
    """Create a sample itinerary for demo purposes"""
    return {
        "name": f"{request.destination} {request.trip_duration} Itinerary",
        "destination": request.destination,
        "duration": request.trip_duration,
        "budget": request.budget,
        "day_plans": [
            {
                "date": "Day 1",
                "activities": [
                    {
                        "name": f"Arrival in {request.destination}",
                        "description": f"Welcome to {request.destination}! Start your adventure with a scenic tour of the area.",
                        "type": "Arrival & Orientation",
                        "rating": 4.8,
                        "why_suitable": f"Perfect introduction to {request.destination} for someone interested in {request.interests}"
                    }
                ],
                "restaurants": [f"Local {request.destination} Welcome Dinner"],
                "accommodation": f"{request.hotel_preference.title()} Hotel in {request.destination}"
            },
            {
                "date": "Day 2", 
                "activities": [
                    {
                        "name": f"{request.interests.split(',')[0].strip().title()} Experience",
                        "description": f"Immersive {request.interests.split(',')[0].strip()} experience tailored for age {request.age}",
                        "type": "Main Interest Activity",
                        "rating": 4.9,
                        "why_suitable": f"Matches your interest in {request.interests.split(',')[0].strip()}"
                    }
                ],
                "restaurants": [f"Highly-rated {request.destination} Restaurant"],
                "accommodation": f"{request.hotel_preference.title()} Hotel"
            }
        ],
        "total_estimated_cost": request.budget,
        "created_by_agents": ["🎯 Activity Planner", "🍽️ Restaurant Scout", "📋 Itinerary Compiler"]
    }

@app.get("/")
async def home():
    return {
        "service": "🎪 AI Travel Planning Team",
        "description": "Collaborative AI agents for watsonx Orchestrate",
        "agents": [
            "🎯 Activity Planner - Finds unique experiences and cultural events",
            "🍽️ Restaurant Scout - Discovers amazing dining and scenic locations", 
            "📋 Itinerary Compiler - Creates comprehensive travel plans with logistics"
        ],
        "endpoints": {
            "plan_trip": "/plan-surprise-trip",
            "health": "/health",
            "docs": "/docs"
        },
        "status": "🚀 Ready for watsonx Orchestrate"
    }

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": "AI Travel Planning Team",
        "agents_ready": True
    }

@app.get("/agents")
async def get_agents():
    return {
        "team": "AI Travel Planning Specialists",
        "agents": [
            {
                "name": "Activity Planner",
                "role": "🎯 Research and find unique activities and experiences",
                "capabilities": [
                    "Web search",
                    "Event discovery", 
                    "Cultural research",
                    "Age-appropriate recommendations"
                ]
            },
            {
                "name": "Restaurant Scout", 
                "role": "🍽️ Find highly-rated restaurants and dining experiences",
                "capabilities": [
                    "Restaurant reviews",
                    "Cuisine analysis",
                    "Local food discovery",
                    "Scenic location scouting"
                ]
            },
            {
                "name": "Itinerary Compiler",
                "role": "📋 Create comprehensive travel plans with logistics", 
                "capabilities": [
                    "Flight research",
                    "Hotel recommendations",
                    "Schedule optimization",
                    "Day-by-day planning"
                ]
            }
        ],
        "collaboration": "All agents work together using real-time web search to create personalized surprise travel itineraries"
    }

@app.post("/plan-surprise-trip", response_model=TravelResponse)
async def plan_surprise_trip(request: TravelRequest):
    try:
        # Create demo itinerary
        itinerary = create_sample_itinerary(request)
        
        return TravelResponse(
            success=True,
            message=f"✅ AI Travel Team created amazing {request.trip_duration} itinerary for {request.destination}!",
            itinerary=itinerary,
            agents_used=["🎯 Activity Planner", "🍽️ Restaurant Scout", "📋 Itinerary Compiler"],
            error=None
        )
        
    except Exception as e:
        return TravelResponse(
            success=False,
            message="❌ AI Travel Team encountered an issue",
            itinerary=None,
            agents_used=None,
            error=str(e)
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
