# Data Models

This document describes the core data structures used throughout the system.

## Core Models

### PromoContext

Represents the contextual environment for promotional planning.

```typescript
interface PromoContext {
  geo: string;  // e.g., "DE", "UA"
  date_range: {
    start: string;  // ISO date
    end: string;
  };
  events: Event[];
  seasonality_factors: SeasonalityFactor[];
  weekend_pattern: {
    weekend_days: string[];  // ["SAT", "SUN"]
  };
  weather_profile: {
    location: string;  // Geographic code (e.g., "DE", "UA")
    coordinates?: {
      latitude: number;
      longitude: number;
      name: string;
    };
    summary: string;  // "rainy_weekend, with 2 rainy day(s), avg 12.5°C"
    daily: DailyWeather[];
  };
}

interface Event {
  name: string;
  date: string;  // ISO date
  type: "global_sale" | "public_holiday" | "local_event" | "payday";
  impact?: "high" | "medium" | "low";
}

interface SeasonalityFactor {
  department: string;
  month: number;
  factor: number;  // Multiplier (1.1 = 10% above average)
}

interface DailyWeather {
  date: string;
  condition: "sun" | "cloud" | "rain" | "snow" | "storm";
  temp_max: number;  // Celsius
  temp_min: number;  // Celsius
  temp_avg: number;  // Celsius
  rain_prob: number;  // 0-100
  rain_sum: number;  // mm
  cloud_cover?: number;  // 0-100
}
```

### PromoBrief

Structured brief extracted from user input.

```typescript
interface PromoBrief {
  month: string;  // "2024-10"
  promo_date_range: {
    start: string;
    end: string;
  };
  gap_to_target: {
    sales_value: number;  // Negative = below target
    margin_points: number;
  };
  objectives: {
    sales_value_target: number;
    margin_floor_pct: number;
    ebit_target?: number;
  };
  focus_departments: string[];  // ["TV", "Gaming"]
  channels: ("online" | "offline")[];
  risk_appetite: "low" | "medium" | "high";
  loyalty_focus: boolean;
  constraints: {
    max_discount_pct: Record<string, number>;  // By department
    min_margin_pct: number;
    excluded_brands?: string[];
  };
}
```

### PromoOpportunity

Identified opportunity for a promotional campaign.

```typescript
interface PromoOpportunity {
  id: string;
  title: string;
  promo_date_range: {
    start: string;
    end: string;
  };
  description: string;
  focus_departments: string[];
  estimated_potential: {
    sales_value: number;
    margin_impact: number;  // Percentage points
  };
  context_snapshot: PromoContext;
  priority: "high" | "medium" | "low";
}
```

### PromoScenario

A specific promotional scenario with mechanics.

```typescript
interface PromoScenario {
  id: string;
  label: string;  // "Conservative", "Balanced", "Aggressive"
  source_opportunity_id?: string;
  date_range: {
    start: string;
    end: string;
  };
  mechanics: PromoMechanic[];
  scenario_type?: "flash" | "best_deal" | "coupon" | "member_only";
}

interface PromoMechanic {
  department: string;
  channel: "online" | "offline" | "both";
  discount_pct: number;
  segments: string[];  // ["ALL"] or ["LOYAL_HIGH_VALUE"]
  notes?: string;
  product_focus?: string[];  // Specific products/brands
}
```

### ScenarioKPI

Key performance indicators for a scenario.

```typescript
interface ScenarioKPI {
  scenario_id: string;
  period: string;  // "2024-10-22..2024-10-27"
  total: {
    sales_value: number;
    margin_value: number;
    margin_pct: number;
    ebit: number;
    units: number;
  };
  vs_baseline: {
    sales_value_delta: number;
    margin_value_delta: number;
    ebit_delta: number;
    units_delta: number;
  };
  by_channel: ChannelKPI[];
  by_department: DepartmentKPI[];
  by_segment: SegmentKPI[];
}

interface ChannelKPI {
  channel: "online" | "offline";
  sales_value: number;
  margin_pct: number;
  units: number;
}

interface DepartmentKPI {
  department: string;
  sales_value: number;
  margin_pct: number;
  units: number;
}

interface SegmentKPI {
  segment_id: string;
  sales_value: number;
  margin_pct: number;
  units: number;
  comment?: string;
}
```

### ValidationReport

Validation results for a scenario.

