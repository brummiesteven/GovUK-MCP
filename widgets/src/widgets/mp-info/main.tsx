import React from 'react'
import ReactDOM from 'react-dom/client'
import MPInfo from './MPInfo'
import '@/components/styles.css'
import '@/types'

export interface MPData {
  id: number
  name: string
  party: string
  constituency: string
  membership_start?: string
  gender?: string
  thumbnail_url?: string
  data_source: string
  retrieved_at: string
}

const getData = (): MPData => {
  if (window.MCP_DATA) {
    return window.MCP_DATA as MPData
  }

  return {
    id: 172,
    name: 'Keir Starmer',
    party: 'Labour',
    constituency: 'Holborn and St Pancras',
    membership_start: '2015-05-07',
    gender: 'M',
    thumbnail_url: 'https://members-api.parliament.uk/api/Members/4514/Thumbnail',
    data_source: 'UK Parliament Members API',
    retrieved_at: new Date().toISOString()
  }
}

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <MPInfo data={getData()} />
  </React.StrictMode>
)
