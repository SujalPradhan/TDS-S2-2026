# AI Weather Chatbot -- Coding Agent Instructions

## Goal

Build a basic AI chatbot that: 1. Detects weather-related queries 2.
Extracts location and requested parameters 3. Fetches live weather from
Open-Meteo (no API key) 4. Uses GPT-5-nano (via aipipe) to format a
conversational response

------------------------------------------------------------------------

## Workflow

User Input\
→ LLM (intent + entity extraction)\
→ Geocode city → latitude/longitude\
→ Call Open-Meteo API\
→ Send structured weather JSON to LLM\
→ Return conversational response

------------------------------------------------------------------------

## Step 1: Intent Detection (LLM)

Call: POST https://aipipe.org/openai/v1/chat/completions

Model: gpt-5-nano

Prompt must return ONLY JSON:

{ "is_weather_query": true, "location": "Delhi", "parameters":
\["temperature", "humidity"\], "timeframe": "current", "latitude": 18 , "longitude": 77} 

 <!-- the LLM should pass the latitude and longitude -->

If not weather-related: { "is_weather_query": false }

------------------------------------------------------------------------

## Step 2: Weather Fetch

Call Open-Meteo Forecast API:

https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m

Only request parameters the user asked for.

------------------------------------------------------------------------

## Step 3: Response Formatting (LLM)

Send structured JSON to GPT:

{ "location": "Delhi", "data": { "temperature_2m": 28.4,
"relative_humidity_2m": 54 } }

LLM must: - Use only provided data - Mention units properly - Keep
response concise - Avoid hallucination

Example output: "In Delhi right now, the temperature is 28.4°C with a
humidity of 54%."

------------------------------------------------------------------------

## Technical Requirements

-   Language: Python
-   Framework: FastAPI
-   Async HTTP requests (httpx)
-   Environment variable: OPENAI_API_KEY
-   Do it in a single script called main.py

------------------------------------------------------------------------

## Edge Cases

-   API failure → return safe fallback message
-   Non-weather query → normal LLM response

------------------------------------------------------------------------

## Final Behavior

Input: "What is the temperature and humidity in Delhi?"

Output: Live data fetched from Open-Meteo and formatted by GPT.
