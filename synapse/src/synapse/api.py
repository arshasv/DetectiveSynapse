from fastapi import FastAPI, Request
import asyncio
from typing import AsyncGenerator, Any, Dict
import json
from .main import Settings, PlotFlow, BriefingFlow
from sse_starlette.sse import EventSourceResponse

class RunRequest(Settings):
    def to_settings(self) -> Settings:
        return Settings(**self.model_dump())

app = FastAPI(title="Detective Synapse API", version="0.1.0")

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
    result: str = await flow(settings)
    parsed = json.loads(result)
    json.dumps({"event": "completed", "data": parsed})

@app.post("/user_inputs", tags=["Briefing"])
async def run_endpoint(payload: RunRequest) -> Dict[str, Any]:
    settings = payload.to_settings()
    result = await flow(settings)
    parsed = json.loads(result)
    return {"result": parsed}

# /User_inputs_stream
@app.post("/user_inputs_stream", tags=["experimental"])
async def run_stream_endpoint(request: Request, payload: RunRequest):
    settings = payload.to_settings()

    async def event_generator(req: Request):
        async for chunk in run_plot_flow_stream(settings):
            if await req.is_disconnected():
                break
            yield {"data": chunk}

    return EventSourceResponse(event_generator(request))