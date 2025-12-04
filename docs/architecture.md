# System Architecture

## Overview

Promo Scenario Co-Pilot follows a layered architecture with clear separation of concerns:

1. **UI Layer**: React-based interface with chat co-pilot
2. **Agent Layer**: LangChain-powered orchestrators
3. **Engine Layer**: Business logic and computation
4. **Tools Layer**: Data access and external integrations

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────┐
│                    UI Layer (React)                      │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐             │
│  │Discovery │  │Scenario   │  │Creative  │  Chat Widget│
│  │  Screen  │  │  Lab      │  │Companion │             │
│  └──────────┘  └──────────┘  └──────────┘             │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│                  Agent Layer (LangChain)                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │Discovery     │  │Scenario Lab  │  │Optimization │  │
│  │Agent         │  │Agent         │  │Agent        │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │Creative      │  │Post-Mortem   │  │Validation    │  │
│  │Agent         │  │Agent         │  │Agent         │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
│  ┌──────────────┐                                      │
│  │Data Analyst  │                                      │
│  │Agent         │                                      │
│  └──────────────┘                                      │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│                  Engine Layer (Python)                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │Context       │  │Forecast &    │  │Uplift &      │  │
│  │Engine        │  │Baseline      │  │Elasticity    │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │Scenario      │  │Scenario      │  │Validation    │  │
│  │Evaluation    │  │Optimization  │  │Engine        │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │Creative      │  │Post-Mortem   │  │Learning     │  │
│  │Engine        │  │Analytics    │  │Engine       │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│                   Tools Layer                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │SalesData     │  │PromoCatalog  │  │CDP Tool      │  │
│  │Tool          │  │Tool          │  │(mock)        │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ContextData   │  │Weather       │  │Targets/     │  │
│  │Tool          │  │Tool          │  │Config Tool   │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│              External Services & Data                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │PostgreSQL/   │  │Weather API   │  │Phoenix       │  │
│  │DuckDB        │  │              │  │Arize         │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘
```

## Agent Layer

### 1. Discovery / Context Agent

**Purpose**: Brainstorming, understanding situation, finding opportunities

**Responsibilities**:
- Parse user input to understand context
- Gather contextual data (weather, events, seasonality)
- Calculate baseline forecasts
- Identify gaps vs targets
- Generate promotional opportunities

**Key Methods**:
- `analyze_situation(month, geo, targets) -> PromoOpportunity[]`
- `get_context(date_range, geo) -> PromoContext`
- `identify_gaps(baseline, targets) -> GapAnalysis`

**Tools Used**:
- Context Engine
- Forecast & Baseline Engine
- ContextDataTool
- WeatherTool
- TargetsTool

### 2. Scenario Lab Agent

**Purpose**: Modeling and comparing promotional scenarios

**Responsibilities**:
- Create/update promotional scenarios
- Evaluate scenario KPIs
- Validate scenarios against constraints
- Compare multiple scenarios side-by-side

**Key Methods**:
- `create_scenario(brief, parameters) -> PromoScenario`
- `evaluate_scenario(scenario) -> ScenarioKPI`
- `compare_scenarios(scenarios[]) -> ComparisonReport`
- `validate_scenario(scenario) -> ValidationReport`

**Tools Used**:
- Scenario Evaluation Engine
- Validation Engine
- Forecast & Baseline Engine
- Uplift & Elasticity Engine

### 3. Optimization & Business Impact Agent

**Purpose**: Finding optimal scenarios for maximum business value

**Responsibilities**:
- Generate candidate scenarios
- Optimize scenarios for objectives
- Build efficient frontier (sales vs margin trade-offs)
- Rank scenarios by business impact

**Key Methods**:
- `optimize_scenarios(brief, constraints) -> PromoScenario[]`
- `calculate_efficient_frontier(scenarios[]) -> FrontierData`
- `rank_by_objectives(scenarios[], weights) -> RankedScenarios`

**Tools Used**:
- Scenario Optimization Engine
- Scenario Evaluation Engine
- Validation Engine

### 4. Execution & Creative Agent

**Purpose**: Campaign planning and creative asset generation

**Responsibilities**:
- Finalize selected scenarios
- Generate campaign timeline
- Create creative briefs
- Generate asset specifications and copy

**Key Methods**:
- `finalize_campaign(scenarios[]) -> CampaignPlan`
- `generate_creative_brief(scenario) -> CreativeBrief`
- `generate_assets(brief) -> AssetSpec[]`

**Tools Used**:
- Creative Engine
- Validation Engine
- CDPTool (for segment-specific messaging)

### 5. Post-Mortem & Learning Agent

**Purpose**: Analyze performance and improve models

**Responsibilities**:
- Compare forecast vs actual
- Analyze uplift accuracy
- Detect cannibalization
- Update uplift models

**Key Methods**:
- `analyze_performance(scenario, actual_data) -> PostMortemReport`
- `update_uplift_model(post_mortems[]) -> UpliftModel`
- `generate_insights(report) -> Insights`

**Tools Used**:
- Post-Mortem Analytics Engine
- Learning Engine
- SalesDataTool

### 6. Governance & Validation Agent

**Purpose**: Cross-cutting quality and risk control

**Responsibilities**:
- Validate scenarios against business rules
- Check brand compliance
- Verify financial constraints
- Block invalid scenarios

**Key Methods**:
- `validate_scenario(scenario, rules) -> ValidationReport`
- `check_brand_compliance(creative) -> ComplianceReport`
- `verify_constraints(scenario, constraints) -> ConstraintCheck`

**Tools Used**:
- Validation Engine
- TargetsTool / ConfigTool

### 7. Data Analyst Agent

**Purpose**: Data preparation, cleaning, and ETL operations

**Responsibilities**:
- Load and parse XLSB files (Web and Stores data)
- Clean and standardize data formats
- Merge multiple data files by date ranges
- Detect and handle data quality issues
- Aggregate data by date, channel, department
- Store processed data in local database
- Generate data quality reports
- Prepare data for analysis by other agents

**Key Methods**:
- `load_xlsb_files(file_paths[]) -> RawData`
- `clean_dataframe(df, schema) -> CleanedDataFrame`
- `merge_files(files[], merge_strategy) -> MergedData`
- `validate_data_quality(df) -> QualityReport`
- `store_to_database(df, table_name) -> StorageResult`
- `prepare_analysis_dataset(filters) -> AnalysisDataset`

**Tools Used**:
- XLSBReaderTool (pyxlsb)
- DataCleaningTool (pandas)
- DataValidationTool
- DatabaseStorageTool
- DataQualityTool

**Python Scripts/Tools**:
- `tools/xlsb_reader.py`: Read XLSB files
- `tools/data_cleaner.py`: Clean and standardize data
- `tools/data_merger.py`: Merge multiple files
- `tools/data_validator.py`: Validate data quality
- `tools/db_loader.py`: Load data to database

### 8. Explainer / Co-Pilot (Chat)

**Purpose**: Conversational interface for all screens

**Responsibilities**:
- Answer "why" questions
- Explain complex calculations
- Help brainstorm scenarios
- Provide what-if analysis

**Context Awareness**:
- Current screen/state
- Active scenarios
- Validation reports
- User's current task

## Engine Layer

### Context Engine

Builds comprehensive context for promotional planning.

**Input**: `geo`, `date_range`, external data

**Output**: `PromoContext` with:
- Events and holidays
- Seasonality factors
- Weather profile
- Weekend patterns

**Implementation**:
```python
class ContextEngine:
    def build_context(
        self, 
        geo: str, 
        date_range: DateRange
    ) -> PromoContext:
        events = self.context_tool.get_events(geo, date_range)
        weather = self.weather_tool.get_forecast(geo, date_range)
        seasonality = self.context_tool.get_seasonality(geo)
        return PromoContext(
            events=events,
            weather=weather,
            seasonality=seasonality
        )
