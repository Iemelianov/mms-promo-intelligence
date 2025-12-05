import axios, { AxiosError, AxiosResponse } from 'axios'
import type {
  AnalyzeRequest,
  AnalyzeResponse,
  PromoContext,
  PromoOpportunity,
  GapAnalysis,
  PromoScenario,
  ScenarioKPI,
  ValidationReport,
  FrontierData,
  RankedScenarioTuple,
  CreativeBrief,
  AssetSpec,
  DataProcessResult,
  QualityReport,
  ChatMessageRequest,
  ChatMessageResponse,
  PostMortemReport,
} from '../types'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
    Accept: 'application/json',
  },
})

apiClient.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    // Centralised place for logging/observability
    console.error('[API] Request failed', error.response?.status, error.response?.data || error.message)
    return Promise.reject(error)
  }
)

const unwrap = <T>(promise: Promise<AxiosResponse<T>>): Promise<T> => promise.then((res) => res.data)

export default apiClient

// Discovery API
export const discoveryApi = {
  analyze: (payload: AnalyzeRequest) =>
    unwrap(apiClient.post<AnalyzeResponse>('/api/v1/discovery/analyze', payload)),

  context: (geo: string, start_date: string, end_date: string) =>
    unwrap(
      apiClient.get<PromoContext>('/api/v1/discovery/context', {
        params: { geo, start_date, end_date },
      })
    ),

  gaps: (month: string, geo: string) =>
    unwrap(
      apiClient.get<GapAnalysis>('/api/v1/discovery/gaps', {
        params: { month, geo },
      })
    ),

  opportunities: (month: string, geo: string) =>
    unwrap(
      apiClient.get<PromoOpportunity[]>('/api/v1/discovery/opportunities', {
        params: { month, geo },
      })
    ),
}

// Scenarios API
export const scenariosApi = {
  create: (brief: string, parameters?: Record<string, unknown>) =>
    unwrap(apiClient.post<PromoScenario>('/api/v1/scenarios/create', { brief, parameters })),

  get: (scenarioId: string) =>
    unwrap(apiClient.get<PromoScenario>(`/api/v1/scenarios/${scenarioId}`)),

  update: (scenarioId: string, payload: PromoScenario) =>
    unwrap(apiClient.put<PromoScenario>(`/api/v1/scenarios/${scenarioId}`, payload)),

  remove: (scenarioId: string) =>
    unwrap(apiClient.delete<{ deleted: boolean; scenario_id: string }>(`/api/v1/scenarios/${scenarioId}`)),

  evaluate: (scenario: PromoScenario) =>
    unwrap(apiClient.post<ScenarioKPI>('/api/v1/scenarios/evaluate', scenario)),

  compare: (scenarios: PromoScenario[]) =>
    unwrap(apiClient.post<ScenarioKPI[]>('/api/v1/scenarios/compare', scenarios)),

  validate: (scenario: PromoScenario, kpi?: ScenarioKPI) =>
    unwrap(apiClient.post<ValidationReport>('/api/v1/scenarios/validate', { scenario, kpi })),
}

// Optimization API
export const optimizationApi = {
  optimize: (brief: string, constraints?: Record<string, unknown>) =>
    unwrap(apiClient.post<PromoScenario[]>('/api/v1/optimization/optimize', { brief, constraints })),

  frontier: (scenarios: PromoScenario[]) =>
    unwrap(apiClient.post<FrontierData>('/api/v1/optimization/frontier', scenarios)),

  rank: (scenarios: PromoScenario[], weights?: Record<string, number>) =>
    unwrap(
      apiClient.post<{ ranked_scenarios: RankedScenarioTuple[]; rationale: Record<string, string> }>(
        '/api/v1/optimization/rank',
        { scenarios, weights }
      )
    ),
}

// Creative API
export const creativeApi = {
  finalize: (scenarios: PromoScenario[]) =>
    unwrap(apiClient.post('/api/v1/creative/finalize', scenarios)),

  brief: (scenario: PromoScenario, segments?: string[]) =>
    unwrap(apiClient.post<CreativeBrief>('/api/v1/creative/brief', { scenario, segments })),

  assets: (brief: CreativeBrief) =>
    unwrap(apiClient.post<AssetSpec[]>('/api/v1/creative/assets', brief)),
}

// Data API
export const dataApi = {
  processXlsb: (files: File[]) => {
    const formData = new FormData()
    files.forEach((file) => formData.append('files', file))
    return unwrap(
      apiClient.post<DataProcessResult>('/api/v1/data/process-xlsb', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
    )
  },

  quality: () => unwrap(apiClient.get<QualityReport>('/api/v1/data/quality')),
}

// Chat API
export const chatApi = {
  message: (payload: ChatMessageRequest) =>
    unwrap(apiClient.post<ChatMessageResponse>('/api/v1/chat/message', payload)),
}

// Post-mortem API
export const postmortemApi = {
  analyze: (scenario_id: string, actual_data: Record<string, number>, period: { start: string; end: string }) =>
    unwrap(
      apiClient.post<PostMortemReport>('/api/v1/postmortem/analyze', {
        scenario_id,
        actual_data,
        period,
      })
    ),
}
