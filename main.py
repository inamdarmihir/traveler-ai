"""
Main module for the Travel Itinerary Planner multi-agent system.
This module orchestrates the agents and tasks to create a travel itinerary.
"""

import os
import json
from datetime import datetime
from dotenv import load_dotenv
from crewai import Crew, Process
from agents import create_agents
from tasks import create_tasks

# Load environment variables
load_dotenv()

class TravelPlannerSystem:
    """
    Main class for the Travel Itinerary Planner system.
    Orchestrates the agents and tasks to create a travel itinerary.
    """
    
    def __init__(self, verbose=True):
        """
        Initialize the Travel Planner System.
        
        Args:
            verbose: Whether to enable verbose mode for the agents and crew.
        """
        self.verbose = verbose
        self.agents = None
        self.tasks = None
        self.crew = None
        self.result = None
        
        # Initialize agents
        try:
            self.agents = create_agents(verbose=verbose)
            print("✅ Agents initialized successfully")
        except Exception as e:
            print(f"❌ Error initializing agents: {e}")
            raise
    
    def plan_trip(self, destination=None, start_date=None, end_date=None, budget=None, 
                 interests=None, accommodation_preferences=None, 
                 transportation_preferences=None, travelers=None):
        """
        Plan a trip based on the provided parameters.
        
        Args:
            destination: Destination for the trip (optional)
            start_date: Start date of the trip
            end_date: End date of the trip
            budget: Budget for the trip
            interests: Traveler interests
            accommodation_preferences: Accommodation preferences
            transportation_preferences: Transportation preferences
            travelers: Number of travelers
            
        Returns:
            The final travel itinerary as a string.
        """
        try:
            # Create tasks
            self.tasks = create_tasks(
                self.agents,
                destination=destination,
                start_date=start_date,
                end_date=end_date,
                budget=budget,
                interests=interests,
                accommodation_preferences=accommodation_preferences,
                transportation_preferences=transportation_preferences,
                travelers=travelers
            )
            print("✅ Tasks created successfully")
            
            # Create crew
            self.crew = Crew(
                agents=list(self.agents.values()),
                tasks=self.tasks,
                verbose=self.verbose,
                process=Process.sequential  # Use sequential process for predictable workflow
            )
            print("✅ Crew initialized successfully")
            
            # Run the crew
            print("🚀 Starting travel planning process...")
            self.result = self.crew.kickoff()
            
            # Save the result
            self._save_result(destination)
            
            return self.result
            
        except Exception as e:
            print(f"❌ Error planning trip: {e}")
            raise
    
    def _save_result(self, destination):
        """
        Save the result to a file.
        
        Args:
            destination: Destination for the trip, used in the filename.
        """
        if not self.result:
            return
        
        try:
            # Create directory if it doesn't exist
            os.makedirs("travel_plans", exist_ok=True)
            
            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            dest_str = destination.replace(" ", "_") if destination else "trip"
            filename = f"travel_plans/{dest_str}_{timestamp}.md"
            
            # Save to file
            with open(filename, "w") as f:
                f.write(self.result)
            
            print(f"✅ Travel plan saved to {filename}")
            return filename
        except Exception as e:
            print(f"⚠️ Error saving result: {e}")
            return None

# Example usage
if __name__ == "__main__":
    # Initialize the system
    planner = TravelPlannerSystem(verbose=True)
    
    # Example trip parameters
    result = planner.plan_trip(
        destination="Tokyo, Japan",
        start_date="2025-06-15",
        end_date="2025-06-22",
        budget="Medium (around $2000 per person)",
        interests="Technology, Food, Culture, Shopping",
        accommodation_preferences="Mid-range hotel or Airbnb, central location",
        transportation_preferences="Public transit, walking",
        travelers="2 adults"
    )
    
    print("\n==== FINAL ITINERARY ====\n")
    print(result)
