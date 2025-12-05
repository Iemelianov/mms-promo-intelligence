import { useQuery } from '@tanstack/react-query'
import ObjectivesForm from '../components/ObjectivesForm'
import EfficientFrontierChart from '../components/EfficientFrontierChart'
import { optimizationApi } from '../services/api'

export default function OptimizationScreen() {
  const { data, isLoading } = useQuery({
    queryKey: ['frontier'],
    queryFn: () => optimizationApi.frontier({ brief_id: 'demo-brief', x_axis: 'sales', y_axis: 'margin' }).then(res => res.data),
  })

  const scenarios = (data?.frontier?.points || []).map((p: any) => ({
    id: p.scenario_id,
    label: p.scenario_id,
    sales: p.sales,
    margin: p.margin,
    ebit: p.ebit,
  }))

  return (
    <div className="px-4 py-6 space-y-6">
      <h2 className="text-2xl font-bold text-gray-900 mb-4">Optimization</h2>
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <ObjectivesForm onSubmit={() => undefined} />
        </div>
        <div className="bg-white rounded-lg shadow p-6 lg:col-span-2">
          {isLoading ? <div className="text-sm text-gray-500">Loading frontier...</div> : <EfficientFrontierChart scenarios={scenarios} />}
        </div>
      </div>
    </div>
  )
}
