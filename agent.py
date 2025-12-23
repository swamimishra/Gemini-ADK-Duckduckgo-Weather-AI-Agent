import os
import sys

sys.modules["google._upb._message"] = None
sys.modules["google.protobuf.pyext._message"] = None

# Force pure python just in case
os.environ["PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION"] = "python"

import requests
import datetime
from zoneinfo import ZoneInfo
from ddgs import DDGS
import google.generativeai as genai
from google.adk.agents import Agent
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Ensure API key is set
if "GOOGLE_API_KEY" not in os.environ:

    print("WARNING: GOOGLE_API_KEY environment variable not set.")
    # You might want to set it here purely for testing if the user allows, 
    # or rely on the environment being set safely.

def get_weather(city: str) -> str:
    """Gets the current weather for a given city."""
    print(f"[Tool] Getting weather for: {city}")
    try:
        # 1. Geocoding
        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1&language=en&format=json"
        geo_res = requests.get(geo_url).json()
        
        if "results" not in geo_res:
            return f"Could not find coordinates for city: {city}"
        
        lat = geo_res["results"][0]["latitude"]
        lon = geo_res["results"][0]["longitude"]
        place_name = geo_res["results"][0]["name"]
        
        # 2. Weather
        weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,weather_code"
        weather_res = requests.get(weather_url).json()
        
        if "current" not in weather_res:
            return f"Could not get weather data for {place_name}."
            
        temp = weather_res["current"]["temperature_2m"]
        unit = weather_res["current_units"]["temperature_2m"]
        code = weather_res["current"]["weather_code"]
        
        # Simple WMO code interpretation
        desc = "Unknown"
        if code == 0: desc = "Clear sky"
        elif code in [1, 2, 3]: desc = "Partly cloudy"
        elif code in [45, 48]: desc = "Fog"
        elif code in [51, 53, 55]: desc = "Drizzle"
        elif code in [61, 63, 65]: desc = "Rain"
        elif code in [71, 73, 75]: desc = "Snow"
        elif code in [95, 96, 99]: desc = "Thunderstorm"
        
        return f"Weather in {place_name}: {desc}, {temp} {unit}"
        
    except Exception as e:
        return f"Error getting weather: {str(e)}"

def get_current_time(city: str) -> str:
    """Gets the current local time for a given city."""
    print(f"[Tool] Getting time for: {city}")
    try:
        # 1. Geocoding
        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1&language=en&format=json"
        geo_res = requests.get(geo_url).json()
        
        if "results" not in geo_res:
            return f"Could not find coordinates for city: {city}"
            
        result = geo_res["results"][0]
        lat = result["latitude"]
        lon = result["longitude"]
        timezone_str = result.get("timezone", "UTC")
        place_name = result["name"]
        
        # 2. Local Time Calculation (Precision: Real-time)
        # Open-Meteo Geocoding gave us the IANA timezone (e.g., "Europe/London")
        # We use Python's zoneinfo to get the exact current time in that zone.
        
        current_time = datetime.datetime.now(ZoneInfo(timezone_str))
        return f"Current time in {place_name} ({timezone_str}): {current_time.strftime('%Y-%m-%d %H:%M:%S')}"

    except Exception as e:
        return f"Error getting time: {str(e)}"

def search_web(query: str) -> str:
    """Searches the web for the given query to find real-time information."""
    print(f"[Tool] Searching web for: {query}")
    try:
        results = DDGS().text(query, max_results=3)
        if not results:
            return "No search results found."
        
        # Format results
        output = "Search Results:\n"
        for i, res in enumerate(results, 1):
            output += f"{i}. {res['title']}: {res['body']}\n"
        return output
    except Exception as e:
        return f"Error searching web: {str(e)}"

# Define the agent
# Define the agent
class WeatherAgent(Agent):
    def __init__(self, model_name="gemini-2.5-flash-lite"):
        # Explicitly configure using the loaded env var
        if "GOOGLE_API_KEY" in os.environ:
            genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
            
        # Initialize the base Agent
        # Note: Implementation details of ADK might vary slightly, 
        # assuming standard tool registration pattern
        self.model = genai.GenerativeModel(model_name=model_name, 
                                           tools=[get_weather, get_current_time, search_web])
        self.chat = self.model.start_chat()

    def query(self, user_input):
        print(f"\nUser: {user_input}")
        response = self.chat.send_message(user_input)
        
        try:
             # Just return the text. 'response.text' acts as the final answer if logic is handled.
             # If tool calls happen, we need to handle them.
             # Automatic function calling:
             response = self.chat.send_message(user_input)
             
             # Loop for tool calls
             while response.parts and response.parts[0].function_call:
                 # Execute tool
                 fc = response.parts[0].function_call
                 fn_name = fc.name
                 args = fc.args
                 
                 result = "Unknown tool"
                 if fn_name == "get_weather":
                     result = get_weather(args["city"])
                 elif fn_name == "get_current_time":
                     result = get_current_time(args["city"])
                 elif fn_name == "search_web":
                     result = search_web(args["query"])
                     
                 # Send result back
                 response = self.chat.send_message(
                     genai.prototypes.Part(function_response=
                         genai.prototypes.FunctionResponse(name=fn_name, response={"result": result})
                     )
                 )
                 
             return response.text
             
        except Exception as e:
            return f"Error encountered: {e}"

# Simple interactions if run directly
if __name__ == "__main__":
    if "GOOGLE_API_KEY" not in os.environ:
        print("Please set GOOGLE_API_KEY environment variable.")
        exit(1)
        
    print("Initializing Weather & Time Agent...")
    
    # Configure explicitly
    genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
    
    model = genai.GenerativeModel("gemini-2.5-flash-lite", tools=[get_weather, get_current_time, search_web])
    chat = model.start_chat(enable_automatic_function_calling=True)
    
    print("Agent ready! (Type 'quit' to exit)")
    
    while True:
        try:
            user_in = input("You: ")
            if user_in.lower() in ['quit', 'exit']:
                break
                
            response = chat.send_message(user_in)
            print(f"Agent: {response.text}")
            
        except Exception as e:
            print(f"Error: {e}")