```typescript
interface ValidationReport {
  scenario_id: string;
  status: "PASS" | "WARN" | "BLOCK";
  issues: ValidationIssue[];
  overall_score?: number;  // 0-100
}

interface ValidationIssue {
  type: 
    | "margin_threshold"
    | "discount_limit"
    | "kpi_plausibility"
    | "brand_compliance"
    | "cannibalization_risk";
  severity: "low" | "medium" | "high" | "critical";
  message: string;
  suggested_fix?: string;
  affected_department?: string;
}
```

### PostMortemReport

Post-campaign analysis report.

```typescript
interface PostMortemReport {
  scenario_id: string;
  period: string;
  forecast_kpi: ScenarioKPI;
  actual_kpi: {
    total: {
      sales_value: number;
      margin_value: number;
      margin_pct: number;
      ebit: number;
      units: number;
    };
  };
  vs_forecast: {
    sales_value_error_pct: number;  // Negative = under-forecast
    margin_value_error_pct: number;
    ebit_error_pct: number;
    units_error_pct: number;
  };
  post_promo_dip?: {
    period: string;
    sales_vs_baseline_delta: number;
  };
  cannibalization_signals: CannibalizationSignal[];
  insights: string[];
  learning_points: string[];
}

interface CannibalizationSignal {
  department: string;
  effect: "negative" | "positive" | "neutral";
  sales_vs_baseline_delta_pct: number;
  comment: string;
}
```

### CreativeBrief

Creative brief for campaign assets.

```typescript
interface CreativeBrief {
  scenario_id: string;
  objectives: {
    primary: string;
    secondary: string[];
  };
  target_audience: {
    segments: string[];
    demographics?: string;
    psychographics?: string;
  };
  key_messages: string[];
  tone: string;  // "energetic", "trustworthy", "urgent"
  mandatory_elements: {
    legal: string[];
    brand: string[];
  };
  assets: AssetSpec[];
}

interface AssetSpec {
  type: 
    | "homepage_hero"
    | "category_banner"
    | "in_store_sheet"
    | "email_hero"
    | "video_storyboard";
  title: string;
  headline: string;
  subheadline?: string;
  cta: string;
  product_focus: string[];
  layout_hints?: string;
  segment_specific?: boolean;
  target_segment?: string;
}
```

### Segment

Customer segment from CDP.

```typescript
interface Segment {
  segment_id: string;
  name: string;
  share_of_customers: number;  // 0-1
  share_of_revenue: number;  // 0-1
  avg_basket_value: number;
  fav_categories: string[];
  discount_sensitivity: "low" | "medium" | "high";
  purchase_frequency?: number;
  last_purchase_days_ago?: number;
}
```

### UpliftModel

Uplift coefficients for forecasting.

```typescript
interface UpliftModel {
  coefficients: UpliftCoefficient[];
  last_updated: string;
  version: string;
}

interface UpliftCoefficient {
  department: string;
  channel: "online" | "offline";
  discount_band: string;  // "0-10", "10-20", "20-30", "30+"
  uplift_sales_pct: number;  // Percentage uplift
  uplift_units_pct: number;
  margin_impact_pct: number;  // Change in margin percentage points
  confidence?: number;  // 0-1
  sample_size?: number;
}
```

### BaselineForecast

Baseline forecast without promotions.

```typescript
interface BaselineForecast {
  period: {
    start: string;
    end: string;
  };
  daily: DailyForecast[];
  totals: {
    sales_value: number;
    margin_value: number;
    margin_pct: number;
    units: number;
  };
  by_channel: ChannelForecast[];
  by_department: DepartmentForecast[];
}

interface DailyForecast {
  date: string;
  sales_value: number;
  margin_value: number;
  units: number;
  day_of_week: string;
}

interface ChannelForecast {
  channel: "online" | "offline";
  sales_value: number;
  margin_pct: number;
}

interface DepartmentForecast {
  department: string;
  sales_value: number;
  margin_pct: number;
}
```

## Database Schema (PostgreSQL)

### Tables

