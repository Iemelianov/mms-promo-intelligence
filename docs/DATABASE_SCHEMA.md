# Database Schema

## Overview

The system uses PostgreSQL for production and DuckDB for local development. The schema is designed to support:
- Historical sales data storage and aggregation
- Promotional scenario management
- KPI tracking and analysis
- Creative asset management
- Post-mortem analysis
- Learning and model updates

## Schema Version

Current version: `1.0.0`

## Core Tables

### sales_aggregated

Stores daily aggregated sales data by channel and department.

```sql
CREATE TABLE sales_aggregated (
    id BIGSERIAL PRIMARY KEY,
    date DATE NOT NULL,
    channel VARCHAR(20) NOT NULL CHECK (channel IN ('online', 'offline')),
    department VARCHAR(50) NOT NULL,
    promo_flag BOOLEAN DEFAULT FALSE,
    discount_pct NUMERIC(5,2),
    sales_value NUMERIC(15,2) NOT NULL,
    margin_value NUMERIC(15,2) NOT NULL,
    margin_pct NUMERIC(5,2) GENERATED ALWAYS AS (
        CASE WHEN sales_value > 0 
        THEN (margin_value / sales_value * 100) 
        ELSE 0 END
    ) STORED,
    units INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    CONSTRAINT unique_sales_record UNIQUE (date, channel, department, promo_flag)
);

CREATE INDEX idx_sales_date ON sales_aggregated(date);
CREATE INDEX idx_sales_channel ON sales_aggregated(channel);
CREATE INDEX idx_sales_department ON sales_aggregated(department);
CREATE INDEX idx_sales_promo ON sales_aggregated(promo_flag);
CREATE INDEX idx_sales_date_channel ON sales_aggregated(date, channel);
CREATE INDEX idx_sales_date_department ON sales_aggregated(date, department);
```

**Data Sources**: Processed from XLSB files by Data Analyst Agent

**Sample Data**:
```sql
INSERT INTO sales_aggregated (date, channel, department, promo_flag, discount_pct, sales_value, margin_value, units)
VALUES 
    ('2024-10-01', 'online', 'TV', false, NULL, 50000, 12500, 100),
    ('2024-10-02', 'online', 'TV', true, 20.0, 75000, 15000, 150);
```

### promo_scenarios

Stores promotional scenario definitions.

```sql
CREATE TABLE promo_scenarios (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    label VARCHAR(100) NOT NULL,
    source_opportunity_id UUID,
    date_range_start DATE NOT NULL,
    date_range_end DATE NOT NULL,
    scenario_type VARCHAR(50) CHECK (scenario_type IN ('conservative', 'balanced', 'aggressive', 'flash', 'best_deal', 'coupon', 'member_only')),
    mechanics JSONB NOT NULL,
    created_by VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    CHECK (date_range_end >= date_range_start)
);

CREATE INDEX idx_scenarios_date_range ON promo_scenarios(date_range_start, date_range_end);
CREATE INDEX idx_scenarios_type ON promo_scenarios(scenario_type);
CREATE INDEX idx_scenarios_created_at ON promo_scenarios(created_at);
```

**mechanics JSONB Structure**:
```json
[
  {
    "department": "TV",
    "channel": "online",
    "discount_pct": 20,
    "segments": ["ALL"],
    "notes": "main hero"
  }
]
```

### scenario_kpis

Stores calculated KPIs for scenarios.

```sql
CREATE TABLE scenario_kpis (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    scenario_id UUID NOT NULL REFERENCES promo_scenarios(id) ON DELETE CASCADE,
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,
    total_sales_value NUMERIC(15,2) NOT NULL,
    total_margin_value NUMERIC(15,2) NOT NULL,
    total_margin_pct NUMERIC(5,2) NOT NULL,
    total_ebit NUMERIC(15,2) NOT NULL,
    total_units INTEGER NOT NULL,
    sales_value_delta NUMERIC(15,2) NOT NULL,
    margin_value_delta NUMERIC(15,2) NOT NULL,
    ebit_delta NUMERIC(15,2) NOT NULL,
    units_delta INTEGER NOT NULL,
    kpi_breakdown JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    CHECK (period_end >= period_start)
);

CREATE INDEX idx_kpis_scenario ON scenario_kpis(scenario_id);
CREATE INDEX idx_kpis_period ON scenario_kpis(period_start, period_end);
```

