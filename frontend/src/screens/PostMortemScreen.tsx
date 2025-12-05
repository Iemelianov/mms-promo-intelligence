import { useState } from 'react'
import { usePostmortemAnalyze } from '../hooks/usePostmortem'
import { useScenarioSelectionStore } from '../store/useScenarioSelectionStore'
import { useScenarioStore } from '../store/useScenarioStore'
import { notifyError, notifySuccess } from '../lib/toast'
import { formatNumber, formatPercent, formatCurrency, formatDate } from '../utils/format'
import { EmptyState, LoadingState } from '../components/Status'

export default function PostMortemScreen() {
  const { selectedScenarioIds } = useScenarioSelectionStore()
  const { byId } = useScenarioStore()
  const primaryScenario = selectedScenarioIds.map(byId).find(Boolean)
  const analyze = usePostmortemAnalyze()
  const [actualSales, setActualSales] = useState<number>(0)
  const [actualMargin, setActualMargin] = useState<number>(0)
  const [actualUnits, setActualUnits] = useState<number>(0)

  const handleAnalyze = async () => {
    if (!primaryScenario?.scenario) return
    try {
      await analyze.mutateAsync({
        scenario_id: primaryScenario.scenario.id!,
        actual_data: {
          sales_value: actualSales,
          margin_value: actualMargin,
          units: actualUnits,
        },
        period: {
          start: primaryScenario.scenario.date_range.start_date,
          end: primaryScenario.scenario.date_range.end_date,
        },
      })
      notifySuccess('Post-mortem generated')
    } catch (e) {
      console.error(e)
      notifyError('Post-mortem failed')
    }
  }

  const report = analyze.data

  return (
    <div className="px-4 py-6 space-y-6">
      <h2 className="text-2xl font-bold text-gray-900 mb-4">Post-Mortem</h2>
      <div className="bg-white rounded-lg shadow p-4 space-y-3">
        <div className="text-sm text-gray-700">
          Scenario: {primaryScenario?.scenario?.name || 'Select in Scenario Lab'}
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3 text-sm">
          <label className="flex flex-col gap-1">
            <span>Actual Sales</span>
            <input type="number" className="border rounded px-2 py-1" value={actualSales} onChange={(e) => setActualSales(Number(e.target.value))} />
          </label>
          <label className="flex flex-col gap-1">
            <span>Actual Margin</span>
            <input type="number" className="border rounded px-2 py-1" value={actualMargin} onChange={(e) => setActualMargin(Number(e.target.value))} />
          </label>
          <label className="flex flex-col gap-1">
            <span>Actual Units</span>
            <input type="number" className="border rounded px-2 py-1" value={actualUnits} onChange={(e) => setActualUnits(Number(e.target.value))} />
          </label>
        </div>
        <button
          className="bg-blue-600 text-white px-4 py-2 rounded disabled:opacity-60"
          onClick={handleAnalyze}
          disabled={analyze.isPending || !primaryScenario}
        >
          {analyze.isPending ? 'Analyzing...' : 'Run Post-Mortem'}
        </button>
      </div>

      {analyze.isPending && <LoadingState message="Running post-mortem..." />}

      {report && (
        <div className="bg-white rounded-lg shadow p-6 space-y-3 text-sm">
          <div className="font-semibold">Forecast vs Actual</div>
          <div className="text-xs text-gray-600">Period: {formatDate(report.period?.start_date)} - {formatDate(report.period?.end_date)}</div>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <div className="text-gray-600">Forecast Sales</div>
              <div className="font-semibold">{formatCurrency(report.forecast_kpi.total_sales)}</div>
            </div>
            <div>
              <div className="text-gray-600">Actual Sales</div>
              <div className="font-semibold">{formatCurrency((report as any).actual_kpi?.total_sales)}</div>
            </div>
            <div>
              <div className="text-gray-600">Forecast Margin %</div>
              <div className="font-semibold">{formatPercent(report.forecast_kpi.total_margin)}</div>
            </div>
            <div>
              <div className="text-gray-600">Actual Margin %</div>
              <div className="font-semibold">{formatPercent((report as any).actual_kpi?.margin_pct)}</div>
            </div>
          </div>
          <div>
            <div className="text-gray-600">Sales error %</div>
            <div className="font-semibold">{report.vs_forecast.sales_value_error_pct?.toFixed?.(2)}%</div>
          </div>
          <div>
            <div className="text-gray-600">Insights</div>
            <ul className="list-disc list-inside">
              {report.insights.map((i, idx) => (
                <li key={idx}>{i}</li>
              ))}
            </ul>
          </div>
          <div>
            <div className="text-gray-600">Learning points</div>
            <ul className="list-disc list-inside">
              {report.learning_points.map((i, idx) => (
                <li key={idx}>{i}</li>
              ))}
            </ul>
          </div>
        </div>
      )}

      {!report && !analyze.isPending && <EmptyState message="Run post-mortem to see results" />}
    </div>
  )
}
import { useState } from 'react'
import { usePostmortemAnalyze } from '../hooks/usePostmortem'
import { useScenarioSelectionStore } from '../store/useScenarioSelectionStore'
import { useScenarioStore } from '../store/useScenarioStore'
import { notifyError, notifySuccess } from '../lib/toast'
import { formatNumber, formatPercent } from '../utils/format'

