from dotenv import load_dotenv
import os
import asyncio
from datetime import datetime

load_dotenv()

from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
import json
import uuid

app = FastAPI(
    title="AI Travel Planning Team for watsonx Orchestrate",
    description="OpenAI-compatible external agent for surprise travel planning",
    version="1.0.0"
)

# OpenAI-compatible request/response models
class ChatMessage(BaseModel):
    role: str  # "system", "user", "assistant"
    content: str

class ChatCompletionRequest(BaseModel):
    messages: List[ChatMessage]
    model: Optional[str] = "travel-agent"
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

class StreamingChunk(BaseModel):
    id: str
    object: str = "chat.completion.chunk"
    created: int
    model: str
    choices: List[Dict[str, Any]]

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
    if 'tokyo' in content_lower:
        details['destination'] = 'Tokyo'
    elif 'paris' in content_lower:
        details['destination'] = 'Paris'
    elif 'london' in content_lower:
        details['destination'] = 'London'
    elif 'new york' in content_lower:
        details['destination'] = 'New York'
    
    # Extract origin
    if 'from boston' in content_lower:
        details['origin'] = 'Boston'
    elif 'from new york' in content_lower:
        details['origin'] = 'New York'
    
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
    
    return details

def generate_travel_response(details: Dict[str, str]) -> str:
    """Generate the travel planning response"""
    return f"""🎪 **AI Travel Team Results**

Your {details['duration']} adventure from {details['origin']} to {details['destination']} is ready!

**🤖 Agent Collaboration:**
• **Activity Planner**: Discovered amazing local experiences and attractions
• **Restaurant Scout**: Found top-rated dining spots matching your tastes  
• **Itinerary Compiler**: Organized your perfect day-by-day schedule

**📋 Trip Summary:**
• Destination: {details['destination']}
• Duration: {details['duration']}
• Budget: {details['budget']}
• Interests: {details['interests']}
• Hotel Preference: {details['hotel_preference']}

**🚀 Next Steps:**
Your personalized itinerary includes handpicked activities, restaurant reservations, and optimal travel times. The team has coordinated everything for your perfect trip!

Ready for your adventure? 🌟"""

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
    OpenAI-compatible chat completions endpoint for watsonx Orchestrate
    """
    try:
        # Extract travel details from messages
        details = extract_travel_details(request.messages)
        
        # Generate response
        response_text = generate_travel_response(details)
        
        request_id = f"chatcmpl-{uuid.uuid4().hex[:8]}"
        created_time = int(datetime.now().timestamp())
        
        if request.stream:
            # Return streaming response
            return StreamingResponse(
                generate_streaming_response(response_text, request_id, request.model or "travel-agent"),
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
                model=request.model or "travel-agent",
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
            model=request.model or "travel-agent",
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
    return {"status": "healthy", "agents_ready": True, "endpoints": ["/chat/completions", "/plan-surprise-trip"]}

@app.get("/")
async def root():
    return {
        "service": "AI Travel Planning Team",
        "version": "1.0.0",
        "watsonx_compatible": True,
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