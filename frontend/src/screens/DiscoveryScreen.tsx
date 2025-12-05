import { useMemo } from 'react'
import { useDiscoveryAnalyze, useDiscoveryContext } from '../hooks/useDiscovery'
import { useFiltersStore } from '../store/useFiltersStore'
import { notifyError } from '../lib/toast'
import { useQueryClient } from '@tanstack/react-query'
import { formatNumber } from '../utils/format'
import { EmptyState, ErrorState, LoadingState } from '../components/Status'
import GapVsTargetChart from '../components/charts/GapVsTargetChart'
import DepartmentHeatmap from '../components/charts/DepartmentHeatmap'
import ContextWidget from '../components/ContextWidget'
import OpportunitiesList from '../components/OpportunitiesList'

export default function DiscoveryScreen() {
  const { month, geo, setMonth, setGeo } = useFiltersStore()
  const qc = useQueryClient()

  const { data: analyze, isLoading: analyzeLoading, error: analyzeError } = useDiscoveryAnalyze({ month, geo })

  const periodStart = analyze?.baseline_forecast?.period.start
  const periodEnd = analyze?.baseline_forecast?.period.end

  const { data: context, error: contextError } = useDiscoveryContext(
    geo,
    periodStart ?? '',
    periodEnd ?? '',
    Boolean(periodStart && periodEnd)
  )

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
            type="month"
            value={month}
            onChange={(e) => setMonth(e.target.value)}
            className="border border-gray-300 rounded-md px-3 py-2"
            placeholder="YYYY-MM"
            pattern="\d{4}-\d{2}"
            required
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
        {analyzeLoading ? (
          <LoadingState />
        ) : analyzeError ? (
          <ErrorState message="Failed to load gap data" />
        ) : (
          <GapVsTargetChart data={gapChartData} />
        )}
        {analyze?.gap_analysis && (
          <div className="mt-4 grid grid-cols-2 gap-3 text-sm text-gray-700">
            <div className="bg-gray-50 rounded px-3 py-2">
              <div className="font-semibold">Sales gap</div>
              <div>{formatNumber(analyze.gap_analysis.sales_gap)}</div>
            </div>
            <div className="bg-gray-50 rounded px-3 py-2">
              <div className="font-semibold">Margin gap</div>
              <div>{formatNumber(analyze.gap_analysis.margin_gap)}</div>
            </div>
          </div>
        )}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold mb-4">Department Heatmap</h3>
          <DepartmentHeatmap data={deptHeatmapData} />
        </div>
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold mb-4">Context</h3>
          {contextError ? <ErrorState message="Failed to load context" /> : <ContextWidget context={context} />}
        </div>
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold mb-4">Opportunities</h3>
          {analyzeLoading ? (
            <LoadingState />
          ) : analyzeError ? (
            <ErrorState message="Failed to load opportunities" />
          ) : (
            <OpportunitiesList opportunities={analyze?.opportunities} />
          )}
          <div className="mt-3">
            <button
              className="text-xs text-blue-600 underline"
              onClick={() => {
                qc.invalidateQueries({ queryKey: ['discovery', 'analyze'] })
              }}
            >
              Refresh
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
