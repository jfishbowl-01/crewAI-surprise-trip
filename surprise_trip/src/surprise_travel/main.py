#!/usr/bin/env python
import sys
import json
from surprise_travel.crew import SurpriseTravelCrew

def display_itinerary(result):
    """Display the itinerary in a beautiful, readable format"""
    
    # Handle different result types
    itinerary = None
    
    if hasattr(result, 'json_dict') and result.json_dict:
        itinerary = result.json_dict
    elif hasattr(result, 'raw') and result.raw:
        try:
            itinerary = json.loads(result.raw)
        except:
            itinerary = None
    elif isinstance(result, dict):
        itinerary = result
    elif isinstance(result, str):
        try:
            itinerary = json.loads(result)
        except:
            itinerary = None
    
    # If we couldn't parse the itinerary, show what we got
    if not itinerary:
        print("\n" + "="*80)
        print("🎪 YOUR SURPRISE TRIP RESULTS")
        print("="*80)
        print(f"\n📋 Raw Result: {result}")
        return
    
    print("\n" + "="*80)
    print(f"🎪 {itinerary.get('name', 'YOUR SURPRISE ADVENTURE').upper()}")
    print("="*80)
    
    # Hotel information
    if itinerary.get('hotel'):
        print(f"\n🏨 ACCOMMODATION")
        print(f"   {itinerary['hotel']}")
    
    # Day by day itinerary
    day_plans = itinerary.get('day_plans', [])
    if not day_plans:
        print("\n⚠️  No day plans found in the itinerary")
        return
        
    for i, day in enumerate(day_plans, 1):
        print(f"\n📅 DAY {i}: {day.get('date', f'Day {i}').upper()}")
        print("-" * 60)
        
        # Flight info
        if day.get('flight'):
            print(f"✈️  FLIGHT: {day['flight']}")
            print()
        
        # Activities
        activities = day.get('activities', [])
        if activities:
            for activity in activities:
                print(f"🎯 {activity.get('name', 'Activity')}")
                print(f"   📍 Location: {activity.get('location', 'TBD')}")
                print(f"   📝 {activity.get('description', 'No description')}")
                
                # Rating with stars
                if activity.get('rating'):
                    rating = float(activity['rating'])
                    stars = "⭐" * int(rating)
                    print(f"   {stars} {rating}/5.0")
                
                # Reviews
                reviews = activity.get('reviews', activity.get('review', []))
                if reviews and len(reviews) > 0:
                    print(f"   💬 \"{reviews[0]}\"")
                print()
        
        # Restaurants
        restaurants = day.get('restaurants', [])
        if restaurants:
            print("🍽️  DINING OPTIONS:")
            for restaurant in restaurants:
                print(f"   • {restaurant}")
            print()
        
        # Add separator between days
        if i < len(day_plans):
            print("─" * 60)

def run():
    print("🎪 Welcome to Your AI Travel Planning Team!")
    print("=" * 60)
    print("Our specialized agents will collaborate to create your perfect surprise trip\n")
    
    # Collect user inputs with better prompts
    print("Let's start with some basic information:")
    origin = input("🛫 Where are you traveling from? ")
    destination = input("🌍 Where would you like to go? ")
    interests = input("✨ What are your travel interests and preferences? ")
    budget = input("💰 What's your budget for this trip? ")
    dates = input("📅 When would you like to travel? ")
    
    # Additional preferences
    print("\n🎯 A few more questions to personalize your experience:")
    age = input("🎂 What's your age? (helps us find age-appropriate activities) ")
    pace = input("⚡ Preferred pace (relaxed/moderate/packed)? ")
    accommodation = input("🏨 Hotel style preference (luxury/boutique/budget)? ")
    duration = input("⏰ How long is your trip? (e.g., 7 days, 10 days) ")
    special = input("🎉 Any special occasions or must-see experiences? ")
    
    # Prepare inputs with the EXACT variable names the tasks expect
    inputs = {
        'origin': origin,
        'destination': destination,
        'age': age,
        'hotel_location': f"{accommodation} hotel in {destination}",
        'flight_information': f"Round-trip flights from {origin} to {destination} on {dates}",
        'trip_duration': duration
    }
    
    print("\n" + "="*60)
    print("🤖 AI AGENTS STARTING COLLABORATION")
    print("="*60)
    
    # Show progress as agents work
    print(f"\n🎯 Activity Planner: Researching amazing experiences in {destination}...")
    print("🔍 Searching for unique activities and events...")
    
    print(f"\n🍽️ Restaurant Scout: Finding incredible dining spots in {destination}...")
    print("🔍 Analyzing reviews and finding hidden gems...")
    
    print(f"\n📋 Itinerary Compiler: Creating your {duration} itinerary...")
    print("🔍 Coordinating flights, hotels, and logistics...\n")
    
    # Run the crew
    crew = SurpriseTravelCrew()
    result = crew.crew().kickoff(inputs=inputs)
    
    # Display beautiful results
    print(f"\n🎉 YOUR SURPRISE TRIP TO {destination.upper()} IS READY!")
    display_itinerary(result)
    
    return result

if __name__ == "__main__":
    run()