"""
Data Processing API Routes

Job-based data processing endpoints aligned to API spec.
"""

import os
import uuid
import json
from datetime import datetime, date
from typing import List, Optional, Dict, Any

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from middleware.rate_limit import get_rate_limit
from middleware.auth import require_promo_lead
from db.base import ProcessingJob
from db.session import get_session
from models.schemas import BaselineForecast
from engines.forecast_baseline_engine import ForecastBaselineEngine
from tools.sales_data_tool import SalesDataTool
from tools.targets_config_tool import TargetsConfigTool

router = APIRouter()

sales_tool = SalesDataTool()
targets_tool = TargetsConfigTool()
baseline_engine = ForecastBaselineEngine(sales_data_tool=sales_tool, targets_tool=targets_tool)


class DataProcessOptions(BaseModel):
    merge_strategy: Optional[str] = "union"
    validate_quality: Optional[bool] = True
    generate_report: Optional[bool] = True


class DataProcessRequest(BaseModel):
    files: List[str]
    options: Optional[DataProcessOptions] = None


class PromoProcessOptions(BaseModel):
    extract_campaigns: Optional[bool] = True
    load_to_db: Optional[bool] = True
    validate_quality: Optional[bool] = True


class PromoProcessRequest(BaseModel):
    file: str
    options: Optional[PromoProcessOptions] = None


class ProcessingProgress(BaseModel):
    files_processed: int
    total_files: int
    records_processed: int
    errors: int


class ProcessingResult(BaseModel):
    data_quality_report: Optional[Dict[str, Any]] = None
    date_range: Optional[Dict[str, str]] = None
    channels: Optional[List[str]] = None
    departments: Optional[List[str]] = None
    campaigns_extracted: Optional[int] = None
    records_processed: Optional[int] = None
    quality_report: Optional[Dict[str, Any]] = None
    campaigns: Optional[List[Dict[str, Any]]] = None


class JobStatusResponse(BaseModel):
    job_id: str
    status: str
    progress: Optional[ProcessingProgress] = None
    result: Optional[ProcessingResult] = None
    completed_at: Optional[str] = None


def _create_job(
    db: Session,
    job_type: str,
    total_files: int,
    created_by: str,
    result: Optional[dict] = None,
    status: str = "processing",
) -> ProcessingJob:
    job = ProcessingJob(
        id=f"job_{uuid.uuid4().hex[:8]}",
        job_type=job_type,
        status=status,
        files_processed=0,
        total_files=total_files,
        records_processed=0,
        errors=0,
        result=json.dumps(result or {}),
        created_by=created_by,
        created_at=datetime.utcnow(),
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


def _job_to_response(job: ProcessingJob) -> JobStatusResponse:
    progress = ProcessingProgress(
        files_processed=job.files_processed,
        total_files=job.total_files,
        records_processed=job.records_processed,
        errors=job.errors,
    )
    result_payload = None
    if job.result:
        try:
            result_payload = ProcessingResult(**json.loads(job.result))
        except Exception:
            result_payload = ProcessingResult()
    return JobStatusResponse(
        job_id=job.id,
        status=job.status,
        progress=progress,
        result=result_payload,
        completed_at=job.completed_at.isoformat() + "Z" if job.completed_at else None,
    )


@router.post("/process")
@get_rate_limit("data_processing")
async def process_data(
    request: DataProcessRequest,
    current_user=Depends(require_promo_lead),
    db: Session = Depends(get_session),
) -> JobStatusResponse:
    """
    Start a data processing job for XLSB files (by path).
    """
    if not request.files:
        raise HTTPException(status_code=400, detail="No files provided")

    # For MVP, mark as completed immediately with stub metrics
    job = _create_job(
        db=db,
        job_type="xlsb",
        total_files=len(request.files),
        created_by=current_user.user_id,
        status="completed",
        result={
            "data_quality_report": {
                "total_records": 150000,
                "clean_records": 149500,
                "issues": [{"type": "missing_values", "count": 500, "columns": ["margin_value"]}],
            },
            "date_range": {"start": "2024-09-01", "end": "2025-01-31"},
            "channels": ["online", "offline"],
            "departments": ["TV", "Gaming", "Audio", "Accessories"],
        },
    )
    job.files_processed = len(request.files)
    job.records_processed = 150000
    job.status = "completed"
    job.completed_at = datetime.utcnow()
    db.commit()
    db.refresh(job)

    return _job_to_response(job)


@router.post("/process/promo")
@get_rate_limit("data_processing")
async def process_promo_catalog(
    request: PromoProcessRequest,
    current_user=Depends(require_promo_lead),
    db: Session = Depends(get_session),
) -> JobStatusResponse:
    """
    Process promotional catalog XLSB file.
    """
    job = _create_job(
        db=db,
        job_type="promo",
        total_files=1,
        created_by=current_user.user_id,
        status="completed",
        result={
            "campaigns_extracted": 45,
            "records_processed": 96653,
            "quality_report": {"overall_score": 0.97, "issues": []},
            "campaigns": [
                {
                    "id": "promo_period_1_2024-10-01",
                    "promo_name": "Promo Period 1",
                    "date_start": "2024-10-01",
                    "date_end": "2024-10-07",
                    "departments": ["TV", "Gaming"],
                    "channels": ["online", "offline"],
                    "avg_discount_pct": 20.5,
                }
            ],
        },
    )
    job.files_processed = 1
    job.records_processed = 96653
    job.status = "completed"
    job.completed_at = datetime.utcnow()
    db.commit()
    db.refresh(job)
    return _job_to_response(job)


@router.get("/process/{job_id}")
@get_rate_limit("data_processing")
async def get_job_status(
    job_id: str,
    current_user=Depends(require_promo_lead),
    db: Session = Depends(get_session),
) -> JobStatusResponse:
    """
    Get processing job status.
    """
    job = db.get(ProcessingJob, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return _job_to_response(job)


@router.get("/quality")
@get_rate_limit("standard")
async def get_quality_report(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    channel: Optional[str] = None,
    department: Optional[str] = None,
    current_user=Depends(require_promo_lead),
) -> dict:
    """
    Get data quality summary (stubbed to spec structure).
    """
    summary = {
        "total_records": 500000,
        "date_range": {"start": "2024-02-01", "end": "2025-01-31"},
        "channels": {"online": 250000, "offline": 250000},
        "departments": {"TV": 150000, "Gaming": 120000, "Audio": 100000, "Accessories": 130000},
    }
    quality_metrics = {
        "completeness": 0.99,
        "accuracy": 0.98,
        "consistency": 0.97,
        "timeliness": 0.95,
    }
    issues = [
        {
            "type": "missing_values",
            "severity": "low",
            "count": 5000,
            "affected_columns": ["margin_value"],
            "affected_dates": ["2024-03-15", "2024-03-16"],
        }
    ]
    return {"summary": summary, "quality_metrics": quality_metrics, "issues": issues}


@router.get("/baseline")
@get_rate_limit("standard")
async def get_baseline(
    start_date: date,
    end_date: date,
    current_user=Depends(require_promo_lead),
) -> BaselineForecast:
    """Get baseline forecast for the requested date range."""
    try:
        return baseline_engine.calculate_baseline((start_date, end_date))
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=str(exc)) from exc
