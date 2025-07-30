from dotenv import load_dotenv
import os
import asyncio
from datetime import datetime
import json

load_dotenv()

from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
import uuid

app = FastAPI(
    title="AI Travel Planning Team - IBM watsonx.ai Edition",
    description="CrewAI travel planning powered by IBM watsonx.ai and Granite models",
    version="1.0.0-ibm"
)

# OpenAI-compatible request/response models
class ChatMessage(BaseModel):
    role: str  # "system", "user", "assistant"
    content: str

class ChatCompletionRequest(BaseModel):
    messages: List[ChatMessage]
    model: Optional[str] = "ibm/granite-13b-chat-v2"
    stream: Optional[bool] = False
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = 1000

class ChatCompletionChoice(BaseModel):
    index: int
    message: ChatMessage
    finish_reason: str

class ChatCompletionResponse(BaseModel):
    id: str
    object: str = "chat.completion"
    created: int
    model: str
    choices: List[ChatCompletionChoice]

def extract_travel_details(messages: List[ChatMessage]) -> Dict[str, str]:
    """Extract travel details from the conversation messages"""
    user_content = ""
    for msg in messages:
        if msg.role == "user":
            user_content += " " + msg.content
    
    # Simple keyword extraction - you could enhance this with NLP
    details = {
        'origin': 'Boston',  # default
        'destination': 'Unknown',
        'age': '25',
        'interests': 'general travel',
        'budget': '$2000',
        'duration': '3 days',
        'hotel_preference': 'standard'
    }
    
    content_lower = user_content.lower()
    
    # Extract destination
    destinations = {
        'tokyo': 'Tokyo', 'japan': 'Tokyo',
        'paris': 'Paris', 'france': 'Paris', 
        'london': 'London', 'england': 'London', 'uk': 'London',
        'new york': 'New York', 'nyc': 'New York',
        'rome': 'Rome', 'italy': 'Rome',
        'barcelona': 'Barcelona', 'spain': 'Barcelona',
        'amsterdam': 'Amsterdam', 'netherlands': 'Amsterdam',
        'berlin': 'Berlin', 'germany': 'Berlin'
    }
    
    for key, value in destinations.items():
        if key in content_lower:
            details['destination'] = value
            break
    
    # Extract origin
    if 'from boston' in content_lower:
        details['origin'] = 'Boston'
    elif 'from new york' in content_lower:
        details['origin'] = 'New York'
    elif 'from chicago' in content_lower:
        details['origin'] = 'Chicago'
    
    # Extract budget
    import re
    budget_match = re.search(r'\$(\d+,?\d*)', content_lower)
    if budget_match:
        details['budget'] = f"${budget_match.group(1)}"
    
    # Extract duration
    duration_patterns = [
        r'(\d+)\s*days?',
        r'(\d+)\s*weeks?',
        r'(\d+)\s*day\s*trip'
    ]
    for pattern in duration_patterns:
        match = re.search(pattern, content_lower)
        if match:
            num = match.group(1)
            if 'week' in pattern:
                details['duration'] = f"{num} weeks"
            else:
                details['duration'] = f"{num} days"
            break
    
    # Extract interests
    if 'food' in content_lower or 'restaurant' in content_lower or 'cuisine' in content_lower:
        details['interests'] = 'food and dining'
    elif 'museum' in content_lower or 'art' in content_lower or 'culture' in content_lower:
        details['interests'] = 'culture and museums'
    elif 'technology' in content_lower or 'tech' in content_lower:
        details['interests'] = 'technology and innovation'
    elif 'shopping' in content_lower:
        details['interests'] = 'shopping and fashion'
    elif 'business' in content_lower:
        details['interests'] = 'business and networking'
    
    return details

