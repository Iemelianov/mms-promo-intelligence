import { useMemo } from 'react'
import { useDiscoveryAnalyze, useDiscoveryContext } from '../hooks/useDiscovery'
import { useFiltersStore } from '../store/useFiltersStore'
import GapVsTargetChart from '../components/charts/GapVsTargetChart'
import DepartmentHeatmap from '../components/charts/DepartmentHeatmap'
import ContextWidget from '../components/ContextWidget'
import OpportunitiesList from '../components/OpportunitiesList'

export default function DiscoveryScreen() {
  const { month, geo, setMonth, setGeo } = useFiltersStore()

  const { data: analyze, isLoading: analyzeLoading } = useDiscoveryAnalyze({ month, geo })

  const periodStart = analyze?.baseline_forecast?.period.start
  const periodEnd = analyze?.baseline_forecast?.period.end

  const { data: context } = useDiscoveryContext(geo, periodStart ?? '', periodEnd ?? '', Boolean(periodStart && periodEnd))

  const gapChartData = useMemo(() => {
    if (!analyze?.baseline_forecast || !analyze.gap_analysis) return []
    const actual = analyze.baseline_forecast.totals.sales_value
    const target = actual + analyze.gap_analysis.sales_gap
    return [{ date: analyze.baseline_forecast.period.start, actual, target }]
  }, [analyze])

  const deptHeatmapData = useMemo(() => {
    if (!analyze?.opportunities) return []
    return analyze.opportunities.map((opp) => ({
      name: opp.department,
      gap_pct: 0,
      sales_value: opp.estimated_potential,
    }))
  }, [analyze])

  return (
    <div className="px-4 py-6 space-y-6">
      <div className="flex flex-wrap gap-4 items-end">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Month</label>
          <input
            type="text"
            value={month}
            onChange={(e) => setMonth(e.target.value)}
            className="border border-gray-300 rounded-md px-3 py-2"
            placeholder="YYYY-MM"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Geography</label>
          <input
            type="text"
            value={geo}
            onChange={(e) => setGeo(e.target.value)}
            className="border border-gray-300 rounded-md px-3 py-2"
          />
        </div>
      </div>

      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold mb-4">Gap vs Target</h3>
        {analyzeLoading ? <div>Loading...</div> : <GapVsTargetChart data={gapChartData} />}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold mb-4">Department Heatmap</h3>
          <DepartmentHeatmap data={deptHeatmapData} />
        </div>
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold mb-4">Context</h3>
          <ContextWidget context={context} />
        </div>
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold mb-4">Opportunities</h3>
          {analyzeLoading ? <div>Loading...</div> : <OpportunitiesList opportunities={analyze?.opportunities} />}
        </div>
      </div>
    </div>
  )
}
