import React from 'react'
import ReactDOM from 'react-dom/client'
import FoodHygiene from './FoodHygiene'
import '@/components/styles.css'
import '@/types'

export interface Establishment {
  name: string
  rating: string
  address: string
  inspection_date: string
  business_type?: string
}

export interface FoodHygieneData {
  query?: string
  postcode?: string
  total_results: number
  showing: number
  establishments: Establishment[]
  data_source: string
  retrieved_at: string
}

const getData = (): FoodHygieneData => {
  if (window.MCP_DATA) {
    return window.MCP_DATA as FoodHygieneData
  }

  return {
    postcode: 'SW1A 1AA',
    total_results: 5,
    showing: 5,
    establishments: [
      { name: 'The Wolseley', rating: '5', address: '160 Piccadilly, London', inspection_date: '2024-06-15', business_type: 'Restaurant' },
      { name: 'Pret A Manger', rating: '5', address: '10 Victoria Street', inspection_date: '2024-03-20', business_type: 'Takeaway' },
      { name: 'Costa Coffee', rating: '4', address: '55 Whitehall', inspection_date: '2024-01-10', business_type: 'Cafe' },
      { name: "Joe's Kitchen", rating: '3', address: '22 Broadway', inspection_date: '2023-11-05', business_type: 'Restaurant' },
      { name: 'Quick Bites', rating: '2', address: '8 Market Lane', inspection_date: '2023-09-18', business_type: 'Takeaway' }
    ],
    data_source: 'Food Standards Agency API',
    retrieved_at: new Date().toISOString()
  }
}

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <FoodHygiene data={getData()} />
  </React.StrictMode>
)
