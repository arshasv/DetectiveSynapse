from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
import asyncio
from typing import AsyncGenerator, Any, Dict, List
import json
import regex as re
import os
import random
from pathlib import Path
from .main import Settings, PlotFlow, BriefingFlow, NarrativeFlow, CrimeFlow, SolutionFlow
from sse_starlette.sse import EventSourceResponse
from pydantic import BaseModel

# --- Configuration for Image Logic ---
IMAGE_SEQUENCE = [
    "https://generativeaidatadocs.blob.core.windows.net/detectivesynapse/apartment.png",
    "https://generativeaidatadocs.blob.core.windows.net/detectivesynapse/before_theft.png",
    "https://generativeaidatadocs.blob.core.windows.net/detectivesynapse/after_theft.png",
]

# --- Pydantic Models for Request and Response ---
class RunRequest(Settings):
    def to_settings(self) -> Settings:
        return Settings(**self.model_dump())

class SuspectModel(BaseModel):
    id: str
    name: str
    gender:str
    role: str
    biography: str
    initialStatement: str
    image: str

class CrimeScenarioResponse(BaseModel):
    type: str
    Goal: str
    suspectlist: List[SuspectModel]

# --- In-memory store for the last user settings ---
# This dictionary will hold the crimeType from the most recent /user_inputs call.
latest_user_settings: Dict[str, Any] = {}

app = FastAPI(title="Detective Synapse API", version="0.1.0")

# --- Create a reliable, absolute path to the static images directory ---
BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "Images"

# --- Mount static directory using the absolute path ---
app.mount("/static/images", StaticFiles(directory=STATIC_DIR), name="images")


# --- Helper Function to Assign Images Sequentially ---
def process_and_segment_story(parsed_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Splits the story into sentences and assigns images sequentially.
    """
    if not parsed_data or not parsed_data.values():
        return []

    full_text = list(parsed_data.values())[0]
    sentences = re.split(r'(?<!\b(?:Dr|Mr|Mrs|Ms|St|Prof))\.\s+', full_text)
    sentences = [s.strip() for s in sentences if s.strip()]

    result_list = []
    for index, sentence in enumerate(sentences):
        if index < len(sentences) - 1:
            sentence += "."

        assigned_image = None
        if index == 0:
            assigned_image = IMAGE_SEQUENCE[0]
        elif index == 1:
            assigned_image = IMAGE_SEQUENCE[1]
        else:
            assigned_image = IMAGE_SEQUENCE[2]

        segment_object = {
            "text": sentence,
            "images": assigned_image
        }
        result_list.append(segment_object)

    return result_list


async def flow(settings: Settings) -> str:
    """Runs the core narrative generation flows."""
    plot_flow = PlotFlow()
    briefing_flow = BriefingFlow()
    crime_flow = CrimeFlow()
    solution_flow = SolutionFlow()
    narrative_flow = NarrativeFlow()
    plot_flow.state.settings = settings
    await plot_flow.kickoff_async()
    await briefing_flow.kickoff_async()
    await crime_flow.kickoff_async()
    await solution_flow.kickoff_async()
    await narrative_flow.kickoff_async()
    return briefing_flow.state.Briefing


async def run_plot_flow_stream(settings: Settings) -> AsyncGenerator[str, None]:
    """Generator function for streaming results."""
    yield json.dumps({"event": "settings", "data": settings.model_dump()})
    await asyncio.sleep(0)
    result_json_string = await flow(settings)
    parsed = json.loads(result_json_string)
    segmented_list = process_and_segment_story(parsed)
    yield json.dumps({"event": "completed", "data": segmented_list})


@app.post("/generate_story", tags=["Briefing"])
async def run_endpoint(payload: RunRequest) -> Dict[str, Any]:
    """
    Accepts user settings, generates the story, and stores the crime type.
    """
    settings = payload.to_settings()

    # MODIFICATION: Store the crimeType from the current request in our in-memory store.
    global latest_user_settings
    latest_user_settings['crimeType'] = settings.crimeType

    result_json_string = await flow(settings)
    parsed = json.loads(result_json_string)
    segmented_list = process_and_segment_story(parsed)
    return {"result": segmented_list}

@app.get("/suspects_list", response_model=CrimeScenarioResponse)
async def run_flow_and_get_dossiers(request: Request):
    """
    Generates the suspect list with a goal based on the previously submitted crime type.
    """
    MALE_IMAGE_DIR = STATIC_DIR / "Male"
    FEMALE_IMAGE_DIR = STATIC_DIR / "Female"

    try:
        if not MALE_IMAGE_DIR.is_dir() or not FEMALE_IMAGE_DIR.is_dir():
             raise HTTPException(status_code=500, detail="Image directories ('Male', 'Female') not found on the server.")

        male_images = [f for f in os.listdir(MALE_IMAGE_DIR) if os.path.isfile(os.path.join(MALE_IMAGE_DIR, f))]
        female_images = [f for f in os.listdir(FEMALE_IMAGE_DIR) if os.path.isfile(os.path.join(FEMALE_IMAGE_DIR, f))]

        random.shuffle(male_images)
        random.shuffle(female_images)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading image directories: {e}")

    try:
        # MODIFICATION: Get crimeType from the in-memory store, set by the /user_inputs endpoint.
        global latest_user_settings
        # Default to "Theft" if /user_inputs hasn't been called yet.
        crime_type = latest_user_settings.get("crimeType", "Theft")
        crime_type_lower = crime_type.lower()
        goal = "Solve the crime" # Default goal

        # Set the goal based on the crime type.
        if "murder" in crime_type_lower:
            goal = "Who is the killer"
        elif "theft" in crime_type_lower or "robbery" in crime_type_lower:
            goal = "Who is the thief"

        dossier_path = BASE_DIR.parent.parent / "Suspect_dossiers.json"

        with open(dossier_path, "r", encoding="utf-8") as f:
            raw_data = json.load(f)

        dossiers_data = raw_data.get("suspectDossiers", [])

        formatted_list = []
        for item in dossiers_data:
            gender = item.get("gender", "").lower()
            image_url = ""

            # Assign a random, unique image to each suspect based on gender.
            if gender == "male" and male_images:
                image_filename = male_images.pop()
                image_url = str(request.url_for('images', path=f"Male/{image_filename}"))
            elif gender == "female" and female_images:
                image_filename = female_images.pop()
                image_url = str(request.url_for('images', path=f"Female/{image_filename}"))

            formatted_item = {
                "id": item.get("characterID", ""),
                "name": item.get("name", ""),
                "gender": item.get("gender", ""),
                "role": item.get("roleInStory", ""),
                "biography": item.get("biography", ""),
                "initialStatement": item.get("initialStatementToPolice", ""),
                "image": image_url
            }
            formatted_list.append(formatted_item)

        # Return the response in the new, desired structure.
        return CrimeScenarioResponse(
            type=crime_type,
            Goal=goal,
            suspectlist=formatted_list
        )

    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"File not found: {dossier_path}. Check the location of Suspect_dossiers.json.")
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Failed to decode Suspect_dossiers.json.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        raise HTTPException(status_code=500, detail=f"An internal server error occurred: {str(e)}")


@app.post("/user_inputs_stream", tags=["experimental"])
async def run_stream_endpoint(request: Request, payload: RunRequest):
    """
    Experimental endpoint for streaming the story generation.
    """
    settings = payload.to_settings()
    async def event_generator(req: Request):
        async for chunk in run_plot_flow_stream(settings):
            if await req.is_disconnected():
                break
            yield {"data": chunk}
    return EventSourceResponse(event_generator(request))
