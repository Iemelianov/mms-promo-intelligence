export const formatNumber = (value?: number, options?: Intl.NumberFormatOptions) => {
  if (value === undefined || value === null || Number.isNaN(value)) return '-'
  return value.toLocaleString(undefined, { maximumFractionDigits: 2, ...options })
}

export const formatPercent = (value?: number, options?: Intl.NumberFormatOptions) => {
  if (value === undefined || value === null || Number.isNaN(value)) return '-'
  return `${value.toLocaleString(undefined, { maximumFractionDigits: 2, ...options })}%`
}

