import { ScatterChart, Scatter, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'

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
            {/* Recharts will color by dataKey if provided; using pareto flag to alter stroke */}
          </Scatter>
        </ScatterChart>
      </ResponsiveContainer>
    </div>
  )
}