```

### Forecast & Baseline Engine

Calculates baseline forecasts without promotions.

**Input**: Historical sales data, context, targets

**Output**: `BaselineForecast` with daily projections

**Methodology**:
- Day-of-week patterns
- Seasonal adjustments
- Trend analysis
- Gap calculation vs targets

### Uplift & Elasticity Engine

Estimates promotional uplift by category/channel.

**Input**: Historical promo data, context

**Output**: `UpliftModel` with coefficients

**Methodology**:
- Compare promo vs non-promo days
- Calculate uplift by discount band
- Adjust for context (weather, events)
- Segment-specific sensitivity

### Scenario Evaluation Engine

Calculates KPIs for a given scenario.

**Input**: `PromoScenario`, baseline, uplift model, context

**Output**: `ScenarioKPI` with:
- Total sales, margin, EBIT
- Breakdown by channel, department, segment
- Comparison vs baseline

### Scenario Optimization Engine

Generates and optimizes scenarios.

**Input**: Brief, constraints, objectives

**Output**: Ranked list of `PromoScenario` with KPIs

**Methodology**:
- Template-based generation (Conservative/Balanced/Aggressive)
- Grid search over discount ranges
- Multi-objective optimization
- Constraint satisfaction

### Validation Engine

Validates scenarios against business rules.

**Input**: Scenario, KPI, rules

**Output**: `ValidationReport` with issues and fixes

**Checks**:
- Discount limits
- Margin thresholds
- KPI plausibility
- Brand compliance

### Creative Engine

Generates creative briefs and copy.

**Input**: Selected scenarios, segments, brand rules

**Output**: `CreativeBrief` with:
- Objectives and messaging
- Asset list
- Copy examples
- Layout hints

### Post-Mortem Analytics Engine

Analyzes actual vs forecasted performance.

**Input**: Scenario, forecast, actual data

**Output**: `PostMortemReport` with:
- Forecast accuracy
- Uplift analysis
- Post-promo dip
- Cannibalization signals

### Learning Engine

Updates uplift models from post-mortems.

**Input**: Post-mortem reports, current model

**Output**: Updated `UpliftModel`

**Methodology**:
- Compare forecasted vs actual uplift
- Adjust coefficients by category/channel
- Weight recent data more heavily

## Tools Layer

### SalesDataTool

Access to historical sales data.

**API**:
```python
get_aggregated_sales(
    date_range: DateRange,
    grain: List[str]  # [date, channel, department, promo_flag]
) -> DataFrame
```

### PromoCatalogTool

Access to historical promotional campaigns.
Supports reading from XLSB files and database.

**API**:
```python
load_from_xlsb(file_path: str) -> DataFrame
process_promo_dataframe(df: DataFrame) -> List[PromoCampaign]
get_past_promos(
    filters: Optional[Dict[str, Any]] = None,
    xlsb_file_path: Optional[str] = None
) -> List[PromoCampaign]
get_promo_by_id(promo_id: str) -> Optional[PromoCampaign]
```

**Features**:
- Reads promotional data from XLSB files (e.g., Promo_October-September_FY25.xlsb)
- Extracts promotional campaigns from data
- Groups by promo name or date ranges with discounts
- Filters by date range, channel, department
- Caches campaigns for performance

### CDPTool (Mock)

Customer data platform integration.

**API**:
```python
get_segments() -> List[Segment]
get_segment_distribution(department: str) -> Dict[str, float]
```

### ContextDataTool

External context data (events, holidays, seasonality).

**API**:
```python
get_events(geo: str, date_range: DateRange) -> List[Event]
get_seasonality_profile(geo: str) -> SeasonalityProfile
```

### WeatherTool

Weather forecast integration using Open-Meteo API (free, no API key required).

**API**:
```python
get_weather_forecast(
    location: str,  # Geographic code (e.g., "DE", "UA") or "lat,lon"
    date_range_start: date,
    date_range_end: date,
    timezone: str = "auto"
) -> WeatherForecast
```

**Features**:
- Free API, no authentication required
- Daily forecasts with temperature, precipitation, cloud cover
- Weather condition mapping (sun, cloud, rain, snow, storm)
- Historical weather data support
- Automatic summary generation

### TargetsTool / ConfigTool

Business targets and configuration.

**API**:
```python
get_targets(month: str) -> Targets
get_promo_constraints() -> Constraints
get_brand_rules() -> BrandRules
```

### DataProcessingTool

Data preparation and ETL operations.

**API**:
```python
process_xlsb_files(file_paths: List[str]) -> ProcessingResult
clean_and_merge_data(raw_data: DataFrame) -> CleanedDataFrame
validate_data_quality(df: DataFrame) -> QualityReport
load_to_database(df: DataFrame, table_name: str) -> StorageResult
```

## Data Processing Flow

### Data Analyst Agent Workflow

```
Raw XLSB Files (Data/)
    ↓
