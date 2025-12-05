import { useMemo, useState } from 'react'
import ScenarioComparisonTable from '../components/ScenarioComparisonTable'
import KPIBreakdown from '../components/KPIBreakdown'
import { useCreateScenario, useEvaluateScenario } from '../hooks/useScenarios'
import { PromoScenario, ScenarioKPI } from '../types'

export default function ScenarioLabScreen() {
  const [brief, setBrief] = useState('Promo for TVs & Gaming 22-27 Oct')
  const [scenarios, setScenarios] = useState<Array<{ scenario: PromoScenario; kpi?: ScenarioKPI }>>([])
  const [selectedId, setSelectedId] = useState<string>()

  const createScenario = useCreateScenario()
  const evaluateScenario = useEvaluateScenario()

  const selected = useMemo(
    () => scenarios.find((s) => s.scenario.id === selectedId) ?? scenarios[0],
    [scenarios, selectedId]
  )

  const handleCreate = async () => {
    try {
      const scenario = await createScenario.mutateAsync({
        brief,
        parameters: {
          name: 'Generated Scenario',
          date_range: { start_date: '2024-10-22', end_date: '2024-10-27' },
          departments: ['TV', 'Gaming'],
          channels: ['online', 'offline'],
          discount_percentage: 15,
        },
      })
      const kpi = await evaluateScenario.mutateAsync(scenario)
      const entry = { scenario, kpi }
      setScenarios((prev) => [...prev, entry])
      setSelectedId(scenario.id)
    } catch (e) {
      console.error('Failed to create/evaluate scenario', e)
    }
  }

  return (
    <div className="px-4 py-6">
      <h2 className="text-2xl font-bold text-gray-900 mb-4">Scenario Lab</h2>
      <div className="mb-4 flex flex-col gap-2">
        <label className="text-sm font-medium text-gray-700">Brief</label>
        <textarea
          value={brief}
          onChange={(e) => setBrief(e.target.value)}
          className="border border-gray-300 rounded-md px-3 py-2 w-full"
          rows={2}
        />
        <button
          onClick={handleCreate}
          className="self-start bg-blue-600 text-white px-4 py-2 rounded-md disabled:opacity-60"
          disabled={createScenario.isPending || evaluateScenario.isPending}
        >
          {createScenario.isPending || evaluateScenario.isPending ? 'Generating...' : 'Generate Scenario'}
        </button>
      </div>
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="bg-white rounded-lg shadow p-6 lg:col-span-2">
          <ScenarioComparisonTable
            scenarios={scenarios.map((s) => ({ id: s.scenario.id!, name: s.scenario.name, kpi: s.kpi }))}
            onSelect={(id) => setSelectedId(id)}
          />
        </div>
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="font-semibold mb-2">Selected Scenario</h3>
          {selected ? (
            <KPIBreakdown kpi={selected.kpi} />
          ) : (
            <div className="text-gray-500 text-sm">Select a scenario</div>
          )}
        </div>
      </div>
    </div>
  )
}
