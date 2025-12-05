import { useState } from 'react'
import CreativeBriefView from '../components/CreativeBriefView'
import AssetCard from '../components/AssetCard'
import { useGenerateAssets, useGenerateBrief } from '../hooks/useCreative'
import { useScenarioSelectionStore } from '../store/useScenarioSelectionStore'
import { useScenarioStore } from '../store/useScenarioStore'
import { notifyError, notifySuccess } from '../lib/toast'
import { EmptyState, LoadingState } from '../components/Status'

export default function CreativeScreen() {
  const { selectedScenarioIds } = useScenarioSelectionStore()
  const { byId } = useScenarioStore()
  const primaryScenario = selectedScenarioIds.map(byId).find(Boolean)
  const [briefResult, setBriefResult] = useState<any>()
  const [assetsResult, setAssetsResult] = useState<any[]>([])

  const generateBrief = useGenerateBrief()
  const generateAssets = useGenerateAssets()

  const handleGenerate = async () => {
    if (!primaryScenario?.scenario) return
    try {
      const brief = await generateBrief.mutateAsync({
        scenario: primaryScenario.scenario,
        segments: primaryScenario.scenario.segments,
      })
      setBriefResult(brief)
      const assets = await generateAssets.mutateAsync(brief)
      setAssetsResult(assets)
      notifySuccess('Creative brief and assets generated')
    } catch (e) {
      console.error('Failed to generate creative', e)
      notifyError('Failed to generate creative')
    }
  }

  return (
    <div className="px-4 py-6 space-y-6">
      <h2 className="text-2xl font-bold text-gray-900 mb-4">Creative Companion</h2>
      <div className="flex items-center gap-3">
        <button
          onClick={handleGenerate}
          className="bg-blue-600 text-white px-4 py-2 rounded-md disabled:opacity-60"
          disabled={!primaryScenario || generateBrief.isPending || generateAssets.isPending}
        >
          {generateBrief.isPending || generateAssets.isPending ? 'Generating...' : 'Generate from selected'}
        </button>
        {!primaryScenario && <div className="text-sm text-gray-600">Select a scenario in Scenario Lab</div>}
      </div>
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="bg-white rounded-lg shadow p-6 lg:col-span-2">
          {briefResult ? (
            <CreativeBriefView brief={briefResult} />
          ) : (
            generateBrief.isPending ? <LoadingState /> : <EmptyState message="No brief yet" />
          )}
        </div>
        <div className="space-y-3">
          {assetsResult.length > 0 ? (
            assetsResult.map((asset, idx) => <AssetCard key={idx} asset={asset} />)
          ) : (
            generateAssets.isPending ? <LoadingState /> : <EmptyState message="No assets yet" />
          )}
        </div>
      </div>
    </div>
  )
}
