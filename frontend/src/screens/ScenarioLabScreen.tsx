import { useEffect, useMemo, useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import ScenarioComparisonTable from '../components/ScenarioComparisonTable'
import KPIBreakdown from '../components/KPIBreakdown'
import { optimizationApi, scenariosApi } from '../services/api'

export default function ScenarioLabScreen() {
  const [scenarios, setScenarios] = useState<any[]>([])
  const [selected, setSelected] = useState<any>(null)
  const [form, setForm] = useState({
    month: '2024-10',
    start: '2024-10-22',
    end: '2024-10-27',
    departments: 'TV,GAMING',
    channels: 'online,store',
    discount_pct: 15,
    name: 'Custom Scenario',
    description: 'User defined scenario',
  })
  const queryClient = useQueryClient()

  const { data, isLoading } = useQuery({
    queryKey: ['optimized-scenarios'],
    queryFn: () => optimizationApi.optimize('Find 3 promo scenarios for October electronics').then(res => res.data),
  })

  useEffect(() => {
    if (data?.scenarios) {
      const mapped = data.scenarios.map((item: any) => ({
        id: item.scenario.id,
        name: item.scenario.name,
        kpi: item.kpi,
      }))
      setScenarios(mapped)
      setSelected(mapped[0])
    }
  }, [data])

  const createMutation = useMutation({
    mutationFn: (payload: any) => scenariosApi.create(payload),
    onSuccess: (res) => {
      const created = res.data?.scenario
      if (!created) return
      const mapped = {
        id: created.id,
        name: created.name || created.label,
        kpi: res.data?.kpi,
      }
      setScenarios((prev) => [mapped, ...prev])
      setSelected(mapped)
      queryClient.invalidateQueries({ queryKey: ['optimized-scenarios'] })
    },
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    createMutation.mutate({
      brief: {
        month: form.month,
        promo_date_range: { start: form.start, end: form.end },
        focus_departments: form.departments.split(',').map((d) => d.trim()).filter(Boolean),
      },
      parameters: {
        name: form.name,
        description: form.description,
        discount_pct: Number(form.discount_pct),
        departments: form.departments.split(',').map((d) => d.trim()).filter(Boolean),
        channels: form.channels.split(',').map((d) => d.trim()).filter(Boolean),
      },
    })
  }
  
  return (
    <div className="px-4 py-6">
      <h2 className="text-2xl font-bold text-gray-900 mb-4">Scenario Lab</h2>
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="bg-white rounded-lg shadow p-6 lg:col-span-2">
          {isLoading && <div className="text-sm text-gray-500">Loading scenarios...</div>}
          {!isLoading && scenarios.length > 0 && (
            <ScenarioComparisonTable scenarios={scenarios} onSelect={(id) => setSelected(scenarios.find(s => s.id === id))} />
          )}
        </div>
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="font-semibold mb-2">Selected Scenario</h3>
          {selected ? <KPIBreakdown kpi={selected.kpi} /> : <div className="text-gray-500 text-sm">Select a scenario</div>}
        </div>
      </div>

      <div className="bg-white rounded-lg shadow p-6 mt-6">
        <h3 className="font-semibold mb-3">Create Scenario</h3>
        <form className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm" onSubmit={handleSubmit}>
          <label className="space-y-1">
            <span className="font-medium">Month</span>
            <input className="border rounded px-2 py-1 w-full" value={form.month} onChange={(e) => setForm({ ...form, month: e.target.value })} />
          </label>
          <label className="space-y-1">
            <span className="font-medium">Discount %</span>
            <input
              className="border rounded px-2 py-1 w-full"
              type="number"
              value={form.discount_pct}
              onChange={(e) => setForm({ ...form, discount_pct: Number(e.target.value) })}
            />
          </label>
          <label className="space-y-1">
            <span className="font-medium">Start</span>
            <input className="border rounded px-2 py-1 w-full" type="date" value={form.start} onChange={(e) => setForm({ ...form, start: e.target.value })} />
          </label>
          <label className="space-y-1">
            <span className="font-medium">End</span>
            <input className="border rounded px-2 py-1 w-full" type="date" value={form.end} onChange={(e) => setForm({ ...form, end: e.target.value })} />
          </label>
          <label className="space-y-1">
            <span className="font-medium">Departments (comma)</span>
            <input className="border rounded px-2 py-1 w-full" value={form.departments} onChange={(e) => setForm({ ...form, departments: e.target.value })} />
          </label>
          <label className="space-y-1">
            <span className="font-medium">Channels (comma)</span>
            <input className="border rounded px-2 py-1 w-full" value={form.channels} onChange={(e) => setForm({ ...form, channels: e.target.value })} />
          </label>
          <label className="space-y-1 md:col-span-2">
            <span className="font-medium">Name</span>
            <input className="border rounded px-2 py-1 w-full" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} />
          </label>
          <label className="space-y-1 md:col-span-2">
            <span className="font-medium">Description</span>
            <textarea className="border rounded px-2 py-1 w-full" value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} />
          </label>
          <div className="md:col-span-2 flex gap-2 items-center">
            <button
              type="submit"
              className="bg-blue-600 text-white px-4 py-2 rounded disabled:opacity-50"
              disabled={createMutation.isLoading}
            >
              {createMutation.isLoading ? 'Creating...' : 'Create Scenario'}
            </button>
            {createMutation.isError && (
              <span className="text-red-600 text-xs">Failed: {(createMutation.error as any)?.message || 'Error'}</span>
            )}
            {createMutation.isSuccess && <span className="text-green-600 text-xs">Created</span>}
          </div>
        </form>
      </div>
    </div>
  )
}
