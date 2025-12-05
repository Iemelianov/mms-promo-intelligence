export default function AssetCard({ asset }: { asset: any }) {
  const copy = async () => {
    if (navigator?.clipboard) {
      await navigator.clipboard.writeText(asset.copy_text || '')
    }
  }
  return (
    <div className="bg-white rounded-lg shadow p-4 border text-sm space-y-2">
      <div className="font-semibold">{asset.asset_type}</div>
      <div className="text-gray-700 whitespace-pre-line">{asset.copy_text}</div>
      <button className="text-blue-600 text-xs underline" onClick={copy}>Copy</button>
    </div>
  )
}

