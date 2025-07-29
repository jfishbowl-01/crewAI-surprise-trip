from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()


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
    title="AI Travel Planning Team for Watson x Orchestrate",
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

class TravelResponse(BaseModel):
    success: bool
    message: str
    itinerary: Optional[dict] = None
    agents_used: Optional[list] = None
    error: Optional[str] = None

@app.post("/plan-surprise-trip", response_model=TravelResponse)
async def plan_surprise_trip(request: TravelRequest):
    """
    🎪 AI Travel Planning Team
    
    Our specialized agents collaborate to create amazing surprise trips:
    - 🎯 Activity Planner: Finds unique experiences and events
    - 🍽️ Restaurant Scout: Discovers incredible dining spots  
    - 📋 Itinerary Compiler: Creates comprehensive day-by-day plans
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
        
        # Parse the result to extract the itinerary
        itinerary = None
        if hasattr(result, 'json_dict') and result.json_dict:
            itinerary = result.json_dict
        elif hasattr(result, 'raw') and result.raw:
            try:
                itinerary = json.loads(result.raw)
            except:
                itinerary = {"raw_result": str(result)}
        elif isinstance(result, dict):
            itinerary = result
        else:
            itinerary = {"raw_result": str(result)}
        
        return TravelResponse(
            success=True,
            message=f"✅ AI Travel Team created amazing {request.trip_duration} itinerary for {request.destination}!",
            itinerary=itinerary,
            agents_used=["🎯 Activity Planner", "🍽️ Restaurant Scout", "📋 Itinerary Compiler"]
        )
        
    except Exception as e:
        return TravelResponse(
            success=False,
            message="❌ AI Travel Team encountered an issue",
            error=str(e)
        )

@app.get("/")
async def home():
    """Home endpoint with service information"""
    return {
        "service": "🎪 AI Travel Planning Team",
        "description": "Collaborative AI agents for Watson x Orchestrate",
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
        "status": "🚀 Ready for Watson x Orchestrate"
    }

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy", 
        "service": "AI Travel Planning Team",
        "agents_ready": True
    }

@app.get("/agents")
async def get_agents():
    """Information about available AI agents"""
    return {
        "team": "AI Travel Planning Specialists",
        "agents": [
            {
                "name": "Activity Planner",
                "role": "🎯 Research and find unique activities and experiences",
                "capabilities": ["Web search", "Event discovery", "Cultural research", "Age-appropriate recommendations"]
            },
            {
                "name": "Restaurant Scout", 
                "role": "🍽️ Find highly-rated restaurants and dining experiences",
                "capabilities": ["Restaurant reviews", "Cuisine analysis", "Local food discovery", "Scenic location scouting"]
            },
            {
                "name": "Itinerary Compiler",
                "role": "📋 Create comprehensive travel plans with logistics",
                "capabilities": ["Flight research", "Hotel recommendations", "Schedule optimization", "Day-by-day planning"]
            }
        ],
        "collaboration": "All agents work together using real-time web search to create personalized surprise travel itineraries"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)