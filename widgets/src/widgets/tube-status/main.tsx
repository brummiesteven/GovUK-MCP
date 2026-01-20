import React from 'react'
import ReactDOM from 'react-dom/client'
import TubeStatus from './TubeStatus'
import '@/components/styles.css'
import '@/types'

export interface TubeLine {
  name: string
  status: string
  reason?: string
}

export interface TubeStatusData {
  lines: TubeLine[]
  data_source: string
  retrieved_at: string
}

// Get data from MCP Apps or use demo data
const getData = (): TubeStatusData => {
  if (window.MCP_DATA) {
    return window.MCP_DATA as TubeStatusData
  }

  // Demo data for development
  return {
    lines: [
      { name: 'Bakerloo', status: 'Good Service' },
      { name: 'Central', status: 'Minor Delays', reason: 'Earlier signal failure at Holborn' },
      { name: 'Circle', status: 'Good Service' },
      { name: 'District', status: 'Part Suspended', reason: 'No service Earls Court to Edgware Road' },
      { name: 'Hammersmith & City', status: 'Good Service' },
      { name: 'Jubilee', status: 'Good Service' },
      { name: 'Metropolitan', status: 'Good Service' },
      { name: 'Northern', status: 'Severe Delays', reason: 'Train fault at Camden Town' },
      { name: 'Piccadilly', status: 'Good Service' },
      { name: 'Victoria', status: 'Good Service' },
      { name: 'Waterloo & City', status: 'Good Service' }
    ],
    data_source: 'Transport for London API',
    retrieved_at: new Date().toISOString()
  }
}

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <TubeStatus data={getData()} />
  </React.StrictMode>
)
