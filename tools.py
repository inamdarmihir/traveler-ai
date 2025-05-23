"""
Custom tools for the Travel Itinerary Planner multi-agent system.
This module provides alternative search tools to replace SerperDevTool.
"""

import os
import json
import requests
from typing import Type, Optional, List, Dict, Any
from pydantic import BaseModel, Field
from crewai.tools import BaseTool
from bs4 import BeautifulSoup
from dotenv import load_dotenv

# Try to import Exa for semantic search
try:
    from exa_py import Exa
    HAS_EXA = True
except ImportError:
    HAS_EXA = False

# Try to import DuckDuckGo search
try:
    from duckduckgo_search import DDGS
    HAS_DDGS = True
except ImportError:
    HAS_DDGS = False

# Load environment variables
load_dotenv()

class SearchQuery(BaseModel):
    """Input schema for search tools."""
    query: str = Field(description="Search query string")

class WebsiteQuery(BaseModel):
    """Input schema for website search tools."""
    url: str = Field(description="URL of the website to search")
    query: Optional[str] = Field(None, description="Optional query to search within the website")

class ExaSearchTool(BaseTool):
    """
    A tool that uses Exa API for semantic search.
    Requires an Exa API key in the environment variables.
    """
    name: str = "Exa Search"
    description: str = "Search the web for current information using Exa's semantic search API"
    args_schema: Type[BaseModel] = SearchQuery
    
    def _run(self, query: str) -> str:
        """Execute the search using Exa API."""
        if not HAS_EXA:
            return "Error: Exa package is not installed. Please install it with 'pip install exa-py'."
        
        api_key = os.getenv("EXA_API_KEY")
        if not api_key:
            return "Error: EXA_API_KEY environment variable not set."
        
        try:
            exa = Exa(api_key=api_key)
            results = exa.search(query=query, num_results=5, use_autoprompt=True)
            
            formatted_results = []
            for i, result in enumerate(results):
                formatted_results.append(f"{i+1}. {result.title}\n   URL: {result.url}\n   Snippet: {result.text[:200]}...\n")
            
            return "\n".join(formatted_results) if formatted_results else "No results found."
        except Exception as e:
            return f"Error performing Exa search: {str(e)}"

class DuckDuckGoSearchTool(BaseTool):
    """
    A tool that uses DuckDuckGo for web search.
    Does not require an API key.
    """
    name: str = "DuckDuckGo Search"
    description: str = "Search the web for current information using DuckDuckGo"
    args_schema: Type[BaseModel] = SearchQuery
    
    def _run(self, query: str) -> str:
        """Execute the search using DuckDuckGo."""
        if not HAS_DDGS:
            return "Error: DuckDuckGo Search package is not installed. Please install it with 'pip install duckduckgo-search'."
        
        try:
            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=5))
            
            formatted_results = []
            for i, result in enumerate(results):
                formatted_results.append(f"{i+1}. {result.get('title', 'No title')}\n   URL: {result.get('href', 'No URL')}\n   Snippet: {result.get('body', 'No snippet')}...\n")
            
            return "\n".join(formatted_results) if formatted_results else "No results found."
        except Exception as e:
            return f"Error performing DuckDuckGo search: {str(e)}"

class WebsiteSearchTool(BaseTool):
    """
    A tool that searches and extracts information from a specific website.
    """
    name: str = "Website Search"
    description: str = "Search and extract information from a specific website URL"
    args_schema: Type[BaseModel] = WebsiteQuery
    
    def _run(self, url: str, query: Optional[str] = None) -> str:
        """Extract information from a website, optionally filtering by query."""
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.extract()
            
            # Get text
            text = soup.get_text(separator='\n')
            
            # Clean up text
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = '\n'.join(chunk for chunk in chunks if chunk)
            
            # If query is provided, try to find relevant sections
            if query:
                query_lower = query.lower()
                paragraphs = text.split('\n\n')
                relevant_paragraphs = [p for p in paragraphs if query_lower in p.lower()]
                
                if relevant_paragraphs:
                    result = f"Information from {url} related to '{query}':\n\n"
                    result += "\n\n".join(relevant_paragraphs[:5])  # Limit to first 5 relevant paragraphs
                    return result
            
            # If no query or no relevant paragraphs found, return beginning of the content
            content = f"Information from {url}:\n\n"
            content += text[:2000] + "..." if len(text) > 2000 else text
            return content
            
        except Exception as e:
            return f"Error extracting information from website: {str(e)}"

