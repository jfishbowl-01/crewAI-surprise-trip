# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a FastAPI-based travel planning service that provides OpenAI-compatible chat completions for IBM watsonx Orchestrate integration. The service simulates a multi-agent AI travel planning team that generates surprise trip itineraries based on user inputs.

## Development Commands

### Running the Application
```bash
# Standard version
uvicorn watson_x_api:app --host 0.0.0.0 --port 8000 --reload

# IBM-specific version
uvicorn watson_x_api_ibm:app --host 0.0.0.0 --port 8000 --reload
```

### Installing Dependencies
```bash
# Standard dependencies
pip install -r requirements.txt

# IBM-specific dependencies (includes watsonx integration)
pip install -r requirements_ibm.txt
```

### Environment Setup
- Copy `.env.example.ibm` to `.env` and configure IBM watsonx credentials
- Required environment variables:
  - `WATSONX_APIKEY`: IBM API key
  - `WATSONX_PROJECT_ID`: IBM project ID
  - `WATSONX_URL`: IBM watsonx URL (default: https://us-south.ml.cloud.ibm.com)
  - `SERPER_API_KEY`: Optional search API key

## Architecture

### Core Components

**API Layers:**
- `watson_x_api.py`: Standard version with mock travel agent responses
- `watson_x_api_ibm.py`: IBM watsonx-integrated version with real AI responses

**Key Endpoints:**
- `/chat/completions`: OpenAI-compatible chat completions (primary interface)
- `/plan-surprise-trip`: Legacy direct planning endpoint
- `/health`: Health check endpoint
- `/`: Service information endpoint

**Request Flow:**
1. Client sends OpenAI-format chat completion request
2. `extract_travel_details()` parses user messages for travel parameters
3. Service generates response (mock in standard, AI in IBM version)
4. Response returned in OpenAI-compatible format with streaming support

### Data Models
- `ChatMessage`: OpenAI-compatible message format
- `ChatCompletionRequest`: Request structure with streaming support
- `ChatCompletionResponse`: Response structure with choice arrays
- `StreamingChunk`: Server-sent events for streaming responses

### Deployment Configurations
- `Procfile`: Standard Heroku deployment
- `Procfile_ibm`: IBM-specific Heroku deployment
- Both configurations use uvicorn ASGI server on port `$PORT`

## Development Notes

### Two Versions Strategy
The repository maintains two parallel implementations:
- Standard version (`watson_x_api.py`): Mock responses for testing
- IBM version (`watson_x_api_ibm.py`): Real watsonx.ai integration

When modifying functionality, update both files to maintain consistency.

### Travel Parameter Extraction
The `extract_travel_details()` function uses regex patterns to extract:
- Destinations (Tokyo, Paris, London, New York)
- Origins (Boston, New York)
- Budget (dollar amounts)
- Duration (days/weeks patterns)

### Response Generation
- Standard version: Template-based mock responses
- IBM version: Integration with watsonx.ai models
- Both support streaming via Server-Sent Events

### Error Handling
All endpoints return OpenAI-compatible error responses to maintain API consistency with watsonx Orchestrate expectations.