**kpi_breakdown JSONB Structure**:
```json
{
  "by_channel": [
    {
      "channel": "online",
      "sales_value": 2100000,
      "margin_pct": 21.5,
      "units": 12000
    }
  ],
  "by_department": [
    {
      "department": "TV",
      "sales_value": 2000000,
      "margin_pct": 21.0,
      "units": 10000
    }
  ],
  "by_segment": [
    {
      "segment_id": "LOYAL_HIGH_VALUE",
      "sales_value": 1500000,
      "margin_pct": 23.0,
      "units": 8000
    }
  ]
}
```

### validation_reports

Stores validation results for scenarios.

```sql
CREATE TABLE validation_reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    scenario_id UUID NOT NULL REFERENCES promo_scenarios(id) ON DELETE CASCADE,
    status VARCHAR(20) NOT NULL CHECK (status IN ('PASS', 'WARN', 'BLOCK')),
    issues JSONB,
    overall_score INTEGER CHECK (overall_score >= 0 AND overall_score <= 100),
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE (scenario_id)
);

CREATE INDEX idx_validation_status ON validation_reports(status);
CREATE INDEX idx_validation_scenario ON validation_reports(scenario_id);
```

**issues JSONB Structure**:
```json
[
  {
    "type": "margin_threshold",
    "severity": "medium",
    "message": "Margin below minimum threshold",
    "suggested_fix": "Reduce discount by 2%",
    "affected_department": "TV"
  }
]
```

### post_mortem_reports

Stores post-campaign analysis reports.

```sql
CREATE TABLE post_mortem_reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    scenario_id UUID NOT NULL REFERENCES promo_scenarios(id) ON DELETE CASCADE,
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,
    forecast_kpi_id UUID REFERENCES scenario_kpis(id),
    actual_sales_value NUMERIC(15,2) NOT NULL,
    actual_margin_value NUMERIC(15,2) NOT NULL,
    actual_margin_pct NUMERIC(5,2) NOT NULL,
    actual_ebit NUMERIC(15,2) NOT NULL,
    actual_units INTEGER NOT NULL,
    sales_value_error_pct NUMERIC(6,2) NOT NULL,
    margin_value_error_pct NUMERIC(6,2) NOT NULL,
    ebit_error_pct NUMERIC(6,2) NOT NULL,
    units_error_pct NUMERIC(6,2) NOT NULL,
    post_promo_dip JSONB,
    cannibalization_signals JSONB,
    insights TEXT[],
    learning_points TEXT[],
    created_at TIMESTAMP DEFAULT NOW(),
    CHECK (period_end >= period_start)
);

CREATE INDEX idx_postmortem_scenario ON post_mortem_reports(scenario_id);
CREATE INDEX idx_postmortem_period ON post_mortem_reports(period_start, period_end);
```

### creative_briefs

Stores creative briefs and asset specifications.

```sql
CREATE TABLE creative_briefs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    scenario_id UUID NOT NULL REFERENCES promo_scenarios(id) ON DELETE CASCADE,
    brief JSONB NOT NULL,
    assets JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_creative_scenario ON creative_briefs(scenario_id);
```

**brief JSONB Structure**:
```json
{
  "objectives": {
    "primary": "Close October sales gap",
    "secondary": ["Maintain margin", "Drive online traffic"]
  },
  "target_audience": {
    "segments": ["LOYAL_HIGH_VALUE"],
    "demographics": "25-45, tech-savvy"
  },
  "key_messages": ["Exclusive member pricing", "Limited time offer"],
  "tone": "energetic",
  "mandatory_elements": {
    "legal": ["Terms and conditions apply"],
    "brand": ["MediaMarkt logo"]
  }
}
```

