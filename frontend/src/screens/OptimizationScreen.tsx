import ObjectivesForm from '../components/ObjectivesForm'
import EfficientFrontierChart from '../components/EfficientFrontierChart'

export default function OptimizationScreen() {
  const scenarios = [
    { id: 'A', label: 'A', sales: 3, margin: 1.2, ebit: 0.8 },
    { id: 'B', label: 'B', sales: 2.2, margin: 1.4, ebit: 0.9 },
  ]
  return (
    <div className="px-4 py-6 space-y-6">
      <h2 className="text-2xl font-bold text-gray-900 mb-4">Optimization</h2>
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <ObjectivesForm onSubmit={() => undefined} />
        </div>
        <div className="bg-white rounded-lg shadow p-6 lg:col-span-2">
          <EfficientFrontierChart scenarios={scenarios} />
        </div>
      </div>
    </div>
  )
}
