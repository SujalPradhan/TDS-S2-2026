import os
import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import json
from dotenv import load_dotenv
import string
load_dotenv()

app = FastAPI(title="AI Weather Chatbot")

# Get API key from environment
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable is required")

AIPIPE_URL = "https://aipipe.org/openai/v1/chat/completions"
OPENMETEO_URL = "https://api.open-meteo.com/v1/forecast"

# Request/Response models
class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str


# Mapping of user-friendly parameter names to Open-Meteo API parameters
PARAM_MAPPING = {
    "temperature": "temperature_2m",
    "humidity": "relative_humidity_2m",
    "precipitation": "precipitation",
    "wind_speed": "wind_speed_10m",
    "wind": "wind_speed_10m",
    "weather": "weather_code",
    "pressure": "pressure_msl",
    "cloud_cover": "cloud_cover",
    "clouds": "cloud_cover"
}


async def call_llm(messages: list) -> dict:
    """Call the aipipe GPT-5-nano API"""
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "gpt-5-nano",
        "messages": messages,
    }
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(AIPIPE_URL, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()


async def detect_intent(user_input: str) -> dict:
    """Step 1: Use LLM to detect weather intent and extract entities"""
    
    system_prompt = """You are a weather query analyzer. Your task is to determine if the user's message is asking about weather and extract relevant information.

You must respond with ONLY valid JSON in this exact format:

For weather queries:
{
  "is_weather_query": true,
  "location": "City Name",
  "parameters": ["temperature", "humidity"],
  "timeframe": "current",
  "latitude": 28.6139,
  "longitude": 77.2090
}

For non-weather queries:
{
  "is_weather_query": false
}

Important rules:
1. Extract the city/location name from the query
2. Determine what weather parameters the user wants (temperature, humidity, precipitation, wind_speed, etc.)
3. Provide accurate latitude and longitude for the location
4. If no specific parameters are mentioned, default to ["temperature"]
5. Timeframe should always be "current" for now
6. Return ONLY the JSON, no other text or explanation"""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_input}
    ]
    
    try:
        llm_response = await call_llm(messages)
        content = llm_response["choices"][0]["message"]["content"].strip()
        
        # Try to extract JSON if there's extra text
        if "{" in content:
            start = content.index("{")
            end = content.rindex("}") + 1
            content = content[start:end]
        
        intent_data = json.loads(content)
        return intent_data
    except Exception as e:
        return {"is_weather_query": False}


async def fetch_weather(latitude: float, longitude: float, parameters: List[str]) -> dict:
    """Step 2: Fetch weather data from Open-Meteo API"""
    
    # Map user parameters to Open-Meteo parameters
    api_params = []
    for param in parameters:
        mapped = PARAM_MAPPING.get(param.lower(), param)
        api_params.append(mapped)
    
    # Build query parameters
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": ",".join(api_params)
    }
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(OPENMETEO_URL, params=params)
            response.raise_for_status()
            return response.json()
    except Exception as e:
        raise


async def format_response(location: str, weather_data: dict, parameters: List[str]) -> str:
    """Step 3: Use LLM to format weather data into conversational response"""
    
    # Extract current weather values
    current = weather_data.get("current", {})
    
    # Create a clean data dict for the LLM
    data_dict = {}
    for i, param in enumerate(parameters):
        mapped_param = PARAM_MAPPING.get(param.lower(), param)
        if mapped_param in current:
            data_dict[mapped_param] = current[mapped_param]
    
    # Get units from the response
    current_units = weather_data.get("current_units", {})
    
    system_prompt = """You are a friendly weather assistant. Format the provided weather data into a natural, conversational response.

Rules:
1. Use ONLY the data provided - do not make up or hallucinate information
2. Include units properly (°C, %, mm, etc.)
3. Keep the response concise and friendly
4. Mention the location clearly
5. If data is missing, acknowledge it politely"""

    user_prompt = f"""Location: {location}

Weather Data: {json.dumps(data_dict, indent=2)}

Units: {json.dumps(current_units, indent=2)}

Format this into a natural conversational response."""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]
    
    try:
        llm_response = await call_llm(messages)
        return llm_response["choices"][0]["message"]["content"].strip()
    except Exception as e:
        # Fallback to simple formatting
        return f"Weather data for {location}: {data_dict}"


async def handle_non_weather_query(user_input: str) -> str:
    """Handle non-weather queries with a normal LLM response"""
    
    messages = [
        {"role": "system", "content": "You are a helpful assistant. Answer the user's question naturally and concisely."},
        {"role": "user", "content": user_input}
    ]
    
    try:
        llm_response = await call_llm(messages, temperature=0.7)
        return llm_response["choices"][0]["message"]["content"].strip()
    except Exception as e:
        return "I'm sorry, I couldn't process your request at the moment. Please try again."


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Main chat endpoint"""
    
    try:
        # Step 1: Detect intent and extract entities
        intent = await detect_intent(request.message)
        # If not a weather query, handle as general conversation
        if not intent.get("is_weather_query", False):
            response_text = await handle_non_weather_query(request.message)
            return ChatResponse(response=response_text)
        
        # Extract location and parameters
        location = intent.get("location", "Unknown")
        latitude = intent.get("latitude")
        longitude = intent.get("longitude")
        parameters = intent.get("parameters", ["temperature"])
        
        if not latitude or not longitude:
            return ChatResponse(
                response="I couldn't determine the location coordinates. Could you please be more specific about the location?"
            )
        
        # Step 2: Fetch weather data
        try:
            weather_data = await fetch_weather(latitude, longitude, parameters)
        except Exception as e:
            return ChatResponse(
                response=f"I'm sorry, I couldn't fetch the weather data for {location} at the moment. Please try again later."
            )
        
        # Step 3: Format response using LLM
        response_text = await format_response(location, weather_data, parameters)
        
        return ChatResponse(response=response_text)
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="An error occurred while processing your request. Please try again."
        )


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "online",
        "service": "AI Weather Chatbot",
        "version": "1.0.0"
    }


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
