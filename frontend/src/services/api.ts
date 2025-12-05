import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

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
  create: (brief: string, parameters?: any) =>
    apiClient.post(`/api/v1/scenarios/create`, { brief, parameters }),
  evaluate: (scenario: any) =>
    apiClient.post(`/api/v1/scenarios/evaluate`, scenario),
  compare: (scenarios: any[]) =>
    apiClient.post(`/api/v1/scenarios/compare`, scenarios),
  validate: (scenario: any, kpi?: any) =>
    apiClient.post(`/api/v1/scenarios/validate`, { scenario, kpi }),
}

// Optimization API
export const optimizationApi = {
  optimize: (brief: string, constraints?: any) =>
    apiClient.post(`/api/v1/optimization/optimize`, { brief, constraints }),
  frontier: (scenarios: any[]) =>
    apiClient.post(`/api/v1/optimization/frontier`, scenarios),
  rank: (scenarios: any[], weights?: any) =>
    apiClient.post(`/api/v1/optimization/rank`, { scenarios, weights }),
}

// Creative API
export const creativeApi = {
  finalize: (scenarios: any[]) =>
    apiClient.post(`/api/v1/creative/finalize`, scenarios),
  brief: (scenario: any, segments?: string[]) =>
    apiClient.post(`/api/v1/creative/brief`, { scenario, segments }),
  assets: (brief: any) =>
    apiClient.post(`/api/v1/creative/assets`, brief),
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
}
