import { useMemo, useState } from 'react'
import ScenarioComparisonTable from '../components/ScenarioComparisonTable'
import KPIBreakdown from '../components/KPIBreakdown'
import { useCompareScenarios, useCreateScenario, useEvaluateScenario, useValidateScenario } from '../hooks/useScenarios'
import { PromoScenario, ScenarioKPI } from '../types'
import { useScenarioStore } from '../store/useScenarioStore'
import { useScenarioSelectionStore } from '../store/useScenarioSelectionStore'
import { notifyError, notifySuccess } from '../lib/toast'

export default function ScenarioLabScreen() {
  const [brief, setBrief] = useState('Promo for TVs & Gaming 22-27 Oct')
  const [selectedId, setSelectedId] = useState<string>()
  const [validationMsg, setValidationMsg] = useState<string>()

  const createScenario = useCreateScenario()
  const evaluateScenario = useEvaluateScenario()
  const compareScenarios = useCompareScenarios()
  const validateScenario = useValidateScenario()
  const { items, upsert, setKpi, byId } = useScenarioStore()
  const { selectedScenarioIds, addScenarioId, setSelectedScenarioIds } = useScenarioSelectionStore()

  const selected = useMemo(
    () => byId(selectedId || selectedScenarioIds[0] || (items[0]?.scenario.id ?? '')) ?? items[0],
    [byId, items, selectedId, selectedScenarioIds]
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
      upsert(entry)
      addScenarioId(scenario.id!)
      setSelectedId(scenario.id)
      setKpi(scenario.id!, kpi)
      notifySuccess('Scenario generated and evaluated')
    } catch (e) {
      console.error('Failed to create/evaluate scenario', e)
      notifyError('Failed to create/evaluate scenario')
    }
  }

  const handleCompare = async () => {
    const scenarios = items.filter((i) => selectedScenarioIds.includes(i.scenario.id!)).map((i) => i.scenario)
    if (!scenarios.length) return
    try {
      const comparison = await compareScenarios.mutateAsync(scenarios)
      // Map returned KPIs to store
      comparison.forEach((kpi) => {
        setKpi(kpi.scenario_id, kpi)
      })
      notifySuccess('Compared scenarios')
    } catch (e) {
      console.error('Failed to compare scenarios', e)
      notifyError('Failed to compare scenarios')
    }
  }

  const handleValidate = async () => {
    if (!selected?.scenario) return
    try {
      const validation = await validateScenario.mutateAsync({ scenario: selected.scenario, kpi: selected.kpi })
      setValidationMsg(
        validation.is_valid
          ? 'Validation passed'
          : `Issues: ${validation.issues.join(', ') || 'Unknown issues'}`
      )
      notifySuccess(validation.is_valid ? 'Validation passed' : 'Validation returned issues')
    } catch (e) {
      console.error('Failed to validate scenario', e)
      setValidationMsg('Validation failed')
      notifyError('Validation failed')
    }
  }

  const handleSelect = (id: string) => {
    setSelectedId(id)
    addScenarioId(id)
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
        <div className="flex gap-2">
          <button
            onClick={handleCompare}
            className="bg-slate-100 text-gray-800 px-3 py-2 rounded border"
            disabled={compareScenarios.isPending || items.length === 0}
          >
            {compareScenarios.isPending ? 'Comparing...' : 'Compare Selected'}
          </button>
          <button
            onClick={handleValidate}
            className="bg-slate-100 text-gray-800 px-3 py-2 rounded border"
            disabled={validateScenario.isPending || !selected?.scenario}
          >
            {validateScenario.isPending ? 'Validating...' : 'Validate'}
          </button>
          <button
            onClick={() => setSelectedScenarioIds([])}
            className="bg-slate-50 text-gray-600 px-3 py-2 rounded border"
          >
            Clear Selection
          </button>
        </div>
      </div>
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="bg-white rounded-lg shadow p-6 lg:col-span-2">
          <ScenarioComparisonTable
            scenarios={items.map((s) => ({ id: s.scenario.id!, name: s.scenario.name, kpi: s.kpi }))}
            onSelect={handleSelect}
          />
        </div>
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="font-semibold mb-2">Selected Scenario</h3>
          {selected ? (
            <KPIBreakdown kpi={selected.kpi} />
          ) : (
            <div className="text-gray-500 text-sm">Select a scenario</div>
          )}
          {validationMsg && <div className="mt-3 text-xs text-gray-700 bg-gray-50 border rounded px-3 py-2">{validationMsg}</div>}
        </div>
      </div>
    </div>
  )
}