def generate_travel_response(details: Dict[str, str]) -> str:
    """Generate travel planning response using IBM watsonx.ai and CrewAI agents"""
    try:
        # Import CrewAI components
        from crewai import Agent, Task, Crew, Process
        from crewai_tools import SerperDevTool, ScrapeWebsiteTool
        
        # Import IBM watsonx.ai components
        try:
            from langchain_ibm import WatsonxLLM
            
            # Configure IBM watsonx.ai
            watsonx_llm = WatsonxLLM(
                model_id=os.getenv("WATSONX_MODEL", "llama-3-3-70b-instruct"),  # ← Uses env variable
                url=os.getenv("WATSONX_URL", "https://us-south.ml.cloud.ibm.com"),
                apikey=os.getenv("WATSONX_APIKEY"),
                project_id=os.getenv("WATSONX_PROJECT_ID"),
                params={
                    "temperature": float(os.getenv("WATSONX_TEMPERATURE", "0.7")),
                    "max_new_tokens": int(os.getenv("WATSONX_MAX_TOKENS", "1000")),
                    "min_new_tokens": int(os.getenv("WATSONX_MIN_TOKENS", "50")),
                    "stop_sequences": ["\n\nHuman:", "\n\nUser:"]
                }
            )
            
        except ImportError:
            # Fallback to basic response if IBM libraries not available
            return generate_fallback_response(details)
        
        # Initialize tools for web searching
        search_tool = SerperDevTool()
        scrape_tool = ScrapeWebsiteTool()
        
        # Create specialized agents with Chris personas
        chris_spots = Agent(
            role='Chris the Guy Who Knows the Spots',
            goal=f'Find all the coolest spots, hidden gems, and must-see places in {details["destination"]} for a {details["duration"]} trip that match {details["interests"]}',
            backstory=f"""You're Chris, the guy who literally knows every single spot worth visiting in {details["destination"]}. You've been living here for years, you know which places are tourist traps and which are the real deal. You've got friends who work at all the cool museums, you know the security guards who'll tell you the best photo spots, and you always know when places are having special events or are unexpectedly closed.

You're that friend who says "Oh, you're going to {details["destination"]}? Dude, you HAVE to check out this tiny place that locals go to" or "Skip the main tourist spot - I know a place with better views for half the price." You keep track of everything: opening times, how much stuff costs, when places get crowded, and you always have a backup plan because you actually live here.""",
            tools=[search_tool, scrape_tool],
            verbose=True,
            allow_delegation=False,
            llm=watsonx_llm
        )
        
        chef_chris = Agent(
            role='Chef Chris',
            goal=f'Find the absolute best food spots in {details["destination"]} that fit the vibe of {details["interests"]} and work with budget {details["budget"]}',
            backstory=f"""You're Chef Chris, and you've eaten at literally every restaurant worth going to in {details["destination"]}. You know the head chefs personally, you know which dishes to order, you know which places have gone downhill and which new spots are blowing up. You're not just about fancy restaurants - you know the street vendors who make the best local food, the hole-in-the-wall places with incredible value, and the high-end spots that are actually worth the money.

You're that friend who says "Forget that tourist place, I'm taking you to where the locals actually eat" and then takes you to some tiny place with no English menu but the best food of your life. You know when to make reservations, you know the secret menu items, and you always know the perfect restaurant for any time of day or mood.""",
            tools=[search_tool, scrape_tool],
            verbose=True,
            allow_delegation=False,
            llm=watsonx_llm
        )
        
        travel_guru_chris = Agent(
            role='Chris the Travel Guru',
            goal=f'Put together the perfect {details["duration"]} day-by-day game plan for {details["destination"]} that flows perfectly and stays within {details["budget"]}',
            backstory=f"""You're Chris the Travel Guru, the master of making everything work perfectly. You've planned hundreds of trips and you know exactly how to time everything so people have the best possible experience. You know that tourists always underestimate travel time, you know which activities work well together, and you know how to pace things so people don't get burned out.

You're that friend who takes the chaos of "I want to see everything" and turns it into "Here's your perfect day-by-day plan that actually makes sense." You account for jet lag, you know when places get crowded, you build in time for people to actually enjoy things instead of rushing around. You're obsessed with logistics - you know the subway systems, you know how long it really takes to get places, and you always have Plan B ready to go.""",
            verbose=True,
            allow_delegation=False,
            llm=watsonx_llm
        )
        
        # Create detailed tasks with Chris-style instructions
        spots_task = Task(
            description=f"""Yo Chris! I need you to find all the best spots in {details["destination"]} for someone who's into {details["interests"]}. I'm talking about the real deal - not just the tourist stuff everyone goes to.

Here's what I need you to research:
1. Search for current info about {details['destination']} attractions (2024 stuff only)
2. Find the spots that locals actually recommend, not just TripAdvisor top 10
3. Get the real details: when they're open, what it costs, how crowded it gets
4. Mix it up: some famous spots they gotta see + some hidden gems only you know about

I want you to find:
- The iconic stuff they absolutely can't miss (3-4 places)
- Cool museums or cultural spots that match their interests: {details['interests']} (3-4 places)
- Some local experiences or workshops that are unique to {details['destination']} (2-3 places)
- Good outdoor spots or viewpoints (2-3 places)
- Shopping or entertainment areas worth checking out (2-3 places)

For each spot, give me the real local knowledge, not guidebook fluff!""",
            agent=chris_spots,
            expected_output=f"Chris's insider guide to {details['destination']} with 12-15 verified spots including the must-sees and hidden gems, with real details, insider tips, and alternatives."
        )
        
        food_task = Task(
            description=f"""Chef Chris! I need your food expertise for {details["destination"]}. Find me the spots where people should actually eat - from the best street food to the places worth splurging on. Budget is {details["budget"]} and they're into {details["interests"]}.

Research mission:
1. Find the restaurants and food spots that are actually good right now (2024)
2. Check recent reviews and make sure places are still solid
3. Get the inside scoop on what to order and when to go
4. Find spots near the activities they'll be doing
5. Make sure it all works with their budget and interests

I want you to find:
- 1-2 iconic restaurants they absolutely have to try
- 3-4 amazing cheaper spots and street food (the real local stuff)
- 3-4 solid mid-range places with great food and good vibes
- 1-2 special occasion restaurants if they want to splurge
- 2-3 great breakfast/coffee spots
- 1-2 late-night options for when they're out exploring

Give me the real food scene, Chef Chris style!""",
            agent=chef_chris,
            expected_output=f"Chef Chris's definitive {details['destination']} food guide with 10-12 verified restaurants covering all meals, with current details, what to order, pricing, and insider food knowledge."
        )
        
        itinerary_task = Task(
            description=f"""Travel Guru Chris! Time to work your magic. Take all the spots and restaurants the other Chrises found and turn it into the perfect {details["duration"]} day-by-day plan for {details["destination"]}. Make it flow perfectly and keep it under {details["budget"]}.

Your mission:
1. Look at all the activities and restaurants they recommended
2. Group things by location so people aren't zigzagging across the city
3. Time everything right - busy attractions in the morning, chill spots in the evening
4. Make sure meals happen when locals eat, not tourist times
5. Build in travel time and rest breaks (people always underestimate this)
6. Have backup plans for everything

For each day, give me the Travel Guru Chris perfection with exact timing, logistics, costs, and backup plans!""",
            agent=travel_guru_chris,
            expected_output=f"Travel Guru Chris's masterpiece: a complete {details['duration']}-day {details['destination']} itinerary with hour-by-hour timing, exact logistics, costs, insider tips, and bulletproof backup plans.",
            context=[spots_task, food_task]
        )
        
        # Create crew and execute
        chris_crew = Crew(
            agents=[chris_spots, chef_chris, travel_guru_chris],
            tasks=[spots_task, food_task, itinerary_task],
            process=Process.sequential,
            verbose=True
        )
        
        # Execute the crew
        result = chris_crew.kickoff()
        
        # Format the result
        formatted_response = f"""🎪 **The Chris Team Results** (Powered by IBM watsonx.ai)

{result}

**🤖 Agent Collaboration Summary:**
✅ **Chris the Guy Who Knows the Spots**: Researched and discovered local experiences and attractions
✅ **Chef Chris**: Found and vetted dining recommendations with insider knowledge
✅ **Chris the Travel Guru**: Organized everything into your perfect day-by-day schedule

**📋 Trip Parameters:**
• Origin: {details['origin']}
• Destination: {details['destination']}
• Duration: {details['duration']}
• Budget: {details['budget']}
• Interests: {details['interests']}
• Hotel Preference: {details['hotel_preference']}

**🧠 Powered by IBM watsonx.ai Granite Models**
Enterprise-grade AI with real-time web research capabilities.

Ready for your adventure! 🌟"""
        
        return formatted_response
        
    except Exception as e:
        # Fallback to basic response if anything fails
        return generate_fallback_response(details, str(e))