class WeatherInfoTool(BaseTool):
    """
    A tool that retrieves weather information for a location.
    Uses a free weather API.
    """
    name: str = "Weather Information"
    description: str = "Get weather information for a specific location and date range"
    
    class WeatherQuery(BaseModel):
        location: str = Field(description="City or location name")
        start_date: Optional[str] = Field(None, description="Start date in YYYY-MM-DD format (optional)")
        end_date: Optional[str] = Field(None, description="End date in YYYY-MM-DD format (optional)")
    
    args_schema: Type[BaseModel] = WeatherQuery
    
    def _run(self, location: str, start_date: Optional[str] = None, end_date: Optional[str] = None) -> str:
        """Get weather information for the specified location and date range."""
        try:
            # Using OpenMeteo free weather API
            base_url = "https://api.open-meteo.com/v1/forecast"
            
            params = {
                "latitude": 0,  # Will be updated after geocoding
                "longitude": 0,  # Will be updated after geocoding
                "current": "temperature_2m,weather_code,wind_speed_10m",
                "daily": "weather_code,temperature_2m_max,temperature_2m_min,precipitation_sum",
                "timezone": "auto",
                "forecast_days": 14  # Maximum forecast days available for free
            }
            
            # First, geocode the location
            geocode_url = f"https://geocoding-api.open-meteo.com/v1/search?name={location}&count=1"
            geocode_response = requests.get(geocode_url)
            geocode_data = geocode_response.json()
            
            if not geocode_data.get("results"):
                return f"Could not find location: {location}"
            
            # Extract coordinates
            lat = geocode_data["results"][0]["latitude"]
            lon = geocode_data["results"][0]["longitude"]
            location_name = geocode_data["results"][0]["name"]
            country = geocode_data["results"][0].get("country", "")
            
            # Update params with coordinates
            params["latitude"] = lat
            params["longitude"] = lon
            
            # Get weather data
            weather_response = requests.get(base_url, params=params)
            weather_data = weather_response.json()
            
            # Format the response
            result = f"Weather information for {location_name}, {country}:\n\n"
            
            # Current weather
            if "current" in weather_data:
                current = weather_data["current"]
                weather_code = current.get("weather_code", 0)
                weather_desc = self._get_weather_description(weather_code)
                
                result += f"Current conditions: {weather_desc}, {current.get('temperature_2m', 'N/A')}°C, "
                result += f"Wind: {current.get('wind_speed_10m', 'N/A')} km/h\n\n"
            
            # Daily forecast
            if "daily" in weather_data:
                daily = weather_data["daily"]
                dates = daily.get("time", [])
                max_temps = daily.get("temperature_2m_max", [])
                min_temps = daily.get("temperature_2m_min", [])
                precip = daily.get("precipitation_sum", [])
                weather_codes = daily.get("weather_code", [])
                
                result += "Daily forecast:\n"
                for i in range(min(7, len(dates))):  # Show up to 7 days
                    weather_desc = self._get_weather_description(weather_codes[i])
                    result += f"{dates[i]}: {weather_desc}, {min_temps[i]}°C to {max_temps[i]}°C, "
                    result += f"Precipitation: {precip[i]} mm\n"
            
            return result
            
        except Exception as e:
            return f"Error retrieving weather information: {str(e)}"
    
    def _get_weather_description(self, code: int) -> str:
        """Convert weather code to human-readable description."""
        weather_codes = {
            0: "Clear sky",
            1: "Mainly clear",
            2: "Partly cloudy",
            3: "Overcast",
            45: "Fog",
            48: "Depositing rime fog",
            51: "Light drizzle",
            53: "Moderate drizzle",
            55: "Dense drizzle",
            56: "Light freezing drizzle",
            57: "Dense freezing drizzle",
            61: "Slight rain",
            63: "Moderate rain",
            65: "Heavy rain",
            66: "Light freezing rain",
            67: "Heavy freezing rain",
            71: "Slight snow fall",
            73: "Moderate snow fall",
            75: "Heavy snow fall",
            77: "Snow grains",
            80: "Slight rain showers",
            81: "Moderate rain showers",
            82: "Violent rain showers",
            85: "Slight snow showers",
            86: "Heavy snow showers",
            95: "Thunderstorm",
            96: "Thunderstorm with slight hail",
            99: "Thunderstorm with heavy hail"
        }
        return weather_codes.get(code, "Unknown")