export default function PostMortemScreen() {
  const { selectedScenarioIds } = useScenarioSelectionStore()
  const { byId } = useScenarioStore()
  const primaryScenario = selectedScenarioIds.map(byId).find(Boolean)
  const analyze = usePostmortemAnalyze()
  const [actualSales, setActualSales] = useState<number>(0)
  const [actualMargin, setActualMargin] = useState<number>(0)
  const [actualUnits, setActualUnits] = useState<number>(0)

  const handleAnalyze = async () => {
    if (!primaryScenario?.scenario) return
    try {
      await analyze.mutateAsync({
        scenario_id: primaryScenario.scenario.id!,
        actual_data: {
          sales_value: actualSales,
          margin_value: actualMargin,
          units: actualUnits,
        },
        period: {
          start: primaryScenario.scenario.date_range.start_date,
          end: primaryScenario.scenario.date_range.end_date,
        },
      })
      notifySuccess('Post-mortem generated')
    } catch (e) {
      console.error(e)
      notifyError('Post-mortem failed')
    }
  }

  const report = analyze.data

  return (
    <div className="px-4 py-6 space-y-6">
      <h2 className="text-2xl font-bold text-gray-900 mb-4">Post-Mortem</h2>
      <div className="bg-white rounded-lg shadow p-4 space-y-3">
        <div className="text-sm text-gray-700">
          Scenario: {primaryScenario?.scenario?.name || 'Select in Scenario Lab'}
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3 text-sm">
          <label className="flex flex-col gap-1">
            <span>Actual Sales</span>
            <input type="number" className="border rounded px-2 py-1" value={actualSales} onChange={(e) => setActualSales(Number(e.target.value))} />
          </label>
          <label className="flex flex-col gap-1">
            <span>Actual Margin</span>
            <input type="number" className="border rounded px-2 py-1" value={actualMargin} onChange={(e) => setActualMargin(Number(e.target.value))} />
          </label>
          <label className="flex flex-col gap-1">
            <span>Actual Units</span>
            <input type="number" className="border rounded px-2 py-1" value={actualUnits} onChange={(e) => setActualUnits(Number(e.target.value))} />
          </label>
        </div>
        <button
          className="bg-blue-600 text-white px-4 py-2 rounded disabled:opacity-60"
          onClick={handleAnalyze}
          disabled={analyze.isPending || !primaryScenario}
        >
          {analyze.isPending ? 'Analyzing...' : 'Run Post-Mortem'}
        </button>
      </div>

      {report && (
        <div className="bg-white rounded-lg shadow p-6 space-y-3 text-sm">
          <div className="font-semibold">Forecast vs Actual</div>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <div className="text-gray-600">Forecast Sales</div>
              <div className="font-semibold">{formatNumber(report.forecast_kpi.total_sales)}</div>
            </div>
            <div>
              <div className="text-gray-600">Actual Sales</div>
              <div className="font-semibold">{formatNumber((report as any).actual_kpi?.total_sales)}</div>
            </div>
            <div>
              <div className="text-gray-600">Forecast Margin %</div>
              <div className="font-semibold">{formatPercent(report.forecast_kpi.total_margin)}</div>
            </div>
            <div>
              <div className="text-gray-600">Actual Margin %</div>
              <div className="font-semibold">{formatPercent((report as any).actual_kpi?.margin_pct)}</div>
            </div>
          </div>
          <div>
            <div className="text-gray-600">Error %</div>
            <div className="font-semibold">{report.vs_forecast.sales_value_error_pct?.toFixed?.(2)}%</div>
          </div>
          <div>
            <div className="text-gray-600">Insights</div>
            <ul className="list-disc list-inside">
              {report.insights.map((i, idx) => (
                <li key={idx}>{i}</li>
              ))}
            </ul>
          </div>
          <div>
            <div className="text-gray-600">Learning points</div>
            <ul className="list-disc list-inside">
              {report.learning_points.map((i, idx) => (
                <li key={idx}>{i}</li>
              ))}
            </ul>
          </div>
        </div>
      )}
    </div>
  )
}
import { useState } from 'react'
import { usePostmortemAnalyze } from '../hooks/usePostmortem'
import { useScenarioSelectionStore } from '../store/useScenarioSelectionStore'
import { useScenarioStore } from '../store/useScenarioStore'
import { notifyError, notifySuccess } from '../lib/toast'