**assets JSONB Structure**:
```json
[
  {
    "type": "homepage_hero",
    "headline": "Member-Exclusive TV & Gaming Sale",
    "subheadline": "Up to 20% off selected models",
    "cta": "Shop Now - Members Only",
    "product_focus": ["TV", "Gaming"]
  }
]
```

### segments

Stores customer segment definitions from CDP.

```sql
CREATE TABLE segments (
    segment_id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    share_of_customers NUMERIC(5,4) NOT NULL CHECK (share_of_customers >= 0 AND share_of_customers <= 1),
    share_of_revenue NUMERIC(5,4) NOT NULL CHECK (share_of_revenue >= 0 AND share_of_revenue <= 1),
    avg_basket_value NUMERIC(10,2) NOT NULL,
    fav_categories TEXT[],
    discount_sensitivity VARCHAR(20) CHECK (discount_sensitivity IN ('low', 'medium', 'high')),
    purchase_frequency NUMERIC(5,2),
    last_purchase_days_ago INTEGER,
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### uplift_coefficients

Stores uplift model coefficients for forecasting.

```sql
CREATE TABLE uplift_coefficients (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    department VARCHAR(50) NOT NULL,
    channel VARCHAR(20) NOT NULL CHECK (channel IN ('online', 'offline')),
    discount_band VARCHAR(20) NOT NULL,
    uplift_sales_pct NUMERIC(6,2) NOT NULL,
    uplift_units_pct NUMERIC(6,2) NOT NULL,
    margin_impact_pct NUMERIC(6,2) NOT NULL,
    confidence NUMERIC(3,2) CHECK (confidence >= 0 AND confidence <= 1),
    sample_size INTEGER,
    model_version VARCHAR(20) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE (department, channel, discount_band, model_version)
);

CREATE INDEX idx_uplift_department ON uplift_coefficients(department);
CREATE INDEX idx_uplift_channel ON uplift_coefficients(channel);
CREATE INDEX idx_uplift_version ON uplift_coefficients(model_version);
```

### data_processing_jobs

Tracks data processing jobs from Data Analyst Agent.

```sql
CREATE TABLE data_processing_jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id VARCHAR(100) UNIQUE NOT NULL,
    status VARCHAR(20) NOT NULL CHECK (status IN ('queued', 'processing', 'completed', 'failed')),
    files_queued INTEGER NOT NULL,
    files_processed INTEGER DEFAULT 0,
    records_processed BIGINT DEFAULT 0,
    errors INTEGER DEFAULT 0,
    result JSONB,
    error_message TEXT,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_jobs_status ON data_processing_jobs(status);
CREATE INDEX idx_jobs_created_at ON data_processing_jobs(created_at);
```

### targets

Stores monthly targets for comparison.

```sql
CREATE TABLE targets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    month VARCHAR(7) NOT NULL,  -- Format: YYYY-MM
    geo VARCHAR(10) NOT NULL,
    sales_value_target NUMERIC(15,2) NOT NULL,
    margin_pct_target NUMERIC(5,2) NOT NULL,
    units_target INTEGER,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE (month, geo)
);

CREATE INDEX idx_targets_month ON targets(month);
CREATE INDEX idx_targets_geo ON targets(geo);
```

### promo_catalog

Stores historical promotional campaign data.
Populated from XLSB files (e.g., Promo_October-September_FY25.xlsb).

```sql
CREATE TABLE promo_catalog (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    promo_name VARCHAR(200),
    date_start DATE NOT NULL,
    date_end DATE NOT NULL,
    departments TEXT[],
    channels TEXT[],
    avg_discount_pct NUMERIC(5,2),
    mechanics JSONB,
    source_file VARCHAR(500),  -- Path to source XLSB file
    created_at TIMESTAMP DEFAULT NOW(),
    CHECK (date_end >= date_start)
);

