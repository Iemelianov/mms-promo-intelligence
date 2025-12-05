# API Specification

## Base Information

- **Base URL**: `https://api.promo-co-pilot.com/api/v1` (dev: `http://localhost:8000/api/v1`)
- **Protocol**: HTTPS
- **Content-Type**: `application/json`
- **Authentication**: Bearer token in `Authorization` header

## Authentication

All endpoints require authentication:

```
Authorization: Bearer <api_key>
```

**Development mode:** if `ENVIRONMENT=development` and no token is provided, the backend returns a mock admin user (Bearer is still required in production).

### Get API Key

```http
POST /api/v1/auth/api-keys
Content-Type: application/json

{
  "name": "My API Key",
  "expires_in_days": 90
}
```

**Response**:
```json
{
  "api_key": "pk_live_...",
  "expires_at": "2024-12-31T23:59:59Z"
}
```

## Data Processing Endpoints

### POST /api/v1/data/process-xlsb
Upload XLSB files (multipart). Cleans, validates, and loads to DuckDB (demo).

**Request**: form-data `files` (one or more `.xlsb` files)

**Response (example)**:
```json
{
  "processed_files": [
    {"filename": "Web_September_FY25.xlsb", "rows": 12000, "quality_score": 0.92, "issues_count": 1}
  ],
  "total_rows": 12000,
  "storage_result": {
    "success": true,
    "rows_inserted": 12000,
    "table_name": "sales_aggregated"
  }
}
```

### GET /api/v1/data/quality
Returns sampled data quality for recent sales data (demo).

### GET /api/v1/data/baseline
Baseline forecast for a date range (optional filters: `department`, `channel`).

### GET /api/v1/data/segments
Demo CDP segments.

### GET /api/v1/data/uplift-model
Demo uplift coefficients; optional `department`, `channel` filters.

## Discovery Endpoints

### GET /api/v1/discovery/context

Get contextual information for a date range.

**Query Parameters**:
- `geo` (required): Geographic region (e.g., "DE", "UA")
- `start_date` (required): ISO date string
- `end_date` (required): ISO date string

**Response**:
```json
{
  "context": {
    "geo": "DE",
    "date_range": {
      "start": "2024-10-20",
      "end": "2024-10-31"
    },
    "events": [
      {
        "name": "Black Friday",
        "date": "2024-11-29",
        "type": "global_sale",
        "impact": "high"
      }
    ],
    "weather_profile": {
      "location": "DE",
      "summary": "rainy_weekend, with 2 rainy day(s), avg 12.5°C",
      "daily": [
        {
          "date": "2024-10-22",
          "condition": "rain",
          "temp_max": 15.0,
          "temp_min": 10.0,
          "temp_avg": 12.5,
          "rain_prob": 75,
          "rain_sum": 5.2,
          "cloud_cover": 85
        }
      ]
    },
    "seasonality_factors": [
      {
        "department": "TV",
        "month": 10,
        "factor": 1.1
      }
    ]
  }
}
```

### POST /api/v1/discovery/analyze

Analyze situation and identify opportunities.

**Request**:
```json
{
  "month": "2024-10",
  "geo": "DE",
  "targets": {
    "sales_value": 10000000,
    "margin_pct": 25.0
  }
}
```

**Response**:
```json
{
  "baseline_forecast": {
    "period": {
      "start": "2024-10-01",
      "end": "2024-10-31"
    },
    "totals": {
      "sales_value": 7000000,
      "margin_value": 1750000,
      "margin_pct": 25.0,
      "units": 35000
    }
  },
  "gap_analysis": {
    "sales_gap": -3000000,
    "margin_gap": 0.0,
    "units_gap": -15000
  },
  "opportunities": [
    {
      "id": "opp_01",
      "title": "Close October gap with TVs+Gaming",
      "promo_date_range": {
        "start": "2024-10-22",
        "end": "2024-10-27"
      },
      "focus_departments": ["TV", "Gaming"],
      "estimated_potential": {
        "sales_value": 2500000,
        "margin_impact": -0.3
      },
      "priority": "high"
    }
  ]
}
```

## Scenario Endpoints

### POST /api/v1/scenarios/create

Create a new promotional scenario.

