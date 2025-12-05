import { useMemo, useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { dataApi, discoveryApi } from '../services/api'
import GapVsTargetChart from '../components/charts/GapVsTargetChart'
import DepartmentHeatmap from '../components/charts/DepartmentHeatmap'
import ContextWidget from '../components/ContextWidget'
import OpportunitiesList from '../components/OpportunitiesList'

export default function DiscoveryScreen() {
  const [month, setMonth] = useState('2024-10')
  const [geo, setGeo] = useState('DE')

  const monthRange = useMemo(() => {
    const [year, monthStr] = month.split('-').map(Number)
    const end = new Date(year, monthStr, 0).getDate()
    const startDate = `${month}-01`
    const endDate = `${month}-${String(end).padStart(2, '0')}`
    return { startDate, endDate }
  }, [month])

  const { data: opportunities, isLoading: opportunitiesLoading } = useQuery({
    queryKey: ['opportunities', month, geo],
    queryFn: () => discoveryApi.getOpportunities(month, geo).then(res => res.data),
    enabled: !!month && !!geo,
  })
  
  const { data: gaps, isLoading: gapsLoading } = useQuery({
    queryKey: ['gaps', month, geo],
    queryFn: () => discoveryApi.getGaps(month, geo).then(res => res.data),
    enabled: !!month && !!geo,
  })

  const { data: baseline } = useQuery({
    queryKey: ['baseline', month, geo],
    queryFn: () => dataApi.getBaseline(monthRange.startDate, monthRange.endDate).then(res => res.data),
    enabled: !!monthRange.startDate,
  })

  const { data: contextData } = useQuery({
    queryKey: ['context', geo, month],
    queryFn: () => discoveryApi.getContext(geo, monthRange.startDate, monthRange.endDate).then(res => res.data?.context ?? res.data),
    enabled: !!geo && !!monthRange.startDate,
  })

  const gapChartData = useMemo(() => {
    if (!baseline?.daily_projections) return []
    const entries = Object.entries(baseline.daily_projections)
    const totalDays = entries.length || 1
    const targetTotal = baseline.total_sales - (gaps?.sales_gap ?? 0)
    const targetPerDay = targetTotal / totalDays
    return entries.map(([date, vals]) => ({
      date,
      actual: vals.sales,
      target: targetPerDay,
    }))
  }, [baseline, gaps])

  const deptHeatmapData = useMemo(() => {
    if (!opportunities || !baseline?.total_sales) return []
    return opportunities.map((opp: any) => ({
      name: opp.department,
      gap_pct: (opp.estimated_potential / baseline.total_sales) * 100,
      sales_value: opp.estimated_potential,
    }))
  }, [opportunities, baseline])

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
        {gapsLoading ? <div>Loading...</div> : <GapVsTargetChart data={gapChartData} />}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold mb-4">Department Heatmap</h3>
          <DepartmentHeatmap data={deptHeatmapData} />
        </div>
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold mb-4">Context</h3>
          <ContextWidget context={contextData} />
        </div>
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold mb-4">Opportunities</h3>
          {opportunitiesLoading ? <div>Loading...</div> : <OpportunitiesList opportunities={opportunities} />}
        </div>
      </div>
    </div>
  )
}
