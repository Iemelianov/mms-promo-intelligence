# API Specification

## Base Information

- **Base URL**: `https://api.promo-co-pilot.com/v1`
- **Protocol**: HTTPS
- **Content-Type**: `application/json`
- **Authentication**: Bearer token in `Authorization` header

## Authentication

All endpoints require authentication:

```
Authorization: Bearer <api_key>
```

### Get API Key

```http
POST /auth/api-keys
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

### POST /data/process

Process XLSB files (sales data) and load into database.

**Request**:
```json
{
  "files": [
    "/path/to/Web_September_FY25.xlsb",
    "/path/to/Stores_October-January_FY25.xlsb"
  ],
  "options": {
    "merge_strategy": "union",  // "union" | "intersect" | "overwrite"
    "validate_quality": true,
    "generate_report": true
  }
}
```

### POST /data/process/promo

Process promotional catalog XLSB file (e.g., Promo_October-September_FY25.xlsb).

**Request**:
```json
{
  "file": "/path/to/Promo_October-September_FY25.xlsb",
  "options": {
    "extract_campaigns": true,
    "load_to_db": true,
    "validate_quality": true
  }
}
```

**Response**:
```json
{
  "job_id": "job_promo_123456",
  "status": "completed",
  "result": {
    "campaigns_extracted": 45,
    "records_processed": 96653,
    "quality_report": {
      "overall_score": 0.97,
      "issues": []
    },
    "campaigns": [
      {
        "id": "promo_period_1_2024-10-01",
        "promo_name": "Promo Period 1",
        "date_start": "2024-10-01",
        "date_end": "2024-10-07",
        "departments": ["TV", "Gaming"],
        "channels": ["online", "offline"],
        "avg_discount_pct": 20.5
      }
    ]
  }
}
```

**Response**:
```json
{
  "job_id": "job_123456",
  "status": "processing",
  "files_queued": 2,
  "estimated_time_seconds": 120
}
```

### GET /data/process/{job_id}

Get processing job status.

**Response**:
```json
{
  "job_id": "job_123456",
  "status": "completed",  // "queued" | "processing" | "completed" | "failed"
  "progress": {
    "files_processed": 2,
    "total_files": 2,
    "records_processed": 150000,
    "errors": 0
  },
  "result": {
    "data_quality_report": {
      "total_records": 150000,
      "clean_records": 149500,
      "issues": [
        {
          "type": "missing_values",
          "count": 500,
          "columns": ["margin_value"]
        }
      ]
    },
    "date_range": {
      "start": "2024-09-01",
      "end": "2025-01-31"
    },
    "channels": ["online", "offline"],
    "departments": ["TV", "Gaming", "Audio", "Accessories"]
  },
  "completed_at": "2024-10-20T10:30:00Z"
}
```

### GET /data/quality

Get data quality report for stored data.

**Query Parameters**:
- `start_date` (optional): Filter start date
- `end_date` (optional): Filter end date
- `channel` (optional): Filter by channel
- `department` (optional): Filter by department

**Response**:
```json
{
  "summary": {
    "total_records": 500000,
    "date_range": {
      "start": "2024-02-01",
      "end": "2025-01-31"
    },
    "channels": {
      "online": 250000,
      "offline": 250000
    },
    "departments": {
      "TV": 150000,
      "Gaming": 120000,
      "Audio": 100000,
      "Accessories": 130000
    }
  },
  "quality_metrics": {
    "completeness": 0.99,
    "accuracy": 0.98,
    "consistency": 0.97,
    "timeliness": 0.95
  },
  "issues": [
    {
      "type": "missing_values",
      "severity": "low",
      "count": 5000,
      "affected_columns": ["margin_value"],
      "affected_dates": ["2024-03-15", "2024-03-16"]
    }
  ]
}
```

## Discovery Endpoints

### GET /discovery/context

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

### POST /discovery/analyze

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

### POST /scenarios

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

### GET /scenarios/{scenario_id}

Get scenario details.

**Response**: Same as POST /scenarios response

### PUT /scenarios/{scenario_id}

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

### DELETE /scenarios/{scenario_id}

Delete a scenario.

**Response**:
```json
{
  "deleted": true,
  "scenario_id": "scenario_123"
}
```

### POST /scenarios/compare

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

### POST /optimization/generate

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

### POST /creative/generate

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
      "scenario_id": "scenario_123",
      "creative_brief": {
        "objectives": {
          "primary": "Close October sales gap",
          "secondary": ["Maintain margin", "Drive online traffic"]
        },
        "target_audience": {
          "segments": ["LOYAL_HIGH_VALUE"],
          "demographics": "25-45, tech-savvy"
        },
        "key_messages": [
          "Exclusive member pricing",
          "Limited time offer",
          "Top brands included"
        ],
        "tone": "energetic",
        "assets": [
          {
            "type": "homepage_hero",
            "headline": "Member-Exclusive TV & Gaming Sale",
            "subheadline": "Up to 20% off selected models",
            "cta": "Shop Now - Members Only",
            "product_focus": ["TV", "Gaming"]
          }
        ]
      }
    }
  ]
}
```

## Post-Mortem Endpoints

### POST /postmortem/analyze

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

### POST /chat/message

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

### POST /chat/stream

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

