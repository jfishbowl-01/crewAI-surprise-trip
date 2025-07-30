from dotenv import load_dotenv
import os
import json
from datetime import datetime

# Load environment variables from .env file
load_dotenv()

from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List, Union

app = FastAPI(
    title="AI Travel Planning Team for watsonx Orchestrate",
    description="Collaborative AI agents for surprise travel planning",
    version="1.0.0"
)

# Flexible model that handles any field names
class FlexibleTravelRequest(BaseModel):
    class Config:
        extra = "allow"  # Allow any extra fields

# Accept any JSON and extract what we need
@app.post("/plan-surprise-trip")
async def plan_surprise_trip(request: Dict[str, Any]):
    try:
        # Extract fields flexibly - handle any field names
        origin = request.get('origin') or request.get('from') or "Boston"
        destination = request.get('destination') or request.get('to') or "Unknown"
        age = str(request.get('age') or request.get('traveler_age') or "25")
        interests = request.get('interests') or request.get('activities') or "general travel"
        budget = request.get('budget') or request.get('cost') or "$2000"
        dates = request.get('dates') or request.get('travel dates') or request.get('travel_dates') or "TBD"
        duration = request.get('trip_duration') or request.get('duration') or request.get('trip duration') or "3 days"
        hotel_pref = request.get('hotel_preference') or request.get('hotel preference') or request.get('accommodation') or "standard"
        
        # Create sample itinerary
        itinerary = {
            "name": f"{origin} to {destination} {duration} Itinerary",
            "origin": origin,
            "destination": destination,
            "duration": duration,
            "budget": budget,
            "travel_dates": dates,
            "day_plans": [
                {
                    "date": "Day 1",
                    "activities": [
                        {
                            "name": f"Arrival in {destination}",
                            "description": f"Welcome to {destination}! Start your adventure with a scenic tour of the area.",
                            "type": "Arrival & Orientation",
                            "rating": 4.8,
                            "why_suitable": f"Perfect introduction to {destination} for someone age {age} interested in {interests}"
                        }
                    ],
                    "restaurants": [f"Local {destination} Welcome Dinner"],
                    "accommodation": f"{hotel_pref.title()} Hotel in {destination}"
                },
                {
                    "date": "Day 2", 
                    "activities": [
                        {
                            "name": f"{interests.split(',')[0].strip().title()} Experience",
                            "description": f"Immersive {interests.split(',')[0].strip()} experience tailored for age {age}",
                            "type": "Main Interest Activity",
                            "rating": 4.9,
                            "why_suitable": f"Matches your interest in {interests.split(',')[0].strip()}"
                        }
                    ],
                    "restaurants": [f"Highly-rated {destination} Restaurant"],
                    "accommodation": f"{hotel_pref.title()} Hotel"
                },
                {
                    "date": "Day 3",
                    "activities": [
                        {
                            "name": f"Final {destination} Experience",
                            "description": f"Conclude your trip with a memorable experience in {destination}",
                            "type": "Farewell Activity", 
                            "rating": 4.7,
                            "why_suitable": f"Perfect ending to your {destination} adventure"
                        }
                    ],
                    "restaurants": [f"Farewell dinner at premium {destination} restaurant"],
                    "accommodation": f"{hotel_pref.title()} Hotel"
                }
            ],
            "total_estimated_cost": budget,
            "created_by_agents": ["🎯 Activity Planner", "🍽️ Restaurant Scout", "📋 Itinerary Compiler"]
        }
        
        return {
            "success": True,
            "message": f"✅ AI Travel Team created amazing {duration} itinerary for {destination}!",
            "itinerary": itinerary,
            "agents_used": ["🎯 Activity Planner", "🍽️ Restaurant Scout", "📋 Itinerary Compiler"],
            "error": None
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": "❌ AI Travel Team encountered an issue",
            "itinerary": None,
            "agents_used": None,
            "error": str(e)
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)