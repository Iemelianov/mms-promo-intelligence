export interface DateRange { start_date: string; end_date: string }
export interface PromoContext { geo: string; date_range: DateRange; events: any[]; weather?: any }
export interface PromoOpportunity { id: string; department: string; channel: string; estimated_potential: number; priority: number }
export interface PromoScenario { id?: string; name: string; description?: string; date_range: DateRange; departments: string[]; channels: string[]; discount_percentage: number }
export interface ScenarioKPI { total_sales: number; total_margin: number; total_ebit: number; total_units: number }



