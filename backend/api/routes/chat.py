"""
Chat API routes.
"""

from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Dict, Any, Generator
import json

from middleware.auth import get_current_user
from middleware.rate_limit import get_rate_limit
from agents.co_pilot_agent import CoPilotAgent
from agents.discovery_agent import DiscoveryAgent
from engines.context_engine import ContextEngine
from engines.forecast_baseline_engine import ForecastBaselineEngine
from tools.sales_data_tool import SalesDataTool
from tools.context_data_tool import ContextDataTool
from tools.targets_config_tool import TargetsConfigTool
from tools.weather_tool import WeatherTool
from agents.scenario_lab_agent import ScenarioLabAgent
from engines.scenario_evaluation_engine import ScenarioEvaluationEngine
from engines.validation_engine import ValidationEngine
from engines.uplift_elasticity_engine import UpliftElasticityEngine

router = APIRouter()

# Shared agents/tools for chat orchestration
_sales_tool = SalesDataTool()
_context_tool = ContextDataTool()
_targets_tool = TargetsConfigTool()
_baseline_engine = ForecastBaselineEngine(sales_data_tool=_sales_tool, targets_tool=_targets_tool)
_context_engine = ContextEngine(context_tool=_context_tool)
_uplift_engine = UpliftElasticityEngine(sales_data_tool=_sales_tool)
_evaluation_engine = ScenarioEvaluationEngine(uplift_engine=_uplift_engine)
_validation_engine = ValidationEngine(config_tool=_targets_tool)
_discovery_agent = DiscoveryAgent(
    context_engine=_context_engine,
    forecast_engine=_baseline_engine,
    context_tool=_context_tool,
    weather_tool=WeatherTool(),
    targets_tool=_targets_tool,
    sales_tool=_sales_tool,
)
_scenario_agent = ScenarioLabAgent(
    evaluation_engine=_evaluation_engine,
    validation_engine=_validation_engine,
    forecast_engine=_baseline_engine,
    uplift_engine=_uplift_engine,
    context_engine=_context_engine,
)
_copilot_agent = CoPilotAgent(discovery_agent=_discovery_agent, scenario_agent=_scenario_agent)


class ChatRequest(BaseModel):
    message: str
    context: Dict[str, Any] | None = None


@router.post("/message")
@get_rate_limit("chat")
async def chat_message(
    payload: ChatRequest,
    request: Request,
    current_user=Depends(get_current_user),
) -> Dict[str, Any]:
    """Return a single chat response."""
    return _copilot_agent.generate_response(payload.message, payload.context or {})


def _stream_response(chunks: Generator[str, None, None]) -> Generator[bytes, None, None]:
    for chunk in chunks:
        payload = json.dumps({"chunk": chunk, "done": False})
        yield f"data: {payload}\n\n".encode()
    yield f"data: {json.dumps({'chunk': '', 'done': True})}\n\n".encode()


@router.post("/stream")
@get_rate_limit("chat")
async def chat_stream(
    payload: ChatRequest,
    request: Request,
    current_user=Depends(get_current_user),
) -> StreamingResponse:
    """Stream chat response via SSE."""
    stream = _stream_response(_copilot_agent.stream_response(payload.message, payload.context or {}))
    return StreamingResponse(stream, media_type="text/event-stream")