```sql
-- Promotional scenarios
CREATE TABLE promo_scenarios (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    label VARCHAR(100) NOT NULL,
    source_opportunity_id UUID,
    date_range_start DATE NOT NULL,
    date_range_end DATE NOT NULL,
    scenario_type VARCHAR(50),
    mechanics JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Scenario KPIs
CREATE TABLE scenario_kpis (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    scenario_id UUID REFERENCES promo_scenarios(id),
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,
    total_sales_value NUMERIC(15,2),
    total_margin_value NUMERIC(15,2),
    total_margin_pct NUMERIC(5,2),
    total_ebit NUMERIC(15,2),
    total_units INTEGER,
    kpi_breakdown JSONB,  -- by_channel, by_department, by_segment
    created_at TIMESTAMP DEFAULT NOW()
);

-- Validation reports
CREATE TABLE validation_reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    scenario_id UUID REFERENCES promo_scenarios(id),
    status VARCHAR(20) NOT NULL,
    issues JSONB,
    overall_score INTEGER,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Post-mortem reports
CREATE TABLE post_mortem_reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    scenario_id UUID REFERENCES promo_scenarios(id),
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,
    forecast_kpi_id UUID REFERENCES scenario_kpis(id),
    actual_kpi JSONB NOT NULL,
    vs_forecast JSONB,
    insights TEXT[],
    created_at TIMESTAMP DEFAULT NOW()
);

-- Creative briefs
CREATE TABLE creative_briefs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    scenario_id UUID REFERENCES promo_scenarios(id),
    brief JSONB NOT NULL,
    assets JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Historical sales data (aggregated)
CREATE TABLE sales_aggregated (
    date DATE NOT NULL,
    channel VARCHAR(20) NOT NULL,
    department VARCHAR(50) NOT NULL,
    promo_flag BOOLEAN DEFAULT FALSE,
    discount_pct NUMERIC(5,2),
    sales_value NUMERIC(15,2),
    margin_value NUMERIC(15,2),
    units INTEGER,
    PRIMARY KEY (date, channel, department)
);

-- Customer segments (from CDP)
CREATE TABLE segments (
    segment_id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    share_of_customers NUMERIC(5,4),
    share_of_revenue NUMERIC(5,4),
    avg_basket_value NUMERIC(10,2),
    fav_categories TEXT[],
    discount_sensitivity VARCHAR(20),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Uplift model coefficients
CREATE TABLE uplift_coefficients (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    department VARCHAR(50) NOT NULL,
    channel VARCHAR(20) NOT NULL,
    discount_band VARCHAR(20) NOT NULL,
    uplift_sales_pct NUMERIC(6,2),
    uplift_units_pct NUMERIC(6,2),
    margin_impact_pct NUMERIC(6,2),
    confidence NUMERIC(3,2),
    sample_size INTEGER,
    model_version VARCHAR(20),
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE (department, channel, discount_band, model_version)
);
```

## API Request/Response Models

### Create Scenario Request

```typescript
interface CreateScenarioRequest {
  brief: PromoBrief;
  scenario_type?: "conservative" | "balanced" | "aggressive";
  custom_parameters?: Record<string, any>;
}
```

### Evaluate Scenario Response

```typescript
interface EvaluateScenarioResponse {
  scenario: PromoScenario;
  kpi: ScenarioKPI;
  validation: ValidationReport;
  baseline_comparison: {
    sales_delta: number;
    margin_delta: number;
    ebit_delta: number;
  };
}
```

### Optimize Scenarios Request

```typescript
interface OptimizeScenariosRequest {
  brief: PromoBrief;
  objectives: {
    maximize: "sales" | "margin" | "ebit";
    constraints: {
      min_margin_pct?: number;
      max_discount_pct?: number;
    };
  };
  num_scenarios?: number;  // Default: 3
}
```

### Generate Creative Request

```typescript
interface GenerateCreativeRequest {
  scenario_id: string;
  asset_types?: string[];  // If omitted, generates all
  target_segments?: string[];
}
```

## Data Validation

All models should be validated using:

- **Python**: Pydantic models
- **TypeScript**: Zod schemas
- **API**: FastAPI automatic validation

Example Pydantic model:

```python
from pydantic import BaseModel, Field, validator
from typing import List, Optional
from datetime import date

class PromoBrief(BaseModel):
    month: str = Field(..., regex=r"^\d{4}-\d{2}$")
    promo_date_range: dict
    gap_to_target: dict
    objectives: dict
    focus_departments: List[str]
    channels: List[str]
    risk_appetite: str = Field(..., regex="^(low|medium|high)$")
    loyalty_focus: bool
    constraints: dict
    
    @validator('channels')
    def validate_channels(cls, v):
        allowed = ['online', 'offline']
        if not all(c in allowed for c in v):
            raise ValueError('Invalid channel')
        return v
```