**Request**:
```json
{
  "brief": {
    "month": "2024-10",
    "promo_date_range": {
      "start": "2024-10-22",
      "end": "2024-10-27"
    },
    "focus_departments": ["TV", "Gaming"],
    "objectives": {
      "sales_value_target": 3000000,
      "margin_floor_pct": 20.0
    },
    "constraints": {
      "max_discount_pct": {
        "TV": 25,
        "Gaming": 30
      }
    }
  },
  "scenario_type": "balanced"
}
```

**Response**:
```json
{
  "scenario": {
    "id": "scenario_123",
    "label": "Balanced",
    "date_range": {
      "start": "2024-10-22",
      "end": "2024-10-27"
    },
    "mechanics": [
      {
        "department": "TV",
        "channel": "online",
        "discount_pct": 20,
        "segments": ["ALL"]
      }
    ]
  },
  "kpi": {
    "total": {
      "sales_value": 3200000,
      "margin_value": 720000,
      "margin_pct": 22.5,
      "ebit": 450000,
      "units": 18000
    },
    "vs_baseline": {
      "sales_value_delta": 1500000,
      "margin_value_delta": -80000,
      "ebit_delta": 90000
    }
  },
  "validation": {
    "status": "PASS",
    "issues": []
  }
}
```

### GET /api/v1/scenarios/{scenario_id}

Get scenario details.

**Response**: Same as POST /scenarios response

### PUT /api/v1/scenarios/{scenario_id}

Update scenario.

**Request**:
```json
{
  "mechanics": [
    {
      "department": "TV",
      "channel": "online",
      "discount_pct": 18,
      "segments": ["ALL"]
    }
  ]
}
```

**Response**: Updated scenario with recalculated KPIs

### DELETE /api/v1/scenarios/{scenario_id}

Delete a scenario.

**Response**:
```json
{
  "deleted": true,
  "scenario_id": "scenario_123"
}
```

### POST /api/v1/scenarios/compare

Compare multiple scenarios.

**Request**:
```json
{
  "scenario_ids": ["scenario_1", "scenario_2", "scenario_3"]
}
```

**Response**:
```json
{
  "comparison": {
    "scenarios": [
      {
        "id": "scenario_1",
        "label": "Conservative",
        "kpi": {...},
        "validation": {...}
      }
    ],
    "summary": {
      "best_sales": "scenario_3",
      "best_margin": "scenario_1",
      "best_ebit": "scenario_2"
    }
  }
}
```

## Optimization Endpoints

### POST /api/v1/optimization/generate

Generate optimized scenarios.

**Request**:
```json
{
  "brief": {...},
  "objectives": {
    "maximize": "ebit",
    "constraints": {
      "min_margin_pct": 20.0,
      "max_discount_pct": 25.0
    }
  },
  "num_scenarios": 3
}
```

**Response**:
```json
{
  "scenarios": [
    {
      "scenario": {...},
      "kpi": {...},
      "rank": 1,
      "score": 0.85,
      "recommendation": "Best balance of sales and margin"
    }
  ],
  "efficient_frontier": {
    "points": [
      {
        "sales": 3000000,
        "margin": 22.5,
        "ebit": 450000,
        "scenario_id": "scenario_123"
      }
    ]
  }
}
```

## Creative Endpoints

### POST /api/v1/creative/generate

Generate creative brief and assets.

**Request**:
```json
{
  "scenario_ids": ["scenario_123"],
  "asset_types": ["homepage_hero", "category_banner", "in_store_sheet"],
  "target_segments": ["LOYAL_HIGH_VALUE"]
}
```

**Response**:
```json
{
  "briefs": [
    {
      "brief_id": "brief_456",
      "scenario_id": "scenario_123",
      "creative_brief": {...},
      "assets": [...]
    }
  ]
}
```

### GET /api/v1/creative/{brief_id}
Fetch creative brief and assets by `brief_id` (stored when generated; demo fallback if missing).

### POST /api/v1/creative/brief
Generate a creative brief from a scenario.

### POST /api/v1/creative/assets
Generate asset specs from a brief.

### POST /api/v1/creative/finalize
Finalize selected scenarios into a campaign plan.

## Post-Mortem Endpoints

### POST /api/v1/postmortem/analyze

Analyze completed campaign.

**Request**:
```json
{
  "scenario_id": "scenario_123",
  "actual_data": {
    "sales_value": 3100000,
    "margin_value": 700000,
    "units": 17500
  },
  "period": {
    "start": "2024-10-22",
    "end": "2024-10-27"
  }
}
```

