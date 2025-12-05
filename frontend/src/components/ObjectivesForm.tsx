interface Props {
  onSubmit: (values: { maximize: string; minMargin: number; maxDiscount: number }) => void
}

export default function ObjectivesForm({ onSubmit }: Props) {
  return (
    <form
      className="space-y-3 text-sm"
      onSubmit={(e) => {
        e.preventDefault()
        const form = new FormData(e.currentTarget)
        const maximize = String(form.get('maximize') || 'sales')
        const minMargin = Number(form.get('minMargin') || 20)
        const maxDiscount = Number(form.get('maxDiscount') || 25)
        onSubmit({ maximize, minMargin, maxDiscount })
      }}
    >
      <div className="space-y-1">
        <label className="font-medium">Maximize</label>
        <select name="maximize" className="border rounded px-2 py-1 w-full" defaultValue="sales">
          <option value="sales">Sales</option>
          <option value="margin">Margin</option>
          <option value="ebit">EBIT</option>
        </select>
      </div>
      <div className="space-y-1">
        <label className="font-medium">Min Margin %</label>
        <input name="minMargin" className="border rounded px-2 py-1 w-full" defaultValue={20} type="number" />
      </div>
      <div className="space-y-1">
        <label className="font-medium">Max Discount %</label>
        <input name="maxDiscount" className="border rounded px-2 py-1 w-full" defaultValue={25} type="number" />
      </div>
      <button className="bg-blue-600 text-white px-3 py-2 rounded" type="submit">Generate</button>
    </form>
  )
}

