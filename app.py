"""
Streamlit UI for the Travel Itinerary Planner multi-agent system.
This module provides a user-friendly interface for the travel planner.
"""

import os
import streamlit as st
from datetime import datetime, timedelta
import time
from main import TravelPlannerSystem

# Set page configuration
st.set_page_config(
    page_title="AI Travel Itinerary Planner",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E88E5;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #0D47A1;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    .info-box {
        background-color: #E3F2FD;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .success-box {
        background-color: #E8F5E9;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .stProgress > div > div > div {
        background-color: #1E88E5;
    }
</style>
""", unsafe_allow_html=True)

def main():
    """Main function to run the Streamlit app."""
    
    # Header
    st.markdown("<h1 class='main-header'>🌍 AI Travel Itinerary Planner</h1>", unsafe_allow_html=True)
    st.markdown("""
    <div class='info-box'>
    This application uses a multi-agent AI system to create personalized travel itineraries.
    Simply fill in your travel preferences, and our AI agents will collaborate to plan your perfect trip!
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar for API keys
    with st.sidebar:
        st.markdown("### API Configuration")
        openai_api_key = st.text_input("OpenAI API Key", type="password", help="Required for agent communication")
        exa_api_key = st.text_input("Exa API Key (Optional)", type="password", help="For enhanced search capabilities")
        
        st.markdown("### About")
        st.markdown("""
        This application demonstrates a multi-agent AI system using:
        - CrewAI for agent orchestration
        - OpenAI for language processing
        - Streamlit for the user interface
        
        Each specialized AI agent handles a different aspect of travel planning:
        - Destination Research
        - Accommodation Selection
        - Activities Planning
        - Transportation Coordination
        - Itinerary Compilation
        """)
    
    # Main form
    with st.form("travel_preferences_form"):
        st.markdown("<h2 class='sub-header'>Your Travel Preferences</h2>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            destination = st.text_input("Destination", help="Leave blank for AI to suggest destinations")
            
            # Date selection with validation
            today = datetime.now()
            start_date = st.date_input("Start Date", today + timedelta(days=30), min_value=today)
            end_date = st.date_input("End Date", start_date + timedelta(days=7), min_value=start_date)
            
            travelers = st.number_input("Number of Travelers", min_value=1, max_value=10, value=2)
            
        with col2:
            budget_options = ["Budget", "Mid-range", "Luxury", "No preference"]
            budget = st.selectbox("Budget Range", budget_options)
            
            interests = st.multiselect(
                "Interests",
                ["Nature", "Culture", "Food", "Adventure", "History", "Art", "Shopping", "Relaxation", "Nightlife", "Family-friendly"],
                default=["Culture", "Food"]
            )
            
            accommodation_options = ["Hotel", "Hostel", "Resort", "Apartment/Airbnb", "No preference"]
            accommodation = st.selectbox("Preferred Accommodation Type", accommodation_options)
            
            transportation_options = ["Public Transit", "Rental Car", "Walking/Biking", "Taxis/Rideshares", "No preference"]
            transportation = st.selectbox("Preferred Transportation", transportation_options)
        
        # Additional preferences
        st.markdown("<h3 class='sub-header'>Additional Details</h3>", unsafe_allow_html=True)
        additional_preferences = st.text_area("Any additional preferences or requirements?", 
                                             placeholder="E.g., accessibility needs, dietary restrictions, must-see attractions...")
        
        # Submit button
        submitted = st.form_submit_button("Generate Travel Itinerary")
    
    # Process form submission
    if submitted:
        # Validate API key
        if not openai_api_key:
            st.error("Please enter your OpenAI API key in the sidebar.")
            return
        
        # Set API keys as environment variables
        os.environ["OPENAI_API_KEY"] = openai_api_key
        if exa_api_key:
            os.environ["EXA_API_KEY"] = exa_api_key
        
        # Format inputs for the planner
        formatted_interests = ", ".join(interests)
        formatted_budget = f"{budget} (please provide specific recommendations within this range)"
        formatted_accommodation = f"{accommodation}, with consideration for location and amenities"
        formatted_transportation = f"{transportation}, optimized for convenience and cost"
        
        if additional_preferences:
            formatted_interests += f". Additional preferences: {additional_preferences}"
        
        # Display progress
        st.markdown("<h2 class='sub-header'>Generating Your Travel Itinerary</h2>", unsafe_allow_html=True)
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Initialize the travel planner system
        try:
            planner = TravelPlannerSystem(verbose=False)
            
            # Update progress
            progress_bar.progress(10)
            status_text.text("✅ AI agents initialized")
            time.sleep(1)
            
            # Show the planning process with simulated progress updates
            status_text.text("🔍 Researching destinations and gathering information...")
            progress_bar.progress(20)
            time.sleep(1)
            
            status_text.text("🏨 Finding the best accommodation options...")
            progress_bar.progress(40)
            time.sleep(1)
            
            status_text.text("🎭 Discovering activities and attractions...")
            progress_bar.progress(60)
            time.sleep(1)
            
            status_text.text("🚆 Planning transportation logistics...")
            progress_bar.progress(80)
            time.sleep(1)
            
            status_text.text("📝 Compiling your personalized itinerary...")
            progress_bar.progress(90)
            
            # Run the actual planning process
            result = planner.plan_trip(
                destination=destination,
                start_date=start_date.strftime("%Y-%m-%d"),
                end_date=end_date.strftime("%Y-%m-%d"),
                budget=formatted_budget,
                interests=formatted_interests,
                accommodation_preferences=formatted_accommodation,
                transportation_preferences=formatted_transportation,
                travelers=f"{travelers} {'person' if travelers == 1 else 'people'}"
            )
            
            # Complete progress
            progress_bar.progress(100)
            status_text.text("✅ Your travel itinerary is ready!")
            
            # Display the result
            st.markdown("<h2 class='sub-header'>Your Personalized Travel Itinerary</h2>", unsafe_allow_html=True)
            st.markdown("""
            <div class='success-box'>
            Your travel itinerary has been generated successfully! You can view it below or download it as a markdown file.
            </div>
            """, unsafe_allow_html=True)
            
            # Display the itinerary in a nice format
            st.markdown(result)
            
            # Provide download option
            st.download_button(
                label="Download Itinerary",
                data=result,
                file_name=f"travel_itinerary_{datetime.now().strftime('%Y%m%d')}.md",
                mime="text/markdown"
            )
            
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
            st.markdown("""
            <div class='info-box'>
            <strong>Troubleshooting:</strong><br>
            - Check your API key and internet connection<br>
            - Try again with different preferences<br>
            - If the problem persists, try again later
            </div>
            """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