def generate_fallback_response(details: Dict[str, str], error: str = None) -> str:
    """Fallback response if IBM watsonx.ai or CrewAI fails"""
    return f"""🎪 **Chris Team Travel Plan** (Basic Mode)

Your {details['duration']} adventure from {details['origin']} to {details['destination']} is ready!

**🗺️ General {details['destination']} Recommendations:**
• Research top attractions before you go
• Try local restaurants recommended by locals
• Download offline maps and translation apps
• Check visa requirements and local customs
• Book accommodations in advance
• Keep copies of important documents

**💰 Budget Planning for {details['duration']}:**
• Accommodation: 40% of budget ({details['budget']})
• Food: 30% of budget
• Activities: 20% of budget
• Transportation: 10% of budget

**🎯 Interests Focus: {details['interests']}**
Look for activities and restaurants that specifically cater to your interests.

**📋 Your Trip Details:**
• Destination: {details['destination']}
• Duration: {details['duration']}
• Budget: {details['budget']}
• Interests: {details['interests']}

**🤖 Agent Status:**
Chris team is in basic mode. For full AI-powered research, ensure IBM watsonx.ai credentials are properly configured.

{f"⚠️ Technical note: {error}" if error else ""}

Ready for your {details['destination']} adventure! 🌟"""

async def generate_streaming_response(response_text: str, request_id: str, model: str):
    """Generate streaming response chunks compatible with OpenAI format"""
    
    # Split response into words for streaming effect
    words = response_text.split()
    
    for i, word in enumerate(words):
        chunk_data = {
            "id": request_id,
            "object": "chat.completion.chunk",
            "created": int(datetime.now().timestamp()),
            "model": model,
            "choices": [{
                "index": 0,
                "delta": {
                    "content": word + " " if i < len(words) - 1 else word
                },
                "finish_reason": None
            }]
        }
        
        # Format as Server-Sent Events
        yield f"data: {json.dumps(chunk_data)}\n\n"
        await asyncio.sleep(0.05)  # Small delay for streaming effect
    
    # Final chunk to signal completion
    final_chunk = {
        "id": request_id,
        "object": "chat.completion.chunk", 
        "created": int(datetime.now().timestamp()),
        "model": model,
        "choices": [{
            "index": 0,
            "delta": {},
            "finish_reason": "stop"
        }]
    }
    
    yield f"data: {json.dumps(final_chunk)}\n\n"
    yield "data: [DONE]\n\n"

