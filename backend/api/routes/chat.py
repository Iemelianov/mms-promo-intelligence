"""
Chat API routes.
"""

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Dict, Any, Generator

from middleware.auth import get_current_user
from middleware.rate_limit import get_rate_limit

router = APIRouter()


class ChatRequest(BaseModel):
    message: str
    context: Dict[str, Any] | None = None


@router.post("/message")
@get_rate_limit("chat")
async def chat_message(
    payload: ChatRequest,
    current_user=Depends(get_current_user),
) -> Dict[str, Any]:
    """Return a single chat response."""
    return {
        "response": f"Scenario insight for '{payload.message}'",
        "suggestions": [
            "Try adjusting the discount on TVs",
            "Consider focusing on loyal customers",
        ],
        "related_data": {"scenario_ids": payload.context.get("active_scenarios", []) if payload.context else []},
    }


def _stream_response(text: str) -> Generator[bytes, None, None]:
    chunks = text.split(" ")
    for chunk in chunks:
        yield f"data: {{\"chunk\": \"{chunk}\", \"done\": false}}\n\n".encode()
    yield b'data: {"chunk": "", "done": true}\n\n'


@router.post("/stream")
@get_rate_limit("chat")
async def chat_stream(
    payload: ChatRequest,
    current_user=Depends(get_current_user),
) -> StreamingResponse:
    """Stream chat response via SSE."""
    stream = _stream_response(f"Scenario response: {payload.message}")
    return StreamingResponse(stream, media_type="text/event-stream")
