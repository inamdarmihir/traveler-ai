"""
Task definitions for the Travel Itinerary Planner multi-agent system.
This module defines specialized tasks for each agent in the travel planning process.
"""

from crewai import Task
from typing import List, Dict, Any, Optional

def create_tasks(agents, destination=None, start_date=None, end_date=None, budget=None, 
                 interests=None, accommodation_preferences=None, 
                 transportation_preferences=None, travelers=None):
    """
    Create and return all tasks needed for the travel itinerary planning system.
    
    Args:
        agents: Dictionary containing all agent instances
        destination: Destination for the trip (optional)
        start_date: Start date of the trip
        end_date: End date of the trip
        budget: Budget for the trip
        interests: Traveler interests
        accommodation_preferences: Accommodation preferences
        transportation_preferences: Transportation preferences
        travelers: Number of travelers
        
    Returns:
        List of Task objects representing the workflow
    """
    # Task 1: Research destination
    destination_research_task = Task(
        description=f"""Research {destination if destination else 'potential travel destinations'} 
        based on the following criteria:
        - Travel dates: {start_date} to {end_date}
        - Budget: {budget}
        - Interests: {interests}
        - Number of travelers: {travelers}
        
        If no specific destination is provided, recommend 3 suitable destinations that match the criteria.
        For each destination, provide:
        1. Overview of the destination
        2. Best time to visit and current weather/seasonal considerations
        3. Cultural highlights and unique aspects
        4. Safety information and travel advisories
        5. Estimated overall costs
        6. Visa requirements if applicable
        
        Your research should be thorough and up-to-date.
        """,
        agent=agents["destination_researcher"],
        expected_output="A comprehensive report on the destination(s) with all requested information."
    )
    
    # Task 2: Find accommodation options
    accommodation_task = Task(
        description=f"""Based on the destination research, find the best accommodation options that match these criteria:
        - Location: {destination if destination else 'To be determined based on destination research'}
        - Check-in date: {start_date}
        - Check-out date: {end_date}
        - Budget: {budget}
        - Preferences: {accommodation_preferences}
        - Number of travelers: {travelers}
        
        For each recommended accommodation, provide:
        1. Name, type (hotel, hostel, apartment, etc.), and location
        2. Price range and value assessment
        3. Amenities and features
        4. Proximity to attractions/city center
        5. Guest ratings and reviews summary
        6. Any special considerations (e.g., accessibility, family-friendliness)
        
        Recommend at least 3 options at different price points when possible.
        """,
        agent=agents["accommodation_specialist"],
        expected_output="A detailed list of accommodation options with all requested information.",
        context=[destination_research_task]
    )
    
    # Task 3: Plan activities and attractions
    activities_task = Task(
        description=f"""Based on the destination research, create a comprehensive list of activities and attractions that match these criteria:
        - Location: {destination if destination else 'To be determined based on destination research'}
        - Travel dates: {start_date} to {end_date}
        - Interests: {interests}
        - Budget considerations: {budget}
        - Number of travelers: {travelers}
        
        For each recommended activity or attraction, provide:
        1. Name and type of activity/attraction
        2. Location and how to get there
        3. Recommended duration
        4. Cost (entry fees, guided tours, etc.)
        5. Booking requirements (advance tickets, reservations)
        6. Best time to visit (time of day, day of week)
        7. Insider tips or special considerations
        
        Include a mix of popular attractions and hidden gems. Consider seasonal events or festivals happening during the travel dates.
        """,
        agent=agents["activities_planner"],
        expected_output="A comprehensive list of activities and attractions with all requested information.",
        context=[destination_research_task]
    )
    
    # Task 4: Plan transportation
    transportation_task = Task(
        description=f"""Based on the destination research, plan the most efficient transportation options for this trip:
        - Origin to destination transportation (if needed)
        - Local transportation within the destination
        - Transportation between accommodations and activities
        
        Consider these factors:
        - Travel dates: {start_date} to {end_date}
        - Budget: {budget}
        - Preferences: {transportation_preferences}
        - Number of travelers: {travelers}
        
        For each transportation recommendation, provide:
        1. Type of transportation (flight, train, bus, rental car, etc.)
        2. Estimated costs
        3. Booking information and tips
        4. Schedules and duration
        5. Convenience and comfort assessment
        6. Any special considerations (e.g., accessibility, luggage restrictions)
        
        Include both transportation to/from the destination and local transportation options.
        """,
        agent=agents["transportation_coordinator"],
        expected_output="A detailed transportation plan with all requested information.",
        context=[destination_research_task, activities_task]
    )
    
    # Task 5: Compile final itinerary
    itinerary_task = Task(
        description=f"""Compile all the research and recommendations into a comprehensive day-by-day travel itinerary:
        - Travel dates: {start_date} to {end_date}
        - Destination: {destination if destination else 'As determined by research'}
        
        The itinerary should include:
        1. A brief overview of the trip
        2. Day-by-day schedule with:
           - Accommodations
           - Activities and attractions with timing
           - Transportation details
           - Meal suggestions or reservations
           - Free time blocks
        3. Estimated costs breakdown
        4. Packing suggestions based on activities and weather
        5. Important contact information and emergency resources
        
        The itinerary should be realistic, well-paced, and consider travel times between locations. 
        Balance scheduled activities with free time for relaxation or spontaneous exploration.
        """,
        agent=agents["itinerary_compiler"],
        expected_output="A complete day-by-day travel itinerary with all requested information.",
        context=[destination_research_task, accommodation_task, activities_task, transportation_task]
    )
    
    return [destination_research_task, accommodation_task, activities_task, transportation_task, itinerary_task]
