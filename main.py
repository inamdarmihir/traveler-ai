import os
import sys

# Add this at the top of main.py
# This will prevent ChromaDB from being imported
os.environ["CREWAI_DISABLE_MEMORY"] = "true"

# Rest of your imports
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
        
        # Create output directory if it doesn't exist
        os.makedirs("travel_plans", exist_ok=True)
    
    def initialize(self, travel_preferences):
        """
        Initialize the agents, tasks, and crew based on travel preferences.
        
        Args:
            travel_preferences: Dictionary containing user's travel preferences.
        """
        # Create agents
        self.agents = create_agents(verbose=self.verbose)
        
        # Create tasks with the travel preferences
        self.tasks = create_tasks(self.agents, travel_preferences)
        
        # Create the crew
        self.crew = Crew(
            agents=list(self.agents.values()),
            tasks=self.tasks,
            verbose=self.verbose,
            process=Process.sequential  # Tasks will be executed in sequence
        )
    
    def kickoff(self, travel_preferences):
        """
        Start the travel planning process.
        
        Args:
            travel_preferences: Dictionary containing user's travel preferences.
            
        Returns:
            The final travel itinerary as a string.
        """
        # Initialize the system
        self.initialize(travel_preferences)
        
        # Run the crew to generate the itinerary
        result = self.crew.kickoff()
        
        # Save the itinerary to a file
        filename = self._save_itinerary(result, travel_preferences)
        
        return result, filename
        
    def plan_trip(self, destination, start_date, end_date, budget, interests, accommodation_preferences, transportation_preferences, travelers):
        """
        Plan a trip based on the provided parameters.
        This method is used by the Streamlit app.
        
        Args:
            destination: The destination for the trip.
            start_date: The start date of the trip.
            end_date: The end date of the trip.
            budget: The budget for the trip.
            interests: The interests for activities.
            accommodation_preferences: Preferences for accommodation.
            transportation_preferences: Preferences for transportation.
            travelers: Number of travelers.
            
        Returns:
            The final travel itinerary as a string.
        """
        # Format the travel preferences
        travel_dates = f"{start_date} to {end_date}"
        start_date_obj = datetime.strptime(start_date, "%Y-%m-%d")
        end_date_obj = datetime.strptime(end_date, "%Y-%m-%d")
        duration = (end_date_obj - start_date_obj).days
        
        travel_preferences = {
            "destination": destination,
            "travel_dates": travel_dates,
            "duration": f"{duration} days",
            "budget": budget,
            "travelers": travelers,
            "interests": interests.split(", "),
            "accommodation_type": accommodation_preferences,
            "transportation": transportation_preferences
        }
        
        # Use the existing kickoff method
        result, _ = self.kickoff(travel_preferences)
        
        return result
    
    def _save_itinerary(self, itinerary, preferences):
        """
        Save the generated itinerary to a file.
        
        Args:
            itinerary: The generated travel itinerary as a string.
            preferences: Dictionary containing user's travel preferences.
            
        Returns:
            The filename of the saved itinerary.
        """
        # Create a filename based on destination and date
        destination = preferences.get("destination", "Custom")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"travel_plans/{destination.replace(' ', '_')}_{timestamp}.md"
        
        # Add a header with the travel preferences
        header = "# Travel Itinerary\n\n"
        header += "## Travel Preferences\n\n"
        
        for key, value in preferences.items():
            formatted_key = key.replace('_', ' ').title()
            if isinstance(value, list):
                formatted_value = ", ".join(value)
            else:
                formatted_value = str(value)
            header += f"- **{formatted_key}:** {formatted_value}\n"
        
        header += "\n## Itinerary\n\n"
        
        # Write the itinerary to the file
        with open(filename, "w", encoding="utf-8") as f:
            f.write(header + itinerary)
        
        return filename

# Example usage
if __name__ == "__main__":
    # Example travel preferences
    example_preferences = {
        "destination": "Japan",
        "travel_dates": "June 10-20, 2024",
        "duration": "10 days",
        "budget": "$3000 USD",
        "travelers": "2 adults",
        "interests": ["culture", "food", "nature", "history"],
        "accommodation_type": "mid-range hotels",
        "pace": "moderate"
    }
    
    # Create and run the travel planner
    planner = TravelPlannerSystem(verbose=True)
    itinerary, filename = planner.kickoff(example_preferences)
    
    print(f"\nTravel itinerary saved to: {filename}")
    print("\nItinerary Preview:")
    print(itinerary[:500] + "...")
