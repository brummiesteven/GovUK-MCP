// MCP Apps passes data via window object
// Use unknown type to avoid conflicts between widgets
declare global {
  interface Window {
    MCP_DATA?: unknown
  }
}

export {}
