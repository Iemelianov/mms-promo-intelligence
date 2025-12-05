import { ScatterChart, Scatter, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts'

interface Point { id: string; label: string; sales: number; margin: number; pareto?: boolean }

export default function EfficientFrontierChart({ scenarios }: { scenarios: Point[] }) {
  return (
    <div className="h-72">
      <ResponsiveContainer width="100%" height="100%">
        <ScatterChart>
          <CartesianGrid />
          <XAxis dataKey="sales" name="Sales" />
          <YAxis dataKey="margin" name="Margin" />
          <Tooltip cursor={{ strokeDasharray: '3 3' }} />
          <Scatter name="Scenarios" data={scenarios} fill="#0ea5e9">
            {scenarios.map((p) => (
              <Cell key={p.id} fill={p.pareto ? '#10b981' : '#0ea5e9'} stroke={p.pareto ? '#047857' : '#0284c7'} />
            ))}
          </Scatter>
        </ScatterChart>
      </ResponsiveContainer>
    </div>
  )
}