@app.post("/chat/completions")
async def chat_completions(request: ChatCompletionRequest):
    """
    IBM watsonx.ai compatible chat completions endpoint for watsonx Orchestrate
    """
    try:
        # Extract travel details from messages
        details = extract_travel_details(request.messages)
        
        # Generate response using IBM watsonx.ai and CrewAI
        response_text = generate_travel_response(details)
        
        request_id = f"chatcmpl-{uuid.uuid4().hex[:8]}"
        created_time = int(datetime.now().timestamp())
        
        if request.stream:
            # Return streaming response
            return StreamingResponse(
                generate_streaming_response(response_text, request_id, request.model or "ibm/granite-13b-chat-v2"),
                media_type="text/plain",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                    "Content-Type": "text/plain; charset=utf-8"
                }
            )
        else:
            # Return complete response
            response = ChatCompletionResponse(
                id=request_id,
                created=created_time,
                model=request.model or "ibm/granite-13b-chat-v2",
                choices=[
                    ChatCompletionChoice(
                        index=0,
                        message=ChatMessage(role="assistant", content=response_text),
                        finish_reason="stop"
                    )
                ]
            )
            return response
            
    except Exception as e:
        # Return error in OpenAI format
        error_response = ChatCompletionResponse(
            id=f"chatcmpl-error-{uuid.uuid4().hex[:8]}",
            created=int(datetime.now().timestamp()),
            model=request.model or "ibm/granite-13b-chat-v2",
            choices=[
                ChatCompletionChoice(
                    index=0,
                    message=ChatMessage(role="assistant", content=f"❌ Error processing travel request: {str(e)}"),
                    finish_reason="stop"
                )
            ]
        )
        return error_response

# Keep original endpoint for direct testing
@app.post("/plan-surprise-trip")
async def plan_surprise_trip(request: Dict[str, Any]):
    """Legacy endpoint for direct testing"""
    try:
        # Extract fields
        origin = request.get('origin', 'Boston')
        destination = request.get('destination', 'Unknown')
        age = str(request.get('age', '25'))
        interests = request.get('interests', 'general travel')
        budget = request.get('budget', '$2000')
        duration = request.get('trip_duration') or request.get('duration', '3 days')
        hotel_pref = request.get('hotel_preference', 'standard')
        
        details = {
            'origin': origin,
            'destination': destination,
            'age': age,
            'interests': interests,
            'budget': budget,
            'duration': duration,
            'hotel_preference': hotel_pref
        }
        
        return generate_travel_response(details)
        
    except Exception as e:
        return f"❌ Error: {str(e)}"

@app.get("/health")
async def health():
    return {
        "status": "healthy", 
        "agents_ready": True, 
        "endpoints": ["/chat/completions", "/plan-surprise-trip"],
        "llm_provider": "IBM watsonx.ai",
        "model": "ibm/granite-13b-chat-v2",
        "version": "1.0.0-ibm"
    }

@app.get("/")
async def root():
    return {
        "service": "AI Travel Planning Team - IBM watsonx.ai Edition",
        "version": "1.0.0-ibm",
        "watsonx_compatible": True,
        "llm_provider": "IBM watsonx.ai",
        "model": "ibm/granite-13b-chat-v2",
        "agents": ["Chris the Guy Who Knows the Spots", "Chef Chris", "Chris the Travel Guru"],
        "endpoints": {
            "chat_completions": "/chat/completions",
            "legacy": "/plan-surprise-trip",
            "health": "/health",
            "docs": "/docs"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)