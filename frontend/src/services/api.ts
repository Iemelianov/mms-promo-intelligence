import axios from 'axios'

const API_URL = (import.meta as any).env?.VITE_API_URL || 'http://localhost:8000'

const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

export default apiClient

// Discovery API
export const discoveryApi = {
  getOpportunities: (month: string, geo: string) =>
    apiClient.get(`/api/v1/discovery/opportunities`, { params: { month, geo } }),
  getContext: (geo: string, startDate: string, endDate: string) =>
    apiClient.get(`/api/v1/discovery/context`, { params: { geo, start_date: startDate, end_date: endDate } }),
  getGaps: (month: string, geo: string) =>
    apiClient.get(`/api/v1/discovery/gaps`, { params: { month, geo } }),
}

// Scenarios API
export const scenariosApi = {
  create: (payload: any, parameters?: any) => {
    if (typeof payload === 'string') {
      return apiClient.post(`/api/v1/scenarios/create`, { brief: payload, parameters })
    }
    return apiClient.post(`/api/v1/scenarios/create`, payload)
  },
  evaluate: (scenario: any) =>
    apiClient.post(`/api/v1/scenarios/evaluate`, scenario),
  compare: (scenarios: any[], scenarioIds?: string[]) =>
    apiClient.post(`/api/v1/scenarios/compare`, { scenarios, scenario_ids: scenarioIds }),
  validate: (scenario: any, kpi?: any) =>
    apiClient.post(`/api/v1/scenarios/validate`, { scenario, kpi }),
}

// Optimization API
export const optimizationApi = {
  optimize: (brief: string, constraints?: any) =>
    apiClient.post(`/api/v1/optimization/generate`, { brief, constraints }),
  frontier: (params?: any) =>
    apiClient.get(`/api/v1/optimization/frontier`, { params }),
  rank: (scenarios: any[], weights?: any) =>
    apiClient.post(`/api/v1/optimization/rank`, { scenarios, weights }),
}

// Creative API
export const creativeApi = {
  generate: (payload: any) =>
    apiClient.post(`/api/v1/creative/generate`, payload),
  finalize: (scenarios: any[]) =>
    apiClient.post(`/api/v1/creative/finalize`, scenarios),
  brief: (scenario: any, segments?: string[]) =>
    apiClient.post(`/api/v1/creative/brief`, { scenario, segments }),
  assets: (brief: any) =>
    apiClient.post(`/api/v1/creative/assets`, brief),
}

// Chat API
export const chatApi = {
  message: (message: string, context?: any) =>
    apiClient.post(`/api/v1/chat/message`, { message, context }),
  stream: (message: string, context?: any) =>
    fetch(`${API_URL}/api/v1/chat/stream`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ message, context }),
    }),
}

// Data API
export const dataApi = {
  processXlsb: (files: File[]) => {
    const formData = new FormData()
    files.forEach(file => formData.append('files', file))
    return apiClient.post(`/api/v1/data/process-xlsb`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },
  getQuality: (datasetId: string) =>
    apiClient.get(`/api/v1/data/quality`, { params: { dataset_id: datasetId } }),
  getBaseline: (startDate: string, endDate: string) =>
    apiClient.get(`/api/v1/data/baseline`, { params: { start_date: startDate, end_date: endDate } }),
  getSegments: () => apiClient.get(`/api/v1/data/segments`),
  getUpliftModel: (department?: string, channel?: string) =>
    apiClient.get(`/api/v1/data/uplift-model`, { params: { department, channel } }),
}
