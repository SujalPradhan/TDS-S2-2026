# AI Weather Chatbot

A conversational AI chatbot that detects weather-related queries and fetches real-time weather data using Open-Meteo API, powered by GPT-5-nano via aipipe.

## Features

- 🤖 **Intelligent Intent Detection**: Uses LLM to determine if queries are weather-related
- 📍 **Location Extraction**: Automatically extracts location and converts to coordinates
- 🌦️ **Real-time Weather Data**: Fetches live weather from Open-Meteo (no API key required)
- 💬 **Natural Responses**: Formats weather data into conversational responses
- 🔄 **Fallback Handling**: Gracefully handles non-weather queries and API failures

## Workflow

```
User Input
    ↓
LLM (intent + entity extraction)
    ↓
Geocode city → latitude/longitude
    ↓
Call Open-Meteo API
    ↓
Send structured weather JSON to LLM
    ↓
Return conversational response
```

## Technical Stack

- **Language**: Python 3.10+
- **Framework**: FastAPI
- **Async HTTP**: httpx
- **LLM Provider**: aipipe (GPT-5-nano)
- **Weather API**: Open-Meteo

## Quick Start

### 1. Setup Environment

```bash
# Clone the repository
git clone <your-repo-url>
cd ai-weather-chatbot

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup environment variables
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

### 2. Run the Server

```bash
python main.py
```

The server will start on `http://localhost:8000`

### 3. Test the Chatbot

```bash
# In a new terminal, run the test script
python tmp_rovodev_test_chatbot.py
```

Or use curl:

```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "What is the temperature in Delhi?"}'
```

### 4. API Documentation

Visit `http://localhost:8000/docs` for interactive API documentation (Swagger UI)

## API Endpoints

### POST /chat

Main chatbot endpoint

**Request:**
```json
{
  "message": "What is the temperature and humidity in Delhi?"
}
```

**Response:**
```json
{
  "response": "In Delhi right now, the temperature is 28.4°C with a humidity of 54%."
}
```

### GET /

Health check endpoint

### GET /health

Service health status

## Supported Weather Parameters

- Temperature
- Humidity
- Precipitation
- Wind Speed
- Pressure
- Cloud Cover
- Weather Code

## Example Queries

✅ **Weather Queries:**
- "What is the temperature in Delhi?"
- "How's the weather in London?"
- "Tell me about the weather in Tokyo with humidity and wind speed"
- "What's the temperature and precipitation in New York?"

✅ **Non-Weather Queries:**
- "Hello, how are you?"
- "What is 2 + 2?"
- Any general conversation

## Docker Support

### Build and Run with Docker

```bash
# Build the image
docker build -t ai-weather-chatbot .

# Run the container
docker run -p 8000:8000 -e OPENAI_API_KEY=your_key_here ai-weather-chatbot
```

### Using Docker Compose

```bash
docker-compose up
```

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENAI_API_KEY` | Yes | API key for aipipe/OpenAI services |

## Error Handling

The chatbot handles various edge cases:

- **API Failures**: Returns friendly error messages
- **Invalid Locations**: Asks user to be more specific
- **Non-Weather Queries**: Routes to general conversation handler
- **Missing Data**: Acknowledges missing information politely

## Architecture

### Step 1: Intent Detection
- Calls aipipe GPT-5-nano to analyze user input
- Extracts: location, parameters, coordinates
- Returns structured JSON

### Step 2: Weather Fetch
- Queries Open-Meteo API with extracted coordinates
- Requests only user-specified parameters
- Returns structured weather data

### Step 3: Response Formatting
- Sends weather data to LLM
- Generates natural, conversational response
- Includes proper units and location context

## Development

### Project Structure

```
.
├── main.py                  # Main application
├── app.py                   # Legacy weather API example
├── requirements.txt         # Python dependencies
├── .env.example            # Environment template
├── .gitignore              # Git ignore rules
├── README.md               # This file
├── Dockerfile              # Docker configuration
└── docker-compose.yml      # Docker Compose config
```

### Running Tests

```bash
python tmp_rovodev_test_chatbot.py
```

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
