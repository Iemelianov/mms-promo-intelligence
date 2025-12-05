// Shared primitives
export interface DateRange {
  start_date: string
  end_date: string
}

export interface Event {
  name: string
  date: string
  type: 'global_sale' | 'public_holiday' | 'local_event' | 'payday' | string
  impact?: 'high' | 'medium' | 'low'
}

export interface SeasonalityProfile {
  [month: string]: number
}

export interface WeatherProfile {
  location: string
  summary?: string
  daily?: DailyWeather[]
}

export interface DailyWeather {
  date: string
  condition: 'sun' | 'cloud' | 'rain' | 'snow' | 'storm' | string
  temp_max: number
  temp_min: number
  temp_avg: number
  rain_prob?: number
  rain_sum?: number
  cloud_cover?: number
}

// Context / discovery
export interface PromoContext {
  geo: string
  date_range: DateRange
  events: Event[]
  weather?: WeatherProfile | null
  seasonality?: SeasonalityProfile
  weekend_patterns?: Record<string, number>
}

export interface PromoOpportunity {
  id: string
  department: string
  channel: string
  date_range: DateRange
  estimated_potential: number
  priority: number
  rationale: string
}

export interface GapAnalysis {
  sales_gap: number
  margin_gap: number
  units_gap: number
  gap_percentage?: Record<string, number>
}

export interface BaselineForecastTotals {
  sales_value: number
  margin_value: number
  margin_pct: number
  units: number
}

export interface BaselineForecast {
  period: { start: string; end: string }
  totals: BaselineForecastTotals
}

export interface AnalyzeRequest {
  month: string
  geo: string
  targets?: Record<string, unknown>
}

export interface AnalyzeResponse {
  baseline_forecast: BaselineForecast
  gap_analysis: GapAnalysis
  opportunities: PromoOpportunity[]
}

// Scenarios
export interface PromoScenario {
  id?: string
  name: string
  description?: string
  date_range: DateRange
  departments: string[]
  channels: string[]
  discount_percentage: number
  segments?: string[]
  metadata?: Record<string, unknown>
}

export interface ScenarioKPI {
  scenario_id: string
  total_sales: number
  total_margin: number
  total_ebit: number
  total_units: number
  breakdown_by_channel: Record<string, Record<string, number>>
  breakdown_by_department: Record<string, Record<string, number>>
  breakdown_by_segment?: Record<string, Record<string, number>>
  comparison_vs_baseline: Record<string, number>
}

export interface ValidationReport {
  scenario_id: string
  is_valid: boolean
  issues: string[]
  fixes: string[]
  checks_passed: Record<string, boolean>
}

export interface ComparisonReport {
  scenarios: PromoScenario[]
  summary: Record<string, string | number>
}

// Optimization
export interface FrontierData {
  scenarios: PromoScenario[]
  coordinates: [number, number][]
  pareto_optimal: boolean[]
}

export type RankedScenarioTuple = [PromoScenario, number]

// Creative
export interface CreativeBrief {
  scenario_id: string
  objectives: string[]
  messaging: string
  target_audience: string
  tone: string
  style: string
  mandatory_elements: string[]
}

export interface AssetSpec {
  asset_type: string
  copy_text: string
  layout_hints?: Record<string, unknown>
  dimensions?: Record<string, number>
}

// Post-mortem
export interface PostMortemReport {
  scenario_id: string
  period: DateRange
  forecast_kpi: ScenarioKPI
  actual_kpi: Record<string, number>
  vs_forecast: Record<string, number>
  insights: string[]
  learning_points: string[]
}

// Data / quality
export interface QualityReport {
  completeness: number
  accuracy: number
  consistency: number
  timeliness: number
  issues: string[]
  recommendations: string[]
}

export interface StorageResult {
  success: boolean
  rows_inserted: number
  table_name: string
  errors?: string[]
}

export interface DataProcessResult {
  processed_files: Array<Record<string, unknown>>
  storage_result?: StorageResult
}