CREATE INDEX idx_promo_dates ON promo_catalog(date_start, date_end);
CREATE INDEX idx_promo_departments ON promo_catalog USING GIN(departments);
CREATE INDEX idx_promo_source_file ON promo_catalog(source_file);
```

**Data Source**: Processed from XLSB files by PromoProcessor

## Views

### sales_daily_summary

Daily summary view for quick queries.

```sql
CREATE VIEW sales_daily_summary AS
SELECT 
    date,
    channel,
    SUM(sales_value) as total_sales_value,
    SUM(margin_value) as total_margin_value,
    AVG(margin_pct) as avg_margin_pct,
    SUM(units) as total_units,
    COUNT(*) FILTER (WHERE promo_flag = true) as promo_days_count
FROM sales_aggregated
GROUP BY date, channel;
```

### scenario_comparison_view

View for comparing scenarios side-by-side.

```sql
CREATE VIEW scenario_comparison_view AS
SELECT 
    ps.id as scenario_id,
    ps.label,
    ps.scenario_type,
    ps.date_range_start,
    ps.date_range_end,
    sk.total_sales_value,
    sk.total_margin_pct,
    sk.total_ebit,
    sk.sales_value_delta,
    vr.status as validation_status,
    vr.overall_score
FROM promo_scenarios ps
LEFT JOIN scenario_kpis sk ON ps.id = sk.scenario_id
LEFT JOIN validation_reports vr ON ps.id = vr.scenario_id;
```

## Functions

### calculate_baseline_forecast

Calculate baseline forecast for a date range.

```sql
CREATE OR REPLACE FUNCTION calculate_baseline_forecast(
    p_start_date DATE,
    p_end_date DATE,
    p_channel VARCHAR DEFAULT NULL,
    p_department VARCHAR DEFAULT NULL
)
RETURNS TABLE (
    date DATE,
    forecasted_sales_value NUMERIC,
    forecasted_margin_value NUMERIC,
    forecasted_units INTEGER
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        d.date,
        AVG(sa.sales_value) FILTER (WHERE sa.promo_flag = false) as forecasted_sales_value,
        AVG(sa.margin_value) FILTER (WHERE sa.promo_flag = false) as forecasted_margin_value,
        AVG(sa.units) FILTER (WHERE sa.promo_flag = false)::INTEGER as forecasted_units
    FROM generate_series(p_start_date, p_end_date, '1 day'::interval) d
    LEFT JOIN sales_aggregated sa ON 
        EXTRACT(DOW FROM d.date) = EXTRACT(DOW FROM sa.date)
        AND (p_channel IS NULL OR sa.channel = p_channel)
        AND (p_department IS NULL OR sa.department = p_department)
        AND sa.promo_flag = false
    GROUP BY d.date;
END;
$$ LANGUAGE plpgsql;
```

## Migrations

### Initial Schema (v1.0.0)

```sql
-- Run migrations in order
\i migrations/001_initial_schema.sql
\i migrations/002_add_indexes.sql
\i migrations/003_add_views.sql
\i migrations/004_add_functions.sql
```

## Data Retention

- **sales_aggregated**: Retain indefinitely (historical analysis)
- **scenario_kpis**: Retain 2 years
- **post_mortem_reports**: Retain 3 years (for learning)
- **data_processing_jobs**: Retain 90 days

## Backup Strategy

- Daily full backups
- Point-in-time recovery (PITR) enabled
- Backup retention: 30 days
- Test restore monthly

## Performance Considerations

- Partition `sales_aggregated` by month for large datasets
- Use materialized views for complex aggregations
- Regular VACUUM and ANALYZE
- Monitor query performance with pg_stat_statements

## DuckDB Compatibility

For local development, DuckDB uses similar schema but:
- No UUID type (use VARCHAR)
- Different JSON handling
- Simpler indexing
- No stored procedures (use Python functions)

