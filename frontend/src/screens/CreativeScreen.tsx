import CreativeBriefView from '../components/CreativeBriefView'
import AssetCard from '../components/AssetCard'

export default function CreativeScreen() {
  const brief = {
    objectives: ['Close gap', 'Maintain margin'],
    messaging: 'Promo message',
    target_audience: 'General',
    tone: 'confident',
    style: 'benefit-led',
    mandatory_elements: ['Discount: 15%'],
  }
  const assets = [
    { asset_type: 'homepage_hero', copy_text: 'Hero copy' },
    { asset_type: 'banner', copy_text: 'Banner copy' },
  ]
  return (
    <div className="px-4 py-6 space-y-6">
      <h2 className="text-2xl font-bold text-gray-900 mb-4">Creative Companion</h2>
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="bg-white rounded-lg shadow p-6 lg:col-span-2">
          <CreativeBriefView brief={brief as any} />
        </div>
        <div className="space-y-3">
          {assets.map((asset, idx) => (
            <AssetCard key={idx} asset={asset as any} />
          ))}
        </div>
      </div>
    </div>
  )
}