**Response**:
```json
{
  "report": {
    "scenario_id": "scenario_123",
    "forecast_kpi": {...},
    "actual_kpi": {...},
    "vs_forecast": {
      "sales_value_error_pct": -3.1,
      "margin_value_error_pct": -2.8
    },
    "insights": [
      "Uplift in Gaming was over-estimated",
      "TV sales exceeded forecast"
    ],
    "learning_points": [
      "Adjust Gaming uplift coefficient by -5%"
    ]
  }
}
```

## Chat Endpoints

### POST /api/v1/chat/message

Send message to co-pilot.

**Request**:
```json
{
  "message": "Why is scenario B better than scenario A?",
  "context": {
    "screen": "scenario_lab",
    "active_scenarios": ["scenario_A", "scenario_B"],
    "user_task": "comparing_scenarios"
  }
}
```

**Response**:
```json
{
  "response": "Scenario B offers a better balance of sales and margin...",
  "suggestions": [
    "Try adjusting the discount on TVs",
    "Consider focusing on loyal customers"
  ],
  "related_data": {
    "scenario_ids": ["scenario_B"]
  }
}
```

### POST /api/v1/chat/stream

Stream chat response (Server-Sent Events).

**Request**: Same as /chat/message

**Response**: SSE stream with chunks:
```
data: {"chunk": "Scenario", "done": false}
data: {"chunk": " B", "done": false}
data: {"chunk": " offers", "done": false}
data: {"chunk": "", "done": true}
```

## Error Responses

All errors follow this format:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid discount percentage",
    "details": {
      "field": "mechanics[0].discount_pct",
      "constraint": "Must be between 0 and 50"
    },
    "request_id": "req_123456"
  }
}
```

### Error Codes

- `VALIDATION_ERROR` (400): Request validation failed
- `NOT_FOUND` (404): Resource not found
- `UNAUTHORIZED` (401): Authentication required
- `FORBIDDEN` (403): Insufficient permissions
- `RATE_LIMIT_EXCEEDED` (429): Too many requests
- `INTERNAL_ERROR` (500): Server error
- `PROCESSING_ERROR` (500): Data processing failed

## Rate Limiting

- **Standard endpoints**: 100 requests/minute
- **Optimization endpoints**: 10 requests/minute
- **Data processing**: 5 jobs/hour
- **Chat endpoints**: 30 requests/minute

Headers:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1634567890
```

## Pagination

List endpoints support pagination:

**Query Parameters**:
- `page`: Page number (default: 1)
- `page_size`: Items per page (default: 20, max: 100)

**Response**:
```json
{
  "items": [...],
  "pagination": {
    "page": 1,
    "page_size": 20,
    "total": 150,
    "total_pages": 8
  }
}
```

## Webhooks

### Scenario Validated

```json
{
  "event": "scenario.validated",
  "scenario_id": "scenario_123",
  "status": "PASS",
  "timestamp": "2024-10-20T10:00:00Z"
}
```

### Data Processing Completed

```json
{
  "event": "data.processing.completed",
  "job_id": "job_123456",
  "records_processed": 150000,
  "timestamp": "2024-10-20T10:30:00Z"
}
```

### Creative Generated

```json
{
  "event": "creative.generated",
  "brief_id": "brief_456",
  "scenario_id": "scenario_123",
  "timestamp": "2024-10-20T10:00:00Z"
}
```

## SDK Examples

### Python

```python
from promo_co_pilot import Client

client = Client(api_key="your_api_key")

# Process data
job = client.data.process_files([
    "/path/to/Web_September_FY25.xlsb"
])
result = client.data.get_job_status(job.job_id)

# Create scenario
scenario = client.scenarios.create(
    brief={...},
    scenario_type="balanced"
)

# Generate creative
creative = client.creative.generate(
    scenario_ids=[scenario.id],
    asset_types=["homepage_hero"]
)
```

### JavaScript/TypeScript

```typescript
import { PromoCoPilotClient } from '@promo-co-pilot/sdk';

const client = new PromoCoPilotClient({
  apiKey: 'your_api_key'
});

// Process data
const job = await client.data.processFiles([
  '/path/to/Web_September_FY25.xlsb'
]);
const result = await client.data.getJobStatus(job.job_id);

// Create scenario
const scenario = await client.scenarios.create({
  brief: {...},
  scenario_type: 'balanced'
});
```

