import { useQuery } from '@tanstack/react-query'
import { storeApi } from '@/api/store'

export const useStores = () => {
  return useQuery({
    queryKey: ['stores'],
    queryFn: storeApi.list,
    staleTime: 10 * 60 * 1000,
  })
}
