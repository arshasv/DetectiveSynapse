from fastapi import FastAPI, Request
import asyncio
from typing import AsyncGenerator, Any, Dict, List
import json
import regex as re
from .main import Settings, PlotFlow, BriefingFlow
from sse_starlette.sse import EventSourceResponse

# --- Configuration for Image Logic ---
# Define the images to be assigned sequentially.
IMAGE_SEQUENCE = [
    "https://generativeaidatadocs.blob.core.windows.net/detectivesynapse/apartment.png",   
    "https://generativeaidatadocs.blob.core.windows.net/detectivesynapse/before_theft.png",  
    "https://generativeaidatadocs.blob.core.windows.net/detectivesynapse/after_theft.png",  
]

class RunRequest(Settings):
    def to_settings(self) -> Settings:
        return Settings(**self.model_dump())

app = FastAPI(title="Detective Synapse API", version="0.1.0")


# --- MODIFIED Helper Function to Assign Images Sequentially ---
def process_and_segment_story(parsed_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Splits the story into sentences using an improved regex to handle abbreviations,
    and assigns images sequentially as a string.
    """
    if not parsed_data or not parsed_data.values():
        return []
    
    full_text = list(parsed_data.values())[0]

    # Use improved regex that avoids splitting on common abbreviations.
    sentences = re.split(r'(?<!\b(?:Dr|Mr|Mrs|Ms|St|Prof))\.\s+', full_text)
    sentences = [s.strip() for s in sentences if s.strip()]

    result_list = []
    for index, sentence in enumerate(sentences):
        # Add the period back to all but the last sentence for cleaner text
        if index < len(sentences) - 1:
            sentence += "."

        assigned_image = None
        
        if index == 0:
            assigned_image = IMAGE_SEQUENCE[0]
        elif index == 1:
            assigned_image = IMAGE_SEQUENCE[1]
        else:
            assigned_image = IMAGE_SEQUENCE[2]

        # **MODIFIED**: Assign the URL directly as a string, not inside an array
        segment_object = {
            "text": sentence,
            "images": assigned_image 
        }
        result_list.append(segment_object)

    return result_list


async def flow(settings: Settings) -> str:
    plot_flow = PlotFlow()
    briefing_flow = BriefingFlow()
    plot_flow.state.settings = settings
    await plot_flow.kickoff_async()
    await briefing_flow.kickoff_async()
    return briefing_flow.state.Briefing


async def run_plot_flow_stream(settings: Settings) -> AsyncGenerator[str, None]:
    yield json.dumps({"event": "settings", "data": settings.model_dump()})
    await asyncio.sleep(0)

    result_json_string = await flow(settings)
    parsed = json.loads(result_json_string)

    segmented_list = process_and_segment_story(parsed)

    yield json.dumps({"event": "completed", "data": segmented_list})


@app.post("/user_inputs", tags=["Briefing"])
async def run_endpoint(payload: RunRequest) -> Dict[str, Any]:
    settings = payload.to_settings()
    result_json_string = await flow(settings)
    parsed = json.loads(result_json_string)

    segmented_list = process_and_segment_story(parsed)

    return {"result": segmented_list}


@app.post("/user_inputs_stream", tags=["experimental"])
async def run_stream_endpoint(request: Request, payload: RunRequest):
    settings = payload.to_settings()

    async def event_generator(req: Request):
        async for chunk in run_plot_flow_stream(settings):
            if await req.is_disconnected():
                break
            yield {"data": chunk}

    return EventSourceResponse(event_generator(request))