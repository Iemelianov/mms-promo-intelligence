import { useMutation, useQuery } from '@tanstack/react-query'
import { dataApi } from '../services/api'

export const useProcessXlsb = () =>
  useMutation({
    mutationFn: (files: File[]) => dataApi.processXlsb(files),
  })

export const useQualityReport = () =>
  useQuery({
    queryKey: ['data', 'quality'],
    queryFn: () => dataApi.quality(),
  })

