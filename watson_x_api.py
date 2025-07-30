from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
import sys
import os

# Add the src directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'surprise_trip', 'src'))

try:
    from surprise_travel.crew import SurpriseTravelCrew
except ImportError:
    # Fallback if import fails
    SurpriseTravelCrew = None

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
        "agents_ready": SurpriseTravelCrew is not None
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
        if SurpriseTravelCrew is None:
            raise HTTPException(status_code=500, detail="CrewAI module not available")
            
        # Create and run the crew
        crew = SurpriseTravelCrew()
        result = crew.crew().kickoff(inputs={
            'origin': request.origin,
            'destination': request.destination, 
            'age': request.age,
            'interests': request.interests,
            'budget': request.budget,
            'dates': request.dates,
            'trip_duration': request.trip_duration,
            'hotel_preference': request.hotel_preference
        })
        
        return TravelResponse(
            success=True,
            message=f"✅ AI Travel Team created amazing {request.trip_duration} itinerary for {request.destination}!",
            itinerary=result,
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
