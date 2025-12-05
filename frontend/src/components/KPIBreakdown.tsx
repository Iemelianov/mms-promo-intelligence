import { ScenarioKPI } from '../types'
import { formatNumber, formatPercent } from '../utils/format'

export default function KPIBreakdown({ kpi }: { kpi?: Partial<ScenarioKPI> }) {
  if (!kpi) return null
  return (
    <div className="space-y-4 text-sm">
      <div className="space-y-2">
        <div className="flex justify-between"><span>Sales</span><span className="font-semibold">{formatNumber(kpi.total_sales)}</span></div>
        <div className="flex justify-between"><span>Margin</span><span className="font-semibold">{formatNumber(kpi.total_margin)}</span></div>
        <div className="flex justify-between"><span>EBIT</span><span className="font-semibold">{formatNumber(kpi.total_ebit)}</span></div>
        <div className="flex justify-between"><span>Units</span><span className="font-semibold">{formatNumber(kpi.total_units)}</span></div>
      </div>

      {kpi.breakdown_by_channel && (
        <div className="space-y-1">
          <div className="font-semibold text-gray-800">By channel</div>
          <table className="w-full text-xs border">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-2 py-1 text-left">Channel</th>
                <th className="px-2 py-1 text-right">Sales</th>
                <th className="px-2 py-1 text-right">Margin</th>
                <th className="px-2 py-1 text-right">Units</th>
              </tr>
            </thead>
            <tbody>
              {Object.entries(kpi.breakdown_by_channel).map(([ch, vals]) => (
                <tr key={ch} className="border-t">
                  <td className="px-2 py-1">{ch}</td>
                  <td className="px-2 py-1 text-right">{formatNumber(vals.sales_value)}</td>
                  <td className="px-2 py-1 text-right">{formatPercent(vals.margin_pct)}</td>
                  <td className="px-2 py-1 text-right">{formatNumber(vals.units)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {kpi.breakdown_by_department && (
        <div className="space-y-1">
          <div className="font-semibold text-gray-800">By department</div>
          <table className="w-full text-xs border">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-2 py-1 text-left">Department</th>
                <th className="px-2 py-1 text-right">Sales</th>
                <th className="px-2 py-1 text-right">Margin</th>
                <th className="px-2 py-1 text-right">Units</th>
              </tr>
            </thead>
            <tbody>
              {Object.entries(kpi.breakdown_by_department).map(([dept, vals]) => (
                <tr key={dept} className="border-t">
                  <td className="px-2 py-1">{dept}</td>
                  <td className="px-2 py-1 text-right">{formatNumber(vals.sales_value)}</td>
                  <td className="px-2 py-1 text-right">{formatPercent(vals.margin_pct)}</td>
                  <td className="px-2 py-1 text-right">{formatNumber(vals.units)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {kpi.breakdown_by_segment && (
        <div className="space-y-1">
          <div className="font-semibold text-gray-800">By segment</div>
          <table className="w-full text-xs border">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-2 py-1 text-left">Segment</th>
                <th className="px-2 py-1 text-right">Sales</th>
                <th className="px-2 py-1 text-right">Margin</th>
                <th className="px-2 py-1 text-right">Units</th>
              </tr>
            </thead>
            <tbody>
              {Object.entries(kpi.breakdown_by_segment).map(([seg, vals]) => (
                <tr key={seg} className="border-t">
                  <td className="px-2 py-1">{seg}</td>
                  <td className="px-2 py-1 text-right">{formatNumber(vals.sales_value)}</td>
                  <td className="px-2 py-1 text-right">{formatPercent(vals.margin_pct)}</td>
                  <td className="px-2 py-1 text-right">{formatNumber(vals.units)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}

