export interface PickupStore {
  id: number
  name: string
  address: string
  contact: string | null
}

export interface CartItem {
  id: number
  product: {
    id: string
    name: string
    price: number
    is_tasting_available: boolean
    main_image: string
  }
  quantity: number
  subtotal: string
  pickup_store: PickupStore | null
  pickup_date: string | null
}

export interface CartResponse {
  count: number
  next: string | null
  previous: string | null
  results: CartItem[]
  cart_items: CartItem[]
  package_drafts?: unknown[]
  total_price: number
  final_total: number
}
