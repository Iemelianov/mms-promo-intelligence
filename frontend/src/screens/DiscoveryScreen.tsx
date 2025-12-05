import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { discoveryApi } from '../services/api'
import GapVsTargetChart from '../components/charts/GapVsTargetChart'
import DepartmentHeatmap from '../components/charts/DepartmentHeatmap'
import ContextWidget from '../components/ContextWidget'
import OpportunitiesList from '../components/OpportunitiesList'

export default function DiscoveryScreen() {
  const [month, setMonth] = useState('2024-10')
  const [geo, setGeo] = useState('DE')
  
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

  const gapChartData = [
    { date: '2024-10-01', actual: 200000, target: 220000 },
    { date: '2024-10-02', actual: 210000, target: 220000 },
  ]
  const deptHeatmapData = [
    { name: 'TV', gap_pct: -8, sales_value: 500000 },
    { name: 'Gaming', gap_pct: 5, sales_value: 300000 },
  ]

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
        <GapVsTargetChart data={gapChartData} />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold mb-4">Department Heatmap</h3>
          <DepartmentHeatmap data={deptHeatmapData} />
        </div>
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold mb-4">Context</h3>
          <ContextWidget />
        </div>
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold mb-4">Opportunities</h3>
          {opportunitiesLoading ? <div>Loading...</div> : <OpportunitiesList opportunities={opportunities} />}
        </div>
      </div>
    </div>
  )
}
