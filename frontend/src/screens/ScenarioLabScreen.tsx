import { useState } from 'react'
import ScenarioComparisonTable from '../components/ScenarioComparisonTable'
import KPIBreakdown from '../components/KPIBreakdown'

export default function ScenarioLabScreen() {
  const [scenarios, setScenarios] = useState<any[]>([
    { id: 'A', name: 'Conservative', kpi: { total_sales: 1, total_margin: 1, total_ebit: 1, total_units: 1 } },
    { id: 'B', name: 'Balanced', kpi: { total_sales: 2, total_margin: 1.5, total_ebit: 1.4, total_units: 2 } },
  ])
  const [selected, setSelected] = useState<any>(scenarios[0])
  
  return (
    <div className="px-4 py-6">
      <h2 className="text-2xl font-bold text-gray-900 mb-4">Scenario Lab</h2>
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="bg-white rounded-lg shadow p-6 lg:col-span-2">
          <ScenarioComparisonTable scenarios={scenarios} onSelect={(id) => setSelected(scenarios.find(s => s.id === id))} />
        </div>
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="font-semibold mb-2">Selected Scenario</h3>
          {selected ? <KPIBreakdown kpi={selected.kpi} /> : <div className="text-gray-500 text-sm">Select a scenario</div>}
        </div>
      </div>
    </div>
  )
}