export default function PostMortemScreen() {
  const { selectedScenarioIds } = useScenarioSelectionStore()
  const { byId } = useScenarioStore()
  const primaryScenario = selectedScenarioIds.map(byId).find(Boolean)
  const analyze = usePostmortemAnalyze()
  const [actualSales, setActualSales] = useState<number>(0)
  const [actualMargin, setActualMargin] = useState<number>(0)
  const [actualUnits, setActualUnits] = useState<number>(0)

  const handleAnalyze = async () => {
    if (!primaryScenario?.scenario) return
    try {
      await analyze.mutateAsync({
        scenario_id: primaryScenario.scenario.id!,
        actual_data: {
          sales_value: actualSales,
          margin_value: actualMargin,
          units: actualUnits,
        },
        period: {
          start: primaryScenario.scenario.date_range.start_date,
          end: primaryScenario.scenario.date_range.end_date,
        },
      })
      notifySuccess('Post-mortem generated')
    } catch (e) {
      console.error(e)
      notifyError('Post-mortem failed')
    }
  }

  const report = analyze.data

  return (
    <div className="px-4 py-6 space-y-6">
      <h2 className="text-2xl font-bold text-gray-900 mb-4">Post-Mortem</h2>
      <div className="bg-white rounded-lg shadow p-4 space-y-3">
        <div className="text-sm text-gray-700">
          Scenario: {primaryScenario?.scenario?.name || 'Select in Scenario Lab'}
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3 text-sm">
          <label className="flex flex-col gap-1">
            <span>Actual Sales</span>
            <input type="number" className="border rounded px-2 py-1" value={actualSales} onChange={(e) => setActualSales(Number(e.target.value))} />
          </label>
          <label className="flex flex-col gap-1">
            <span>Actual Margin</span>
            <input type="number" className="border rounded px-2 py-1" value={actualMargin} onChange={(e) => setActualMargin(Number(e.target.value))} />
          </label>
          <label className="flex flex-col gap-1">
            <span>Actual Units</span>
            <input type="number" className="border rounded px-2 py-1" value={actualUnits} onChange={(e) => setActualUnits(Number(e.target.value))} />
          </label>
        </div>
        <button
          className="bg-blue-600 text-white px-4 py-2 rounded disabled:opacity-60"
          onClick={handleAnalyze}
          disabled={analyze.isPending || !primaryScenario}
        >
          {analyze.isPending ? 'Analyzing...' : 'Run Post-Mortem'}
        </button>
      </div>

      {report && (
        <div className="bg-white rounded-lg shadow p-6 space-y-3 text-sm">
          <div className="font-semibold">Forecast vs Actual</div>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <div className="text-gray-600">Forecast Sales</div>
              <div className="font-semibold">{report.forecast_kpi.total_sales.toLocaleString()}</div>
            </div>
            <div>
              <div className="text-gray-600">Actual Sales</div>
              <div className="font-semibold">{report.actual_kpi.total_sales?.toLocaleString?.() || report.actual_kpi.total_sales}</div>
            </div>
          </div>
          <div>
            <div className="text-gray-600">Error %</div>
            <div className="font-semibold">{report.vs_forecast.sales_value_error_pct?.toFixed?.(2)}%</div>
          </div>
          <div>
            <div className="text-gray-600">Insights</div>
            <ul className="list-disc list-inside">
              {report.insights.map((i, idx) => (
                <li key={idx}>{i}</li>
              ))}
            </ul>
          </div>
          <div>
            <div className="text-gray-600">Learning points</div>
            <ul className="list-disc list-inside">
              {report.learning_points.map((i, idx) => (
                <li key={idx}>{i}</li>
              ))}
            </ul>
          </div>
        </div>
      )}
    </div>
  )
}

