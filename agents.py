"""
Agent definitions for the Travel Itinerary Planner multi-agent system.
This module defines specialized agents with distinct roles in the travel planning process.
"""

from crewai import Agent
from langchain_openai import ChatOpenAI
from typing import List, Optional
from tools import DuckDuckGoSearchTool, ExaSearchTool, WebsiteSearchTool, WeatherInfoTool

def create_agents(llm=None, verbose=True):
    """
    Create and return all agents needed for the travel itinerary planning system.
    
    Args:
        llm: Language model to use for the agents. If None, will use OpenAI's GPT model.
        verbose: Whether to enable verbose mode for the agents.
        
    Returns:
        Dictionary containing all agent instances.
    """
    # Initialize the language model if not provided
    if llm is None:
        try:
            llm = ChatOpenAI(model="gpt-4o", temperature=0.7)
        except Exception as e:
            print(f"Error initializing OpenAI model: {e}")
            print("Falling back to gpt-3.5-turbo...")
            llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.7)
    
    # Initialize tools
    search_tools = []
    try:
        search_tools.append(ExaSearchTool())
        print("✅ Exa search tool initialized")
    except Exception as e:
        print(f"⚠️ Exa search tool not available: {e}")
    
    try:
        search_tools.append(DuckDuckGoSearchTool())
        print("✅ DuckDuckGo search tool initialized")
    except Exception as e:
        print(f"⚠️ DuckDuckGo search tool not available: {e}")
    
    website_search_tool = WebsiteSearchTool()
    weather_tool = WeatherInfoTool()
    
    # Ensure we have at least one search tool
    if not search_tools:
        raise ValueError("No search tools available. Please install either exa-py or duckduckgo-search.")
    
    # 1. Destination Research Agent
    destination_researcher = Agent(
        role="Travel Destination Researcher",
        goal="Find the best destinations based on traveler preferences and provide detailed information about each location",
        backstory="""You are an expert travel researcher with extensive knowledge of global destinations. 
        You have visited over 100 countries and have a deep understanding of different cultures, 
        climates, and travel experiences. Your recommendations are always well-researched and tailored 
        to the traveler's specific interests and constraints.""",
        verbose=verbose,
        allow_delegation=True,
        tools=search_tools + [website_search_tool, weather_tool],
        llm=llm
    )

    # 2. Accommodation Specialist Agent
    accommodation_specialist = Agent(
        role="Accommodation Specialist",
        goal="Find the best accommodation options based on traveler preferences, budget, and location",
        backstory="""You are a hotel and accommodation expert who has worked in the hospitality 
        industry for over 15 years. You have connections with hotels, resorts, and vacation 
        rental properties worldwide. You know how to find the perfect place to stay that 
        balances comfort, convenience, and budget.""",
        verbose=verbose,
        allow_delegation=True,
        tools=search_tools + [website_search_tool],
        llm=llm
    )

    # 3. Activities Planner Agent
    activities_planner = Agent(
        role="Activities and Attractions Planner",
        goal="Create a comprehensive list of activities, attractions, and experiences tailored to the traveler's interests",
        backstory="""You are a local experiences expert who specializes in finding unique and 
        authentic activities for travelers. You have a knack for discovering hidden gems and 
        can recommend both popular tourist attractions and off-the-beaten-path experiences. 
        You consider the traveler's interests, physical abilities, and time constraints.""",
        verbose=verbose,
        allow_delegation=True,
        tools=search_tools + [website_search_tool],
        llm=llm
    )

    # 4. Transportation Coordinator Agent
    transportation_coordinator = Agent(
        role="Transportation Coordinator",
        goal="Plan the most efficient and convenient transportation options for the entire trip",
        backstory="""You are a transportation logistics expert who can navigate complex 
        transportation systems worldwide. You know the best ways to get around in different 
        cities and countries, whether by public transit, rental car, or private transfers. 
        You optimize for convenience, cost, and time efficiency.""",
        verbose=verbose,
        allow_delegation=True,
        tools=search_tools + [website_search_tool],
        llm=llm
    )

    # 5. Itinerary Compiler Agent
    itinerary_compiler = Agent(
        role="Itinerary Compiler and Optimizer",
        goal="Compile all research and recommendations into a cohesive, day-by-day travel itinerary",
        backstory="""You are a master travel planner who excels at creating detailed, 
        well-organized itineraries. You know how to balance activities with downtime, 
        account for travel logistics, and create realistic schedules. Your itineraries 
        are always clear, comprehensive, and easy to follow.""",
        verbose=verbose,
        allow_delegation=True,
        tools=[],  # This agent primarily synthesizes information from other agents
        llm=llm
    )
    
    # Return all agents as a dictionary for easy access
    return {
        "destination_researcher": destination_researcher,
        "accommodation_specialist": accommodation_specialist,
        "activities_planner": activities_planner,
        "transportation_coordinator": transportation_coordinator,
        "itinerary_compiler": itinerary_compiler
    }