Data Analyst Agent
    ├─→ XLSBReaderTool → Parse files
    ├─→ DataCleaningTool → Standardize formats
    ├─→ DataMergerTool → Merge by date ranges
    ├─→ DataValidatorTool → Quality checks
    └─→ DatabaseStorageTool → Store in DB
    ↓
Processed Data in Database
    ↓
SalesDataTool → Other Agents
```

## Data Flow

### Scenario Generation Flow

```
User Input (Chat)
    ↓
Discovery Agent
    ↓
Context Engine → PromoContext
Forecast Engine → BaselineForecast
    ↓
Scenario Lab Agent
    ↓
Uplift Engine → UpliftModel
Scenario Evaluation Engine → ScenarioKPI
Validation Engine → ValidationReport
    ↓
UI Display (Scenario Comparison Table)
```

### Optimization Flow

```
PromoBrief
    ↓
Optimization Agent
    ↓
Scenario Optimization Engine
    ├─→ Generate Candidate Scenarios
    ├─→ Evaluate Each Scenario
    └─→ Rank by Objectives
    ↓
Validation Engine → ValidationReport
    ↓
UI Display (Efficient Frontier Chart)
```

### Creative Generation Flow

```
Selected Scenario
    ↓
Execution Agent
    ↓
Creative Engine
    ├─→ Generate Brief
    ├─→ Generate Asset Specs
    └─→ Generate Copy
    ↓
UI Display (Creative Brief Panel)
```

## Observability

### Phoenix Arize Integration

All LLM calls are traced through Phoenix:

- Agent invocations
- Tool calls
- Engine computations
- Error tracking
- Latency monitoring

**Key Metrics**:
- Token usage
- Response times
- Error rates
- Scenario evaluation accuracy

## Security & Governance

- All scenarios validated before execution
- Brand compliance checks
- Financial constraint enforcement
- Audit trail of all decisions
- Role-based access control (future)

## Scalability Considerations

- Engines are stateless and can be scaled horizontally
- Tools cache data where appropriate
- LLM calls are rate-limited and batched
- Database queries optimized with indexes
- Frontend uses React Query for caching

