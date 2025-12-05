# API Documentation

## Base URL

- **Development**: `http://localhost:8000`
- **Production**: `https://api.promo-co-pilot.com`

## Authentication

All endpoints require authentication via API key:

```
Authorization: Bearer <api_key>
```

## Endpoints

### Discovery & Context

#### GET /api/v1/discovery/context

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
    "events": [...],
    "weather_profile": {...},
    "seasonality_factors": [...]
  }
}
```

#### POST /api/v1/discovery/analyze

Analyze situation and identify opportunities.

**Request Body**:
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
  "baseline_forecast": {...},
  "gap_analysis": {
    "sales_gap": -3000000,
    "margin_gap": -0.5
  },
  "opportunities": [
    {
      "id": "opp_01",
      "title": "Close October gap with TVs+Gaming",
      "estimated_potential": {...}
    }
  ]
}
```

### Scenario Management

#### POST /api/v1/scenarios/create

Create a new promotional scenario.

**Request Body**:
```json
{
  "brief": {
    "month": "2024-10",
    "promo_date_range": {
      "start": "2024-10-22",
      "end": "2024-10-27"
    },
    "focus_departments": ["TV", "Gaming"],
    "objectives": {...},
    "constraints": {...}
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
    "mechanics": [...],
    "date_range": {...}
  },
  "kpi": {
    "total": {...},
    "vs_baseline": {...}
  },
  "validation": {
    "status": "PASS",
    "issues": []
  }
}
```

#### GET /api/v1/scenarios/{scenario_id}

Get scenario details with KPIs.

**Response**:
```json
{
  "scenario": {...},
  "kpi": {...},
  "validation": {...}
}
```

#### PUT /api/v1/scenarios/{scenario_id}

Update scenario parameters.

**Request Body**:
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

**Response**: Updated scenario with recalculated KPIs.

#### POST /api/v1/scenarios/{scenario_id}/evaluate

Re-evaluate scenario KPIs (useful after parameter changes).

**Response**:
```json
{
  "kpi": {...},
  "validation": {...}
}
```

#### POST /api/v1/scenarios/compare

Compare multiple scenarios side-by-side.

**Request Body**:
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
        "kpi": {...}
      },
      ...
    ],
    "summary": {
      "best_sales": "scenario_3",
      "best_margin": "scenario_1",
      "best_ebit": "scenario_2"
    }
  }
}
```

### Optimization

#### POST /api/v1/optimization/generate

Generate optimized scenarios.

**Request Body**:
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
      "score": 0.85
    },
    ...
  ],
  "efficient_frontier": {
    "points": [
      {"sales": 3000000, "margin": 22.5, "scenario_id": "..."},
      ...
    ]
  }
}
```

#### GET /api/v1/optimization/frontier

Get efficient frontier data for visualization.

**Query Parameters**:
- `brief_id` (required): Brief identifier
- `x_axis`: "sales" | "margin" | "ebit" (default: "sales")
- `y_axis`: "sales" | "margin" | "ebit" (default: "margin")

**Response**:
```json
{
  "frontier": {
    "points": [...],
    "pareto_optimal": ["scenario_1", "scenario_2"]
  }
}
```

### Creative Generation

#### POST /api/v1/creative/generate

Generate creative brief and assets for selected scenarios.

**Request Body**:
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
        "objectives": {...},
        "key_messages": [...],
        "tone": "energetic",
        "assets": [...]
      }
    }
  ]
}
```

#### GET /api/v1/creative/{brief_id}

Get creative brief details.

**Response**:
```json
{
  "brief": {...},
  "assets": [...]
}
```

### Post-Mortem

#### POST /api/v1/postmortem/analyze

Analyze completed campaign performance.

**Request Body**:
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
    "insights": [...]
  }
}
```

#### GET /api/v1/postmortem/{scenario_id}

Get post-mortem report for a scenario.

**Response**: PostMortemReport object

### Data & Tools

#### GET /api/v1/data/baseline

Get baseline forecast.

**Query Parameters**:
- `start_date` (required)
- `end_date` (required)
- `department` (optional)
- `channel` (optional)

**Response**: BaselineForecast object

#### GET /api/v1/data/segments

Get customer segments from CDP.

**Response**:
```json
{
  "segments": [
    {
      "segment_id": "LOYAL_HIGH_VALUE",
      "name": "Loyal High Value",
      "share_of_customers": 0.18,
      ...
    },
    ...
  ]
}
```

#### GET /api/v1/data/uplift-model

Get current uplift model coefficients.

**Query Parameters**:
- `department` (optional)
- `channel` (optional)

**Response**: UpliftModel object

### Chat / Co-Pilot

#### POST /api/v1/chat/message

Send message to co-pilot agent.

**Request Body**:
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
  "response": "Scenario B offers a better balance...",
  "suggestions": [
    "Try adjusting the discount on TVs",
    "Consider focusing on loyal customers"
  ],
  "related_data": {
    "scenario_ids": ["scenario_B"]
  }
}
```

#### POST /api/v1/chat/stream

Stream chat response (SSE).

**Request Body**: Same as `/chat/message`

**Response**: Server-Sent Events stream

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
    }
  }
}
```

### Error Codes

- `VALIDATION_ERROR`: Request validation failed
- `NOT_FOUND`: Resource not found
- `UNAUTHORIZED`: Authentication required
- `FORBIDDEN`: Insufficient permissions
- `INTERNAL_ERROR`: Server error
- `RATE_LIMIT_EXCEEDED`: Too many requests

## Rate Limiting

- **Standard endpoints**: 100 requests/minute
- **Optimization endpoints**: 10 requests/minute
- **Chat endpoints**: 30 requests/minute

Rate limit headers:
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

Triggered when a scenario passes validation.

**Payload**:
```json
{
  "event": "scenario.validated",
  "scenario_id": "scenario_123",
  "timestamp": "2024-10-20T10:00:00Z"
}
```

### Creative Generated

Triggered when creative brief is generated.

**Payload**:
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

# Create scenario
scenario = client.scenarios.create(
    brief={
        "month": "2024-10",
        "focus_departments": ["TV", "Gaming"],
        ...
    },
    scenario_type="balanced"
)

# Get KPIs
kpi = client.scenarios.evaluate(scenario.id)

# Generate creative
creative = client.creative.generate(
    scenario_ids=[scenario.id],
    asset_types=["homepage_hero", "category_banner"]
)
```

### JavaScript/TypeScript

```typescript
import { PromoCoPilotClient } from '@promo-co-pilot/sdk';

const client = new PromoCoPilotClient({
  apiKey: 'your_api_key',
  baseUrl: 'http://localhost:8000'
});

// Create scenario
const scenario = await client.scenarios.create({
  brief: {
    month: '2024-10',
    focus_departments: ['TV', 'Gaming'],
    ...
  },
  scenario_type: 'balanced'
});

// Get KPIs
const kpi = await client.scenarios.evaluate(scenario.id);

// Generate creative
const creative = await client.creative.generate({
  scenario_ids: [scenario.id],
  asset_types: ['homepage_hero', 'category_banner']
});
```



