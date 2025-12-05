import { useQuery } from '@tanstack/react-query'
import CreativeBriefView from '../components/CreativeBriefView'
import AssetCard from '../components/AssetCard'
import { creativeApi } from '../services/api'

export default function CreativeScreen() {
  const { data, isLoading } = useQuery({
    queryKey: ['creative-demo'],
    queryFn: () => creativeApi.generate({ scenario_ids: ['demo_scenario'], asset_types: ['homepage_hero', 'category_banner'] }).then(res => res.data),
  })

  const firstBrief = data?.briefs?.[0]
  const brief = firstBrief?.creative_brief
  const assets = firstBrief?.assets || []

  return (
    <div className="px-4 py-6 space-y-6">
      <h2 className="text-2xl font-bold text-gray-900 mb-4">Creative Companion</h2>
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="bg-white rounded-lg shadow p-6 lg:col-span-2">
          {isLoading && <div className="text-sm text-gray-500">Generating brief...</div>}
          {brief && <CreativeBriefView brief={brief as any} />}
        </div>
        <div className="space-y-3">
          {assets.map((asset: any, idx: number) => (
            <AssetCard key={idx} asset={asset as any} />
          ))}
        </div>
      </div>
    </div>
  )
}
