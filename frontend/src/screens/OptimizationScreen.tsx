import { useState } from 'react'
import ObjectivesForm from '../components/ObjectivesForm'
import EfficientFrontierChart from '../components/EfficientFrontierChart'
import { useOptimizeScenarios, useFrontier, useRankScenarios } from '../hooks/useOptimization'
import { useScenarioSelectionStore } from '../store/useScenarioSelectionStore'
import { useScenarioStore } from '../store/useScenarioStore'
import { PromoScenario } from '../types'

export default function OptimizationScreen() {
  const [brief, setBrief] = useState('Optimize October promo')
  const [optimized, setOptimized] = useState<PromoScenario[]>([])
  const [frontierPoints, setFrontierPoints] = useState<{ id: string; label: string; sales: number; margin: number; pareto?: boolean }[]>([])
  const [rankings, setRankings] = useState<Array<{ id: string; score: number; label: string }>>([])

  const optimize = useOptimizeScenarios()
  const frontier = useFrontier()
  const rank = useRankScenarios()

  const { selectedScenarioIds } = useScenarioSelectionStore()
  const { byId } = useScenarioStore()

  const handleOptimize = async (vals: { maximize: string; minMargin: number; maxDiscount: number }) => {
    try {
      const constraints = {
        objectives: { [vals.maximize]: 1 },
        min_margin_pct: vals.minMargin,
        max_discount_pct: vals.maxDiscount,
      }
      const result = await optimize.mutateAsync({ brief, constraints })
      setOptimized(result)
      // frontier calculation based on optimized scenarios
      const frontierData = await frontier.mutateAsync(result)
      setFrontierPoints(
        frontierData.coordinates.map((coord, idx) => ({
          id: result[idx]?.id || `scenario_${idx}`,
          label: result[idx]?.name || `Scenario ${idx + 1}`,
          sales: coord[0],
          margin: coord[1],
          pareto: frontierData.pareto_optimal[idx],
        }))
      )
      const ranked = await rank.mutateAsync({ scenarios: result })
      setRankings(
        ranked.ranked_scenarios.map(([scenario, score]) => ({
          id: scenario.id || '',
          label: scenario.name,
          score,
        }))
      )
    } catch (e) {
      console.error('Failed to optimize', e)
    }
  }

  const handleRankSelected = async () => {
    const scenarios = selectedScenarioIds.map(byId).filter(Boolean).map((s) => s!.scenario)
    if (!scenarios.length) return
    try {
      const ranked = await rank.mutateAsync({ scenarios })
      setRankings(
        ranked.ranked_scenarios.map(([scenario, score]) => ({
          id: scenario.id || '',
          label: scenario.name,
          score,
        }))
      )
    } catch (e) {
      console.error('Failed to rank scenarios', e)
    }
  }

  return (
    <div className="px-4 py-6 space-y-6">
      <h2 className="text-2xl font-bold text-gray-900 mb-4">Optimization</h2>
      <div className="bg-white rounded-lg shadow p-4 flex flex-col gap-3">
        <label className="text-sm font-medium text-gray-700">Brief</label>
        <textarea
          value={brief}
          onChange={(e) => setBrief(e.target.value)}
          className="border rounded px-3 py-2 w-full"
          rows={2}
        />
        <div className="flex gap-2">
          <button
            onClick={() => handleRankSelected()}
            className="bg-slate-100 text-gray-800 px-3 py-2 rounded border"
            disabled={rank.isPending}
          >
            {rank.isPending ? 'Ranking...' : 'Rank selected scenarios'}
          </button>
        </div>
      </div>
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <ObjectivesForm onSubmit={handleOptimize} />
        </div>
        <div className="bg-white rounded-lg shadow p-6 lg:col-span-2 space-y-4">
          <EfficientFrontierChart scenarios={frontierPoints} />
          <div>
            <h3 className="font-semibold mb-2">Rankings</h3>
            {rankings.length ? (
              <ul className="text-sm space-y-1">
                {rankings.map((r, idx) => (
                  <li key={r.id || idx} className="flex justify-between">
                    <span>{r.label || `Scenario ${idx + 1}`}</span>
                    <span className="font-semibold">{r.score.toFixed(2)}</span>
                  </li>
                ))}
              </ul>
            ) : (
              <div className="text-gray-500 text-sm">No rankings yet</div>
            )}
          </div>
        </div>
      </div>
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="font-semibold mb-2">Optimized Scenarios</h3>
        {optimized.length ? (
          <ul className="text-sm space-y-1">
            {optimized.map((s) => (
              <li key={s.id || s.name} className="flex justify-between">
                <span>{s.name}</span>
                <span className="text-gray-600">{s.discount_percentage}% discount</span>
              </li>
            ))}
          </ul>
        ) : (
          <div className="text-gray-500 text-sm">No optimized scenarios yet</div>
        )}
      </div>
    </div>
  )
}
