import React from 'react'
import ReactDOM from 'react-dom/client'
import PostcodeLookup from './PostcodeLookup'
import '@/components/styles.css'
import '@/types'

export interface PostcodeData {
  postcode: string
  latitude: number
  longitude: number
  admin_district: string
  parliamentary_constituency: string
  region: string
  country: string
  ward?: string
  data_source: string
  retrieved_at: string
}

const getData = (): PostcodeData => {
  if (window.MCP_DATA) {
    return window.MCP_DATA as PostcodeData
  }

  return {
    postcode: 'SW1A 1AA',
    latitude: 51.5014,
    longitude: -0.1419,
    admin_district: 'Westminster',
    parliamentary_constituency: 'Cities of London and Westminster',
    region: 'London',
    country: 'England',
    ward: "St James's",
    data_source: 'Postcodes.io API',
    retrieved_at: new Date().toISOString()
  }
}

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <PostcodeLookup data={getData()} />
  </React.StrictMode>
)
