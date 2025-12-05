import { useEffect, useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import ScenarioComparisonTable from '../components/ScenarioComparisonTable'
import KPIBreakdown from '../components/KPIBreakdown'
import { optimizationApi } from '../services/api'

export default function ScenarioLabScreen() {
  const [scenarios, setScenarios] = useState<any[]>([])
  const [selected, setSelected] = useState<any>(null)

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
    </div>
  )
}
