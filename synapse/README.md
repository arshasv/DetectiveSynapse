# Detective Synapse - API Documentation & Usage Guide

A multi-agent system built with crewAI that generates story plots and runs interactive interrogations. It includes FastAPI APIs with SSE streaming, persistent interrogation sessions, and YAML-configured agents/tasks.

## Features

- Plot generation via CrewAI agents configured in YAML
- Interrogation flow with persistent sessions (continue asking multiple questions)
- FastAPI endpoints with Server-Sent Events (SSE) streaming
- Pydantic-validated inputs for structured settings
- JSON output files (ignored by git by default)

## Requirements

- Python >= 3.10, < 3.13

## Installation

From the `synapse/` folder:
```bash
pip install -e .
```

This installs dependencies declared in `pyproject.toml`:
- crewai[tools]
- fastapi
- sse-starlette
- uvicorn[standard]
- python-dotenv

## Environment Variables

Place credentials in `.env` at `synapse/.env` (file is gitignored):

For Azure OpenAI:
```env
AZURE_OPENAI_API_KEY=your_azure_key
AZURE_OPENAI_ENDPOINT=https://your-endpoint.openai.azure.com
AZURE_OPENAI_API_VERSION=2024-06-01
```

The plot crew uses `langchain_litellm.ChatLiteLLM` with model `azure/gpt-5-mini`. Ensure your credentials match your provider.

## Project Layout (Key Files)

- `src/synapse/main.py`: Interrogation flow (state, flow logic, persistence)
- `src/synapse/api.py`: Plot flow FastAPI (SSE + JSON)
- `src/synapse/crews/plot_crew/plot_crew.py`: Plot crew (agents, tasks, LLM)
- `src/synapse/crews/plot_crew/config/agents.yaml`: Agent config
- `src/synapse/crews/plot_crew/config/tasks.yaml`: Task config and expected output schema

## Running the Server

### Plot API
```bash
uvicorn synapse.api:app --reload
```

## API Endpoints

### 1. POST `/run` - One-shot Plot Generation
Generates a plot and returns the result immediately.

**Request Body:**
```json
{
  "location": "Luxury Flat in Kochi",
  "crimeType": "Theft",
  "region": "Kerala, India"
}
```

**Response:**
```json
{
  "result": "Generated plot content..."
}
```

### 2. POST `/run_stream` - Streaming Plot Generation
Generates a plot with real-time progress updates using Server-Sent Events (SSE).

**Request Body:**
```json
{
  "location": "Los Angeles",
  "crimeType": "Murder",
  "region": "Hollywood"
}
```

**Response:** Server-Sent Events stream with progress updates.

## Input Schema

The API accepts these required fields:

- `location` (string): The location where the crime/story takes place
- `crimeType` (string): The type of crime or incident
- `region` (string): The broader region or area

## Outputs

- Plot flow saves to: `Plot.json`

## Expected Output Schema

The plot crew generates a concise JSON with this shape:
```json
{
  "bullseyeConcept": {
    "culprit": { "name": "", "profile": "" },
    "victim": { "name": "", "profile": "" },
    "crime": { "object": "", "description": "" },
    "motive": { "primary": "", "description": "" }
  }
}
```
