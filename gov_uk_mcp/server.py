"""Gov.uk MCP Server - FastMCP implementation."""
import logging
import sys
from pathlib import Path
from dotenv import load_dotenv
from fastmcp import FastMCP

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Fix for running with -m: ensure this module is accessible as gov_uk_mcp.server
# When running with python -m gov_uk_mcp.server, the module is loaded as __main__
# but tool files import from gov_uk_mcp.server, creating a duplicate module.
# This ensures both refer to the same module instance.
if __name__ == "__main__" and "gov_uk_mcp.server" not in sys.modules:
    sys.modules["gov_uk_mcp.server"] = sys.modules[__name__]

# Create FastMCP server instance
mcp = FastMCP(
    name="gov-uk-mcp",
    instructions="Access 33 UK government APIs including Companies House, Transport for London, NHS, Parliament, and more."
)

# Widget directory for UI resources
WIDGET_DIR = Path(__file__).parent.parent / "widgets" / "dist"

# Import tool modules - decorators auto-register tools with mcp instance
# These imports must come AFTER mcp is defined to avoid circular imports
from gov_uk_mcp.tools import postcode  # noqa: E402
from gov_uk_mcp.tools import transport  # noqa: E402
from gov_uk_mcp.tools import companies_house  # noqa: E402
from gov_uk_mcp.tools import food_hygiene  # noqa: E402
from gov_uk_mcp.tools import bank_holidays  # noqa: E402
from gov_uk_mcp.tools import search  # noqa: E402
from gov_uk_mcp.tools import flood_warnings  # noqa: E402
from gov_uk_mcp.tools import police_crime  # noqa: E402
from gov_uk_mcp.tools import epc  # noqa: E402
from gov_uk_mcp.tools import courts  # noqa: E402
from gov_uk_mcp.tools import charity  # noqa: E402
from gov_uk_mcp.tools import nhs  # noqa: E402
from gov_uk_mcp.tools import legislation  # noqa: E402
from gov_uk_mcp.tools import cqc  # noqa: E402
from gov_uk_mcp.tools import mps  # noqa: E402
from gov_uk_mcp.tools import hansard  # noqa: E402
from gov_uk_mcp.tools import voting  # noqa: E402
from gov_uk_mcp.tools import parliamentary_questions  # noqa: E402


# Inline MCP Apps widgets (SEP-1865 compliant)
# These are self-contained HTML that work with the MCP Apps postMessage protocol

WIDGET_STYLES = '''
/* CSS Custom Properties for theming */
:root {
  --bg-primary: #1a1a1a;
  --bg-card: #2a2a2a;
  --bg-elevated: #333;
  --text-primary: #fff;
  --text-secondary: #ccc;
  --text-muted: #888;
  --text-dim: #777;
  --border-subtle: #333;
  --accent-good: #22c55e;
  --accent-good-text: #4ade80;
  --accent-warning: #f59e0b;
  --accent-warning-text: #fbbf24;
  --accent-error: #ef4444;
  --accent-error-text: #f87171;
  --accent-info: #6366f1;
  --accent-nhs: #005EB8;
  --accent-tfl: #0019A8;
  --accent-govuk: #1D70B8;
  --accent-parliament: #4A7729;
  --radius-sm: 4px;
  --radius-md: 8px;
  --radius-lg: 12px;
}

* { box-sizing: border-box; }
body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', sans-serif;
  margin: 0;
  padding: 16px;
  background: var(--bg-primary);
  color: var(--text-secondary);
  line-height: 1.5;
  -webkit-font-smoothing: antialiased;
}
.widget-container { max-width: 600px; }
.widget-header { margin-bottom: 16px; }
.widget-title {
  font-size: clamp(18px, 4vw, 20px);
  font-weight: 600;
  margin: 0 0 4px 0;
  color: var(--text-primary);
  letter-spacing: -0.02em;
}
.widget-subtitle {
  font-size: 13px;
  color: var(--text-muted);
  margin: 0;
}
.widget-section { margin-bottom: 16px; }
.section-title {
  font-size: 11px;
  font-weight: 600;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 8px;
}

/* Status Cards */
.status-card {
  background: var(--bg-card);
  border-radius: var(--radius-md);
  padding: 14px 16px;
  margin-bottom: 8px;
  border-left: 4px solid #444;
  box-shadow: 0 1px 3px rgba(0,0,0,0.3);
  transition: transform 0.15s ease, box-shadow 0.15s ease;
  position: relative;
}
.status-card:hover {
  transform: translateX(2px);
  box-shadow: 0 2px 6px rgba(0,0,0,0.4);
}
.status-card:focus-visible {
  outline: 2px solid var(--accent-info);
  outline-offset: 2px;
}
.status-good { border-left-color: var(--accent-good); }
.status-warning { border-left-color: var(--accent-warning); }
.status-error { border-left-color: var(--accent-error); }
/* Brand accent colors for non-status cards */
.accent-nhs { border-left-color: var(--accent-nhs) !important; }
.accent-tfl { border-left-color: var(--accent-tfl) !important; }
.accent-govuk { border-left-color: var(--accent-govuk) !important; }
.accent-parliament { border-left-color: var(--accent-parliament) !important; }
.status-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
}
.status-name {
  font-weight: 500;
  font-size: 14px;
  color: var(--text-primary);
}
.status-badge {
  font-size: 11px;
  padding: 3px 10px;
  border-radius: var(--radius-lg);
  font-weight: 500;
  white-space: nowrap;
}
.badge-good { background: rgba(34, 197, 94, 0.15); color: var(--accent-good-text); }
.badge-warning { background: rgba(245, 158, 11, 0.15); color: var(--accent-warning-text); }
.badge-error { background: rgba(239, 68, 68, 0.15); color: var(--accent-error-text); }
.status-reason {
  font-size: 12px;
  color: var(--text-muted);
  margin-top: 8px;
  line-height: 1.4;
}

/* Info Grid */
.info-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
}
.info-grid-3 { grid-template-columns: repeat(3, 1fr); }
.info-item {
  background: var(--bg-card);
  padding: 14px;
  border-radius: var(--radius-md);
  box-shadow: 0 1px 3px rgba(0,0,0,0.2);
}
.info-item:focus-visible {
  outline: 2px solid var(--accent-info);
  outline-offset: 2px;
}
.info-item-full { grid-column: 1 / -1; }
.info-item-highlight {
  background: linear-gradient(135deg, var(--bg-card) 0%, var(--bg-elevated) 100%);
}
.info-label {
  font-size: 10px;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  font-weight: 500;
}
.info-value {
  font-size: 14px;
  color: var(--text-primary);
  margin-top: 4px;
  font-weight: 500;
}
.info-value-sm { font-size: 13px; font-weight: 400; }
.info-value-lg { font-size: 18px; }

/* Pills / Tags */
.pill-container {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}
.pill {
  padding: 6px 12px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 500;
  display: inline-flex;
  align-items: center;
  gap: 6px;
}
.pill[tabindex]:focus-visible {
  outline: 2px solid var(--text-primary);
  outline-offset: 1px;
}
.pill-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}

/* Profile Card */
.profile-card {
  display: flex;
  gap: 16px;
  align-items: flex-start;
}
.profile-avatar {
  width: 72px;
  height: 72px;
  border-radius: var(--radius-md);
  background: var(--bg-elevated);
  object-fit: cover;
  flex-shrink: 0;
}
.profile-info { flex: 1; min-width: 0; }
.profile-name {
  font-size: clamp(16px, 4vw, 18px);
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 4px 0;
}
.profile-party {
  display: inline-block;
  padding: 3px 10px;
  border-radius: var(--radius-lg);
  font-size: 12px;
  font-weight: 500;
  margin-bottom: 8px;
}
.profile-meta {
  font-size: 13px;
  color: var(--text-muted);
}

/* Rating Display */
.rating-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  border-radius: var(--radius-md);
  font-size: 18px;
  font-weight: 700;
  flex-shrink: 0;
}
.rating-5, .rating-4 { background: rgba(34, 197, 94, 0.2); color: var(--accent-good-text); }
.rating-3 { background: rgba(245, 158, 11, 0.2); color: var(--accent-warning-text); }
.rating-2, .rating-1, .rating-0 { background: rgba(239, 68, 68, 0.2); color: var(--accent-error-text); }
.rating-exempt { background: rgba(100, 100, 100, 0.2); color: #999; font-size: 10px; }

/* Score Bar */
.score-row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 8px;
}
.score-label {
  font-size: 10px;
  color: var(--text-muted);
  width: 70px;
  flex-shrink: 0;
}
.score-bar {
  flex: 1;
  height: 6px;
  background: var(--bg-elevated);
  border-radius: 3px;
  overflow: hidden;
}
.score-fill {
  height: 100%;
  border-radius: 3px;
  transition: width 0.3s ease;
}
.score-fill-good { background: linear-gradient(90deg, var(--accent-good), var(--accent-good-text)); }
.score-fill-warning { background: linear-gradient(90deg, var(--accent-warning), var(--accent-warning-text)); }
.score-fill-error { background: linear-gradient(90deg, var(--accent-error), var(--accent-error-text)); }

/* Address Card */
.address-card {
  background: var(--bg-card);
  border-radius: var(--radius-md);
  padding: 14px 16px;
  margin-top: 12px;
}
.address-label {
  font-size: 10px;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 6px;
}
.address-text {
  font-size: 13px;
  color: var(--text-secondary);
  line-height: 1.5;
}

/* Company Status */
.company-status {
  display: inline-block;
  padding: 4px 12px;
  border-radius: var(--radius-lg);
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.03em;
}
.status-active { background: rgba(34, 197, 94, 0.15); color: var(--accent-good-text); }
.status-dissolved { background: rgba(239, 68, 68, 0.15); color: var(--accent-error-text); }
.status-liquidation { background: rgba(245, 158, 11, 0.15); color: var(--accent-warning-text); }

/* SIC Codes */
.sic-list {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-top: 6px;
}
.sic-tag {
  background: var(--bg-elevated);
  padding: 4px 10px;
  border-radius: var(--radius-sm);
  font-size: 12px;
  color: #aaa;
  font-family: 'SF Mono', Monaco, Consolas, monospace;
}

/* Flood Severity */
.severity-indicator {
  display: flex;
  align-items: center;
  gap: 8px;
}
.severity-icon {
  width: 24px;
  height: 24px;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  flex-shrink: 0;
}
.severity-1 { background: rgba(239, 68, 68, 0.2); color: var(--accent-error); }
.severity-2 { background: rgba(245, 158, 11, 0.2); color: var(--accent-warning); }
.severity-3 { background: rgba(234, 179, 8, 0.2); color: #eab308; }
.severity-4 { background: rgba(34, 197, 94, 0.2); color: var(--accent-good); }

/* MP list */
.mp-list-item {
  display: flex;
  align-items: center;
  gap: 12px;
  background: var(--bg-card);
  padding: 12px 14px;
  border-radius: var(--radius-md);
  margin-bottom: 8px;
}
.mp-thumb {
  width: 48px;
  height: 48px;
  border-radius: 6px;
  background: var(--bg-elevated);
  object-fit: cover;
  flex-shrink: 0;
}
.mp-details { flex: 1; min-width: 0; }
.mp-name {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
  margin-bottom: 2px;
}
.mp-constituency {
  font-size: 12px;
  color: var(--text-muted);
}
.mp-party-badge {
  padding: 4px 10px;
  border-radius: var(--radius-lg);
  font-size: 11px;
  font-weight: 500;
  flex-shrink: 0;
}

/* Footer */
.widget-footer {
  font-size: 11px;
  color: var(--text-dim);
  margin-top: 16px;
  padding-top: 12px;
  border-top: 1px solid var(--bg-card);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

/* Empty State */
.empty-state {
  text-align: center;
  padding: 32px 16px;
  color: var(--text-muted);
}
.empty-icon {
  font-size: 32px;
  margin-bottom: 12px;
  opacity: 0.5;
}
.empty-text {
  font-size: 14px;
}

/* Loading */
.loading {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 48px;
  color: var(--text-muted);
}
@keyframes pulse {
  0%, 100% { opacity: 0.4; transform: scale(0.8); }
  50% { opacity: 1; transform: scale(1); }
}
.loading-dot {
  width: 8px;
  height: 8px;
  background: var(--text-muted);
  border-radius: 50%;
  margin: 0 4px;
  animation: pulse 1.2s ease-in-out infinite;
}
.loading-dot:nth-child(1) { animation-delay: 0s; }
.loading-dot:nth-child(2) { animation-delay: 0.15s; }
.loading-dot:nth-child(3) { animation-delay: 0.3s; }

/* Skeleton Loading */
@keyframes shimmer {
  0% { background-position: -200px 0; }
  100% { background-position: calc(200px + 100%) 0; }
}
.skeleton {
  background: linear-gradient(90deg, var(--bg-card) 0px, var(--bg-elevated) 40px, var(--bg-card) 80px);
  background-size: 200px 100%;
  animation: shimmer 1.5s ease-in-out infinite;
  border-radius: var(--radius-sm);
}
.skeleton-text { height: 14px; margin-bottom: 8px; }
.skeleton-title { height: 20px; width: 60%; margin-bottom: 12px; }
.skeleton-card { height: 60px; margin-bottom: 8px; border-radius: var(--radius-md); }

/* Error */
.error-state {
  background: rgba(239, 68, 68, 0.08);
  border: 1px solid rgba(239, 68, 68, 0.2);
  border-radius: var(--radius-md);
  padding: 20px;
  color: var(--accent-error-text);
  font-size: 13px;
  text-align: center;
}
.error-state::before {
  content: "!";
  display: block;
  width: 32px;
  height: 32px;
  margin: 0 auto 12px;
  background: rgba(239, 68, 68, 0.15);
  border-radius: 50%;
  line-height: 32px;
  font-weight: 600;
  font-size: 18px;
}

/* Utility Classes */
.font-mono {
  font-family: 'SF Mono', Monaco, Consolas, monospace;
  letter-spacing: 0.02em;
}
.truncate {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.mt-8 { margin-top: 8px !important; }
.mt-12 { margin-top: 12px !important; }
.mt-16 { margin-top: 16px !important; }
.mt-20 { margin-top: 20px !important; }
.mb-8 { margin-bottom: 8px !important; }
.mb-12 { margin-bottom: 12px !important; }
.mb-16 { margin-bottom: 16px !important; }
.pt-12 { padding-top: 12px !important; }
.gap-8 { gap: 8px !important; }
.gap-12 { gap: 12px !important; }

/* Responsive Breakpoints */
@media (max-width: 400px) {
  .info-grid { grid-template-columns: 1fr; }
  .info-grid-3 { grid-template-columns: 1fr; }
  .profile-avatar { width: 56px; height: 56px; }
  .profile-name { font-size: 16px; }
  .widget-title { font-size: 18px; }
  .status-header { flex-direction: column; align-items: flex-start; gap: 8px; }
  .profile-card { flex-direction: column; align-items: center; text-align: center; }
}
'''

WIDGETS = {
    "tube-status": '''
<div id="app"><div class="loading"><span class="loading-dot"></span><span class="loading-dot"></span><span class="loading-dot"></span></div></div>
<script>
// Official TfL line colors
const TUBE_COLORS = {
  "Bakerloo": "#B36305",
  "Central": "#E32017",
  "Circle": "#FFD300",
  "District": "#00782A",
  "Hammersmith & City": "#F3A9BB",
  "Jubilee": "#A0A5A9",
  "Metropolitan": "#9B0056",
  "Northern": "#000000",
  "Piccadilly": "#003688",
  "Victoria": "#0098D4",
  "Waterloo & City": "#95CDBA",
  "Elizabeth": "#6950a1",
  "DLR": "#00A4A7",
  "Overground": "#EE7C0E",
  "London Overground": "#EE7C0E",
  "TfL Rail": "#0019A8",
  "Tram": "#84B817"
};

// Lines that need dark text on their background
const DARK_TEXT_LINES = ["Circle", "Hammersmith & City", "Waterloo & City", "Tram"];

function getStatus(s) {
  if (!s) return "good";
  s = s.toLowerCase();
  if (s.includes("good") || s.includes("special")) return "good";
  if (s.includes("minor") || s.includes("reduced") || s.includes("part")) return "warning";
  return "error";
}

function getStatusIcon(status) {
  if (status === "good") return "&#10003;";
  if (status === "warning") return "!";
  return "&#10005;";
}

window.render = function(data) {
  const app = document.getElementById("app");
  if (!data || !data.lines) {
    app.innerHTML = '<div class="error-state">Unable to load tube status data</div>';
    return;
  }

  const issues = data.lines.filter(l => getStatus(l.status) !== "good");
  const good = data.lines.filter(l => getStatus(l.status) === "good");

  // Sort issues by severity (errors first)
  issues.sort((a, b) => {
    const aStatus = getStatus(a.status);
    const bStatus = getStatus(b.status);
    if (aStatus === "error" && bStatus !== "error") return -1;
    if (bStatus === "error" && aStatus !== "error") return 1;
    return 0;
  });

  let html = '<div class="widget-container">';
  html += '<div class="widget-header">';
  html += '<h1 class="widget-title">TfL Status</h1>';

  if (issues.length > 0) {
    html += '<p class="widget-subtitle">' + issues.length + ' line' + (issues.length > 1 ? 's' : '') + ' with disruptions</p>';
  } else {
    html += '<p class="widget-subtitle">All lines running normally</p>';
  }
  html += '</div>';

  // Show disrupted lines first with detailed cards
  if (issues.length > 0) {
    html += '<div class="widget-section">';
    html += '<div class="section-title">Service Disruptions</div>';
    issues.forEach(l => {
      const st = getStatus(l.status);
      const color = TUBE_COLORS[l.line] || "#666";
      html += '<div class="status-card status-' + st + '">';
      html += '<div class="status-header">';
      html += '<div style="display:flex;align-items:center;gap:10px">';
      html += '<span style="width:4px;height:28px;background:' + color + ';border-radius:2px;flex-shrink:0"></span>';
      html += '<span class="status-name">' + escapeHtml(l.line) + '</span>';
      html += '</div>';
      html += '<span class="status-badge badge-' + st + '">' + escapeHtml(l.status) + '</span>';
      html += '</div>';
      if (l.reason) {
        html += '<div class="status-reason">' + escapeHtml(l.reason) + '</div>';
      }
      html += '</div>';
    });
    html += '</div>';
  }

  // Show good service lines as compact pills
  if (good.length > 0) {
    html += '<div class="widget-section">';
    html += '<div class="section-title">Good Service</div>';
    html += '<div class="pill-container">';
    good.forEach(l => {
      const color = TUBE_COLORS[l.line] || "#666";
      const textColor = DARK_TEXT_LINES.includes(l.line) ? "#000" : "#fff";
      html += '<span class="pill" style="background:' + color + ';color:' + textColor + '">';
      html += '<span class="pill-dot" style="background:' + (DARK_TEXT_LINES.includes(l.line) ? 'rgba(0,0,0,0.3)' : 'rgba(255,255,255,0.4)') + '"></span>';
      html += escapeHtml(l.line);
      html += '</span>';
    });
    html += '</div>';
    html += '</div>';
  }

  html += '<div class="widget-footer">';
  html += '<span>' + escapeHtml(data.data_source || "Transport for London") + '</span>';
  if (data.retrieved_at) {
    html += '<span>Updated ' + formatTime(data.retrieved_at) + '</span>';
  }
  html += '</div>';
  html += '</div>';

  app.innerHTML = html;
}
</script>
''',
    "postcode-lookup": '''
<div id="app"><div class="loading"><span class="loading-dot"></span><span class="loading-dot"></span><span class="loading-dot"></span></div></div>
<script>
window.render = function(data) {
  const app = document.getElementById("app");

  if (!data || data.error) {
    app.innerHTML = '<div class="error-state">' + escapeHtml(data?.error || "Unable to load postcode data") + '</div>';
    return;
  }

  let html = '<div class="widget-container">';

  // Header with prominent postcode
  html += '<div class="widget-header">';
  html += '<h1 class="widget-title" style="font-size:28px;letter-spacing:0.05em;font-family:monospace">' + escapeHtml(data.postcode) + '</h1>';
  html += '<p class="widget-subtitle">' + escapeHtml([data.admin_district, data.region].filter(Boolean).join(", ")) + '</p>';
  html += '</div>';

  // Location info grid
  html += '<div class="widget-section">';
  html += '<div class="section-title">Location</div>';
  html += '<div class="info-grid">';

  if (data.country) {
    html += '<div class="info-item">';
    html += '<div class="info-label">Country</div>';
    html += '<div class="info-value">' + escapeHtml(data.country) + '</div>';
    html += '</div>';
  }

  if (data.region) {
    html += '<div class="info-item">';
    html += '<div class="info-label">Region</div>';
    html += '<div class="info-value">' + escapeHtml(data.region) + '</div>';
    html += '</div>';
  }

  if (data.admin_district) {
    html += '<div class="info-item">';
    html += '<div class="info-label">District</div>';
    html += '<div class="info-value">' + escapeHtml(data.admin_district) + '</div>';
    html += '</div>';
  }

  if (data.ward) {
    html += '<div class="info-item">';
    html += '<div class="info-label">Ward</div>';
    html += '<div class="info-value">' + escapeHtml(data.ward) + '</div>';
    html += '</div>';
  }

  html += '</div>';
  html += '</div>';

  // Political representation
  if (data.parliamentary_constituency) {
    html += '<div class="widget-section">';
    html += '<div class="section-title">Parliamentary Constituency</div>';
    html += '<div class="info-item info-item-full info-item-highlight">';
    html += '<div class="info-value" style="font-size:15px">' + escapeHtml(data.parliamentary_constituency) + '</div>';
    html += '</div>';
    html += '</div>';
  }

  // Coordinates
  if (data.latitude !== undefined && data.longitude !== undefined) {
    html += '<div class="widget-section">';
    html += '<div class="section-title">Coordinates</div>';
    html += '<div class="info-grid">';
    html += '<div class="info-item">';
    html += '<div class="info-label">Latitude</div>';
    html += '<div class="info-value info-value-sm font-mono">' + (typeof data.latitude === 'number' ? data.latitude.toFixed(6) : escapeHtml(data.latitude)) + '</div>';
    html += '</div>';
    html += '<div class="info-item">';
    html += '<div class="info-label">Longitude</div>';
    html += '<div class="info-value info-value-sm font-mono">' + (typeof data.longitude === 'number' ? data.longitude.toFixed(6) : escapeHtml(data.longitude)) + '</div>';
    html += '</div>';
    html += '</div>';
    html += '</div>';
  }

  html += '<div class="widget-footer">';
  html += '<span>' + escapeHtml(data.data_source || "Postcodes.io") + '</span>';
  html += '</div>';
  html += '</div>';

  app.innerHTML = html;
}
</script>
''',
    "company-info": '''
<div id="app"><div class="loading"><span class="loading-dot"></span><span class="loading-dot"></span><span class="loading-dot"></span></div></div>
<script>
function getStatusClass(status) {
  if (!status) return "";
  const s = status.toLowerCase();
  if (s === "active") return "status-active";
  if (s.includes("dissolv") || s.includes("struck")) return "status-dissolved";
  if (s.includes("liquid") || s.includes("admin") || s.includes("receiv")) return "status-liquidation";
  return "";
}

function formatCompanyType(type) {
  const types = {
    "ltd": "Private Limited",
    "private-limited-guarant-nsc": "Private Limited by Guarantee",
    "plc": "Public Limited Company",
    "llp": "Limited Liability Partnership",
    "private-unlimited": "Private Unlimited"
  };
  return types[type] || (type ? escapeHtml(type.replace(/-/g, " ").replace(/\b\w/g, l => l.toUpperCase())) : "");
}

window.render = function(data) {
  const app = document.getElementById("app");

  if (!data || data.error) {
    app.innerHTML = '<div class="error-state">' + escapeHtml(data?.error || "Unable to load company data") + '</div>';
    return;
  }

  let html = '<div class="widget-container">';

  // Header with company name and status badge
  html += '<div class="widget-header" style="margin-bottom:20px">';
  html += '<div style="display:flex;justify-content:space-between;align-items:flex-start;gap:12px">';
  html += '<div>';
  html += '<h1 class="widget-title" style="margin-bottom:6px">' + escapeHtml(data.company_name) + '</h1>';
  html += '<p class="widget-subtitle font-mono" style="letter-spacing:0.05em">' + escapeHtml(data.company_number) + '</p>';
  html += '</div>';
  if (data.company_status) {
    html += '<span class="company-status ' + getStatusClass(data.company_status) + '">' + escapeHtml(data.company_status) + '</span>';
  }
  html += '</div>';
  html += '</div>';

  // Company details
  html += '<div class="widget-section">';
  html += '<div class="section-title">Company Details</div>';
  html += '<div class="info-grid">';

  if (data.company_type) {
    html += '<div class="info-item">';
    html += '<div class="info-label">Type</div>';
    html += '<div class="info-value info-value-sm">' + formatCompanyType(data.company_type) + '</div>';
    html += '</div>';
  }

  if (data.date_of_creation) {
    html += '<div class="info-item">';
    html += '<div class="info-label">Incorporated</div>';
    html += '<div class="info-value">' + formatDate(data.date_of_creation) + '</div>';
    html += '</div>';
  }

  if (data.jurisdiction) {
    html += '<div class="info-item">';
    html += '<div class="info-label">Jurisdiction</div>';
    html += '<div class="info-value">' + escapeHtml(data.jurisdiction.replace(/-/g, " ").replace(/\b\w/g, l => l.toUpperCase())) + '</div>';
    html += '</div>';
  }

  // Accounts info
  if (data.accounts?.last_accounts?.made_up_to) {
    html += '<div class="info-item">';
    html += '<div class="info-label">Last Accounts</div>';
    html += '<div class="info-value info-value-sm">' + formatDate(data.accounts.last_accounts.made_up_to) + '</div>';
    html += '</div>';
  }

  html += '</div>';
  html += '</div>';

  // SIC codes
  if (data.sic_codes && data.sic_codes.length > 0) {
    html += '<div class="widget-section">';
    html += '<div class="section-title">SIC Codes</div>';
    html += '<div class="sic-list">';
    data.sic_codes.forEach(code => {
      html += '<span class="sic-tag">' + escapeHtml(code) + '</span>';
    });
    html += '</div>';
    html += '</div>';
  }

  // Registered address
  if (data.registered_office_address) {
    const addr = data.registered_office_address;
    const addressParts = [
      addr.address_line_1,
      addr.address_line_2,
      addr.locality,
      addr.region,
      addr.postal_code,
      addr.country
    ].filter(Boolean).map(p => escapeHtml(p));

    if (addressParts.length > 0) {
      html += '<div class="address-card">';
      html += '<div class="address-label">Registered Office</div>';
      html += '<div class="address-text">' + addressParts.join("<br>") + '</div>';
      html += '</div>';
    }
  }

  // Warning indicators
  if (data.has_insolvency_history || data.has_charges) {
    html += '<div style="display:flex;gap:8px;margin-top:12px">';
    if (data.has_insolvency_history) {
      html += '<span class="status-badge badge-warning">Insolvency History</span>';
    }
    if (data.has_charges) {
      html += '<span class="status-badge badge-warning">Has Charges</span>';
    }
    html += '</div>';
  }

  html += '<div class="widget-footer">';
  html += '<span>Companies House</span>';
  if (data.retrieved_at) {
    html += '<span>Updated ' + formatTime(data.retrieved_at) + '</span>';
  }
  html += '</div>';
  html += '</div>';

  app.innerHTML = html;
}
</script>
''',
    "food-hygiene": '''
<div id="app"><div class="loading"><span class="loading-dot"></span><span class="loading-dot"></span><span class="loading-dot"></span></div></div>
<script>
function getRatingClass(rating) {
  if (rating === "Exempt" || rating === "AwaitingInspection") return "rating-exempt";
  const num = parseInt(rating, 10);
  if (isNaN(num)) return "rating-exempt";
  if (num >= 4) return "rating-5";
  if (num === 3) return "rating-3";
  return "rating-0";
}

function getRatingDisplay(rating) {
  if (rating === "Exempt") return "EX";
  if (rating === "AwaitingInspection") return "...";
  return rating;
}

function getScoreClass(score) {
  if (score === null || score === undefined) return "";
  if (score <= 5) return "score-fill-good";
  if (score <= 10) return "score-fill-warning";
  return "score-fill-error";
}

function getScorePercent(score) {
  // FSA scores: 0 is best, 20+ is worst. Invert for visual
  if (score === null || score === undefined) return 0;
  return Math.max(0, Math.min(100, (20 - score) * 5));
}

window.render = function(data) {
  const app = document.getElementById("app");

  if (data?.message && !data.establishments) {
    app.innerHTML = '<div class="empty-state"><div class="empty-text">' + escapeHtml(data.message) + '</div></div>';
    return;
  }

  if (!data || data.error) {
    app.innerHTML = '<div class="error-state">' + escapeHtml(data?.error || "Unable to load food hygiene data") + '</div>';
    return;
  }

  const establishments = data.establishments || [];

  let html = '<div class="widget-container">';

  // Header
  html += '<div class="widget-header">';
  html += '<h1 class="widget-title">Food Hygiene Ratings</h1>';
  html += '<p class="widget-subtitle">' + data.total_results + ' establishment' + (data.total_results !== 1 ? 's' : '') + ' found</p>';
  html += '</div>';

  // Establishments list
  if (establishments.length > 0) {
    establishments.slice(0, 10).forEach(e => {
      const rating = e.rating || "N/A";
      const ratingClass = getRatingClass(rating);

      html += '<div class="status-card" style="border-left:none;display:flex;gap:14px;align-items:flex-start">';

      // Rating badge
      html += '<div class="rating-badge ' + ratingClass + '">' + getRatingDisplay(rating) + '</div>';

      // Business details
      html += '<div style="flex:1;min-width:0">';
      html += '<div class="status-name" style="margin-bottom:4px">' + escapeHtml(e.business_name) + '</div>';

      // Address
      const addressParts = [e.address, e.postcode].filter(Boolean).map(p => escapeHtml(p));
      if (addressParts.length > 0) {
        html += '<div class="status-reason" style="margin-top:0">' + addressParts.join(", ") + '</div>';
      }

      // Business type
      if (e.business_type) {
        html += '<div style="font-size:11px;color:#666;margin-top:4px">' + escapeHtml(e.business_type) + '</div>';
      }

      // Score bars (only if scores available)
      const hasScores = e.hygiene_score !== null || e.structural_score !== null || e.confidence_in_management !== null;
      if (hasScores) {
        html += '<div style="margin-top:10px">';

        if (e.hygiene_score !== null && e.hygiene_score !== undefined) {
          html += '<div class="score-row">';
          html += '<span class="score-label">Hygiene</span>';
          html += '<div class="score-bar"><div class="score-fill ' + getScoreClass(e.hygiene_score) + '" style="width:' + getScorePercent(e.hygiene_score) + '%"></div></div>';
          html += '</div>';
        }

        if (e.structural_score !== null && e.structural_score !== undefined) {
          html += '<div class="score-row">';
          html += '<span class="score-label">Structural</span>';
          html += '<div class="score-bar"><div class="score-fill ' + getScoreClass(e.structural_score) + '" style="width:' + getScorePercent(e.structural_score) + '%"></div></div>';
          html += '</div>';
        }

        if (e.confidence_in_management !== null && e.confidence_in_management !== undefined) {
          html += '<div class="score-row">';
          html += '<span class="score-label">Management</span>';
          html += '<div class="score-bar"><div class="score-fill ' + getScoreClass(e.confidence_in_management) + '" style="width:' + getScorePercent(e.confidence_in_management) + '%"></div></div>';
          html += '</div>';
        }

        html += '</div>';
      }

      // Rating date
      if (e.rating_date) {
        html += '<div style="font-size:10px;color:#555;margin-top:8px">Inspected: ' + formatDate(e.rating_date) + '</div>';
      }

      html += '</div>';
      html += '</div>';
    });

    // Show "more" indicator
    if (data.total_results > 10) {
      html += '<div style="text-align:center;padding:12px;color:#666;font-size:12px">Showing 10 of ' + data.total_results + ' results</div>';
    }
  }

  html += '<div class="widget-footer">';
  html += '<span>' + escapeHtml(data.data_source || "Food Standards Agency") + '</span>';
  if (data.retrieved_at) {
    html += '<span>Updated ' + formatTime(data.retrieved_at) + '</span>';
  }
  html += '</div>';
  html += '</div>';

  app.innerHTML = html;
}
</script>
''',
    "flood-warnings": '''
<div id="app"><div class="loading"><span class="loading-dot"></span><span class="loading-dot"></span><span class="loading-dot"></span></div></div>
<script>
function getSeverityInfo(level) {
  // Environment Agency severity levels: 1=Severe, 2=Warning, 3=Alert, 4=No longer in force
  const severities = {
    1: { class: "severity-1", icon: "!!", label: "Severe Flood Warning", color: "#ef4444", cardClass: "status-error" },
    2: { class: "severity-2", icon: "!", label: "Flood Warning", color: "#f59e0b", cardClass: "status-warning" },
    3: { class: "severity-3", icon: "i", label: "Flood Alert", color: "#eab308", cardClass: "status-warning" },
    4: { class: "severity-4", icon: "-", label: "Warning Removed", color: "#22c55e", cardClass: "status-good" }
  };
  return severities[level] || severities[3];
}

function formatTimeAgo(dateStr) {
  if (!dateStr) return "";
  const date = new Date(dateStr);
  const now = new Date();
  const diffMs = now - date;
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMins / 60);
  const diffDays = Math.floor(diffHours / 24);

  if (diffMins < 60) return diffMins + " min" + (diffMins !== 1 ? "s" : "") + " ago";
  if (diffHours < 24) return diffHours + " hour" + (diffHours !== 1 ? "s" : "") + " ago";
  return diffDays + " day" + (diffDays !== 1 ? "s" : "") + " ago";
}

window.render = function(data) {
  const app = document.getElementById("app");

  if (data?.message && !data.warnings) {
    app.innerHTML = '<div class="widget-container">' +
      '<div class="widget-header">' +
      '<h1 class="widget-title">Flood Warnings</h1>' +
      '</div>' +
      '<div class="empty-state" style="background:#2a2a2a;border-radius:8px">' +
      '<div style="font-size:24px;margin-bottom:8px;opacity:0.5">&#10003;</div>' +
      '<div class="empty-text">' + escapeHtml(data.message) + '</div>' +
      '</div>' +
      '<div class="widget-footer"><span>' + escapeHtml(data.data_source || "Environment Agency") + '</span></div>' +
      '</div>';
    return;
  }

  if (!data || data.error) {
    app.innerHTML = '<div class="error-state">' + escapeHtml(data?.error || "Unable to load flood warning data") + '</div>';
    return;
  }

  const warnings = data.warnings || [];

  // Sort by severity (most severe first)
  warnings.sort((a, b) => (a.severity || 3) - (b.severity || 3));

  let html = '<div class="widget-container">';

  // Header with summary
  html += '<div class="widget-header">';
  html += '<h1 class="widget-title">Flood Warnings</h1>';

  const severe = warnings.filter(w => w.severity === 1).length;
  const warning = warnings.filter(w => w.severity === 2).length;
  const alert = warnings.filter(w => w.severity === 3).length;

  if (warnings.length > 0) {
    let summaryParts = [];
    if (severe > 0) summaryParts.push('<span style="color:#ef4444">' + severe + ' severe</span>');
    if (warning > 0) summaryParts.push('<span style="color:#f59e0b">' + warning + ' warning' + (warning !== 1 ? 's' : '') + '</span>');
    if (alert > 0) summaryParts.push('<span style="color:#eab308">' + alert + ' alert' + (alert !== 1 ? 's' : '') + '</span>');
    html += '<p class="widget-subtitle">' + summaryParts.join(" | ") + '</p>';
  } else {
    html += '<p class="widget-subtitle">No active warnings</p>';
  }
  html += '</div>';

  // Warning cards
  if (warnings.length > 0) {
    warnings.forEach(w => {
      const sev = getSeverityInfo(w.severity);

      html += '<div class="status-card ' + sev.cardClass + '">';
      html += '<div class="status-header">';
      html += '<div class="severity-indicator">';
      html += '<div class="severity-icon ' + sev.class + '">' + sev.icon + '</div>';
      html += '<div>';
      html += '<div class="status-name">' + escapeHtml(w.area || "Unknown area") + '</div>';
      html += '<div style="font-size:11px;color:#666">' + escapeHtml(sev.label) + '</div>';
      html += '</div>';
      html += '</div>';
      if (w.time_raised) {
        html += '<span style="font-size:11px;color:#666">' + formatTimeAgo(w.time_raised) + '</span>';
      }
      html += '</div>';

      if (w.description) {
        html += '<div class="status-reason">' + escapeHtml(w.description) + '</div>';
      }

      if (w.message) {
        const msgText = w.message.substring(0, 200) + (w.message.length > 200 ? "..." : "");
        html += '<div style="font-size:12px;color:#777;margin-top:8px;padding-top:8px;border-top:1px solid #333">' + escapeHtml(msgText) + '</div>';
      }

      html += '</div>';
    });
  }

  html += '<div class="widget-footer">';
  html += '<span>' + escapeHtml(data.data_source || "Environment Agency") + '</span>';
  if (data.retrieved_at) {
    html += '<span>Updated ' + formatTime(data.retrieved_at) + '</span>';
  }
  html += '</div>';
  html += '</div>';

  app.innerHTML = html;
}
</script>
''',
    "mp-info": '''
<div id="app"><div class="loading"><span class="loading-dot"></span><span class="loading-dot"></span><span class="loading-dot"></span></div></div>
<script>
// UK Political party colors
const PARTY_COLORS = {
  "Conservative": { bg: "rgba(0, 135, 220, 0.15)", color: "#0087DC", text: "#5BC0F5" },
  "Labour": { bg: "rgba(228, 0, 59, 0.15)", color: "#E4003B", text: "#FF6B8A" },
  "Liberal Democrat": { bg: "rgba(250, 166, 26, 0.15)", color: "#FAA61A", text: "#FFC04D" },
  "Liberal Democrats": { bg: "rgba(250, 166, 26, 0.15)", color: "#FAA61A", text: "#FFC04D" },
  "Scottish National Party": { bg: "rgba(255, 249, 93, 0.15)", color: "#FFF95D", text: "#FFF95D" },
  "SNP": { bg: "rgba(255, 249, 93, 0.15)", color: "#FFF95D", text: "#FFF95D" },
  "Green Party": { bg: "rgba(106, 176, 35, 0.15)", color: "#6AB023", text: "#8FD94D" },
  "Green": { bg: "rgba(106, 176, 35, 0.15)", color: "#6AB023", text: "#8FD94D" },
  "Plaid Cymru": { bg: "rgba(0, 129, 66, 0.15)", color: "#008142", text: "#4DBA7D" },
  "Democratic Unionist Party": { bg: "rgba(212, 58, 58, 0.15)", color: "#D43A3A", text: "#F07070" },
  "DUP": { bg: "rgba(212, 58, 58, 0.15)", color: "#D43A3A", text: "#F07070" },
  "Sinn Fein": { bg: "rgba(50, 100, 50, 0.15)", color: "#326432", text: "#5DAD5D" },
  "Sinn Féin": { bg: "rgba(50, 100, 50, 0.15)", color: "#326432", text: "#5DAD5D" },
  "Alliance": { bg: "rgba(242, 183, 5, 0.15)", color: "#F2B705", text: "#FFD54D" },
  "SDLP": { bg: "rgba(45, 115, 71, 0.15)", color: "#2D7347", text: "#5DAD7D" },
  "UUP": { bg: "rgba(72, 166, 227, 0.15)", color: "#48A6E3", text: "#7FC4F0" },
  "Reform UK": { bg: "rgba(18, 178, 199, 0.15)", color: "#12B2C7", text: "#4DD4E8" },
  "Independent": { bg: "rgba(128, 128, 128, 0.15)", color: "#808080", text: "#A0A0A0" },
  "Speaker": { bg: "rgba(128, 128, 128, 0.15)", color: "#808080", text: "#A0A0A0" }
};

function getPartyStyle(party) {
  const p = PARTY_COLORS[party] || PARTY_COLORS["Independent"];
  return p;
}

window.render = function(data) {
  const app = document.getElementById("app");

  if (!data || data.error) {
    app.innerHTML = '<div class="error-state">' + escapeHtml(data?.error || "Unable to load MP data") + '</div>';
    return;
  }

  let html = '<div class="widget-container">';

  // Multiple MPs result
  if (data.mps && data.mps.length > 0) {
    html += '<div class="widget-header">';
    html += '<h1 class="widget-title">Members of Parliament</h1>';
    html += '<p class="widget-subtitle">' + data.mps.length + ' MP' + (data.mps.length !== 1 ? 's' : '') + ' found</p>';
    html += '</div>';

    data.mps.forEach(mp => {
      const party = getPartyStyle(mp.party);

      html += '<div class="mp-list-item">';

      // Thumbnail with fallback to initial on load error
      const mpInitial = mp.name ? escapeHtml(mp.name.charAt(0)) : "?";
      const mpFallback = '<div class="mp-thumb" style="display:flex;align-items:center;justify-content:center;font-size:18px;color:#666">' + mpInitial + '</div>';
      if (mp.thumbnail_url) {
        html += '<img class="mp-thumb" src="' + escapeHtml(mp.thumbnail_url) + '" alt="" onerror="this.outerHTML=this.dataset.fallback" data-fallback="' + mpFallback.replace(/"/g, '&quot;') + '">';
      } else {
        html += mpFallback;
      }

      html += '<div class="mp-details">';
      html += '<div class="mp-name">' + escapeHtml(mp.name) + '</div>';
      html += '<div class="mp-constituency">' + escapeHtml(mp.constituency) + '</div>';
      html += '</div>';

      html += '<span class="mp-party-badge" style="background:' + party.bg + ';color:' + party.text + '">' + escapeHtml(mp.party) + '</span>';
      html += '</div>';
    });

    html += '<div class="widget-footer">';
    html += '<span>' + escapeHtml(data.data_source || "UK Parliament") + '</span>';
    html += '</div>';
    html += '</div>';

    app.innerHTML = html;
    return;
  }

  // Single MP result - profile card view
  const party = getPartyStyle(data.party);

  html += '<div class="profile-card">';

  // Avatar with fallback to initial on load error
  const initial = data.name ? escapeHtml(data.name.charAt(0)) : "?";
  const fallbackAvatar = '<div class="profile-avatar" style="display:flex;align-items:center;justify-content:center;font-size:28px;color:#666">' + initial + '</div>';
  if (data.thumbnail_url) {
    html += '<img class="profile-avatar" src="' + escapeHtml(data.thumbnail_url) + '" alt="" onerror="this.outerHTML=this.dataset.fallback" data-fallback="' + fallbackAvatar.replace(/"/g, '&quot;') + '">';
  } else {
    html += fallbackAvatar;
  }

  html += '<div class="profile-info">';
  html += '<h1 class="profile-name">' + escapeHtml(data.name) + '</h1>';
  html += '<span class="profile-party" style="background:' + party.bg + ';color:' + party.text + '">' + escapeHtml(data.party) + '</span>';
  html += '<div class="profile-meta">' + escapeHtml(data.constituency) + '</div>';
  html += '</div>';
  html += '</div>';

  // Additional details
  html += '<div class="widget-section" style="margin-top:20px">';
  html += '<div class="info-grid">';

  html += '<div class="info-item">';
  html += '<div class="info-label">Constituency</div>';
  html += '<div class="info-value">' + escapeHtml(data.constituency) + '</div>';
  html += '</div>';

  if (data.membership_start) {
    html += '<div class="info-item">';
    html += '<div class="info-label">MP Since</div>';
    html += '<div class="info-value">' + formatDate(data.membership_start) + '</div>';
    html += '</div>';
  }

  if (data.gender) {
    html += '<div class="info-item">';
    html += '<div class="info-label">Gender</div>';
    html += '<div class="info-value">' + escapeHtml(data.gender) + '</div>';
    html += '</div>';
  }

  html += '</div>';
  html += '</div>';

  html += '<div class="widget-footer">';
  html += '<span>' + escapeHtml(data.data_source || "UK Parliament") + '</span>';
  if (data.retrieved_at) {
    html += '<span>Updated ' + formatTime(data.retrieved_at) + '</span>';
  }
  html += '</div>';
  html += '</div>';

  app.innerHTML = html;
}
</script>
''',
    "bank-holidays": '''
<div id="app"><div class="loading"><span class="loading-dot"></span><span class="loading-dot"></span><span class="loading-dot"></span></div></div>
<script>
// Bank holidays uses a custom date format with weekday
function formatHolidayDate(dateStr) {
  if (!dateStr) return "";
  try {
    const d = new Date(dateStr);
    if (isNaN(d.getTime())) return dateStr;
    const options = { weekday: "short", day: "numeric", month: "short", year: "numeric" };
    return d.toLocaleDateString("en-GB", options);
  } catch (e) {
    return dateStr;
  }
}

function daysUntil(dateStr) {
  if (!dateStr) return null;
  const target = new Date(dateStr);
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  target.setHours(0, 0, 0, 0);
  const diffTime = target - today;
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
  return diffDays;
}

window.render = function(data) {
  const app = document.getElementById("app");

  if (!data || data.error) {
    app.innerHTML = '<div class="error-state">' + escapeHtml(data?.error || "Unable to load bank holidays") + '</div>';
    return;
  }

  let html = '<div class="widget-container">';
  html += '<div class="widget-header">';
  html += '<h1 class="widget-title">Bank Holidays</h1>';

  // Handle single country or all countries
  let holidays = [];
  let countryName = "";

  if (data.country && data.upcoming_holidays) {
    holidays = data.upcoming_holidays;
    countryName = data.country.replace(/-/g, " ").replace(/\b\w/g, l => l.toUpperCase());
    html += '<p class="widget-subtitle">' + escapeHtml(countryName) + '</p>';
  } else {
    // Show England & Wales by default
    const ew = data["england-and-wales"];
    if (ew && ew.upcoming_holidays) {
      holidays = ew.upcoming_holidays;
      countryName = "England & Wales";
      html += '<p class="widget-subtitle">' + escapeHtml(countryName) + '</p>';
    }
  }
  html += '</div>';

  if (holidays.length > 0) {
    // Next holiday highlight
    const next = holidays[0];
    const days = daysUntil(next.date);

    html += '<div class="status-card status-good" style="border-left-color:#6366f1">';
    html += '<div class="status-header">';
    html += '<div>';
    html += '<div class="status-name" style="font-size:16px">' + escapeHtml(next.title) + '</div>';
    html += '<div style="font-size:13px;color:#888;margin-top:4px">' + formatHolidayDate(next.date) + '</div>';
    html += '</div>';
    if (days !== null) {
      html += '<div style="text-align:right">';
      if (days === 0) {
        html += '<div style="font-size:20px;font-weight:600;color:#4ade80">Today!</div>';
      } else if (days === 1) {
        html += '<div style="font-size:20px;font-weight:600;color:#fbbf24">Tomorrow</div>';
      } else {
        html += '<div style="font-size:24px;font-weight:600;color:#6366f1">' + days + '</div>';
        html += '<div style="font-size:11px;color:#666">days away</div>';
      }
      html += '</div>';
    }
    html += '</div>';
    html += '</div>';

    // Upcoming holidays list
    if (holidays.length > 1) {
      html += '<div class="widget-section">';
      html += '<div class="section-title">Upcoming</div>';
      holidays.slice(1, 6).forEach(h => {
        const d = daysUntil(h.date);
        html += '<div class="status-card" style="padding:10px 14px">';
        html += '<div class="status-header">';
        html += '<span class="status-name" style="font-size:13px">' + escapeHtml(h.title) + '</span>';
        html += '<span style="font-size:12px;color:#888">' + formatHolidayDate(h.date) + '</span>';
        html += '</div>';
        html += '</div>';
      });
      html += '</div>';
    }
  } else {
    html += '<div class="empty-state"><div class="empty-text">No upcoming bank holidays</div></div>';
  }

  html += '<div class="widget-footer">';
  html += '<span>' + escapeHtml(data.data_source || "GOV.UK") + '</span>';
  if (data.retrieved_at) {
    html += '<span>Updated ' + formatTime(data.retrieved_at) + '</span>';
  }
  html += '</div>';
  html += '</div>';

  app.innerHTML = html;
}
</script>
''',
    "crime-stats": '''
<div id="app"><div class="loading"><span class="loading-dot"></span><span class="loading-dot"></span><span class="loading-dot"></span></div></div>
<script>
const CRIME_COLORS = {
  "anti-social-behaviour": "#f59e0b",
  "burglary": "#ef4444",
  "criminal-damage-arson": "#f97316",
  "drugs": "#8b5cf6",
  "other-theft": "#ec4899",
  "possession-of-weapons": "#dc2626",
  "public-order": "#eab308",
  "robbery": "#b91c1c",
  "shoplifting": "#f472b6",
  "theft-from-the-person": "#e879f9",
  "vehicle-crime": "#6366f1",
  "violent-crime": "#ef4444",
  "other-crime": "#6b7280",
  "bicycle-theft": "#14b8a6"
};

function formatCategory(cat) {
  if (!cat) return "Unknown";
  return cat.replace(/-/g, " ").replace(/\b\w/g, l => l.toUpperCase());
}

window.render = function(data) {
  const app = document.getElementById("app");

  if (data?.message && !data.crimes) {
    app.innerHTML = '<div class="widget-container"><div class="widget-header"><h1 class="widget-title">Crime Data</h1></div><div class="empty-state"><div class="empty-text">' + escapeHtml(data.message) + '</div></div></div>';
    return;
  }

  if (!data || data.error) {
    app.innerHTML = '<div class="error-state">' + escapeHtml(data?.error || "Unable to load crime data") + '</div>';
    return;
  }

  const crimes = data.crimes || [];

  // Count by category
  const counts = {};
  crimes.forEach(c => {
    const cat = c.category || "other-crime";
    counts[cat] = (counts[cat] || 0) + 1;
  });

  // Sort by count
  const sorted = Object.entries(counts).sort((a, b) => b[1] - a[1]);
  const maxCount = sorted.length > 0 ? sorted[0][1] : 1;

  let html = '<div class="widget-container">';
  html += '<div class="widget-header">';
  html += '<h1 class="widget-title">Crime Statistics</h1>';
  html += '<p class="widget-subtitle">' + escapeHtml(data.total_crimes) + ' incidents reported</p>';
  html += '</div>';

  if (sorted.length > 0) {
    html += '<div class="widget-section">';
    html += '<div class="section-title">By Category</div>';

    sorted.slice(0, 8).forEach(([cat, count]) => {
      const color = CRIME_COLORS[cat] || "#6b7280";
      const pct = Math.round((count / maxCount) * 100);

      html += '<div style="margin-bottom:12px">';
      html += '<div style="display:flex;justify-content:space-between;margin-bottom:4px">';
      html += '<span style="font-size:12px;color:#ccc">' + escapeHtml(formatCategory(cat)) + '</span>';
      html += '<span style="font-size:12px;font-weight:500;color:#fff">' + count + '</span>';
      html += '</div>';
      html += '<div class="score-bar"><div class="score-fill" style="width:' + pct + '%;background:' + color + '"></div></div>';
      html += '</div>';
    });

    html += '</div>';
  }

  html += '<div class="widget-footer">';
  html += '<span>' + escapeHtml(data.data_source || "Police.uk") + '</span>';
  if (data.retrieved_at) {
    html += '<span>Updated ' + formatTime(data.retrieved_at) + '</span>';
  }
  html += '</div>';
  html += '</div>';

  app.innerHTML = html;
}
</script>
''',
    "cqc-rating": '''
<div id="app"><div class="loading"><span class="loading-dot"></span><span class="loading-dot"></span><span class="loading-dot"></span></div></div>
<script>
const RATING_STYLES = {
  "Outstanding": { bg: "rgba(34, 197, 94, 0.15)", color: "#4ade80", icon: "★★" },
  "Good": { bg: "rgba(34, 197, 94, 0.15)", color: "#4ade80", icon: "★" },
  "Requires improvement": { bg: "rgba(245, 158, 11, 0.15)", color: "#fbbf24", icon: "!" },
  "Inadequate": { bg: "rgba(239, 68, 68, 0.15)", color: "#f87171", icon: "✗" }
};

function getRatingStyle(rating) {
  return RATING_STYLES[rating] || { bg: "rgba(100,100,100,0.15)", color: "#888", icon: "?" };
}

window.render = function(data) {
  const app = document.getElementById("app");

  if (!data || data.error) {
    app.innerHTML = '<div class="error-state">' + escapeHtml(data?.error || "Unable to load CQC data") + '</div>';
    return;
  }

  const overall = getRatingStyle(data.overall_rating);

  let html = '<div class="widget-container">';

  // Header with overall rating
  html += '<div class="widget-header" style="margin-bottom:20px">';
  html += '<div style="display:flex;justify-content:space-between;align-items:flex-start;gap:12px">';
  html += '<div style="flex:1">';
  html += '<h1 class="widget-title">' + escapeHtml(data.name) + '</h1>';
  html += '<p class="widget-subtitle">' + escapeHtml(data.type || "Care Provider") + '</p>';
  html += '</div>';
  html += '<div style="text-align:center;padding:12px 16px;border-radius:8px;background:' + overall.bg + '">';
  html += '<div style="font-size:20px">' + overall.icon + '</div>';
  html += '<div style="font-size:12px;font-weight:600;color:' + overall.color + '">' + escapeHtml(data.overall_rating || "Not Rated") + '</div>';
  html += '</div>';
  html += '</div>';
  html += '</div>';

  // Rating breakdown
  if (data.ratings) {
    html += '<div class="widget-section">';
    html += '<div class="section-title">Rating Breakdown</div>';

    const categories = [
      { key: "safe", label: "Safe" },
      { key: "effective", label: "Effective" },
      { key: "caring", label: "Caring" },
      { key: "responsive", label: "Responsive" },
      { key: "well_led", label: "Well-led" }
    ];

    categories.forEach(cat => {
      const rating = data.ratings[cat.key];
      const style = getRatingStyle(rating);

      html += '<div style="display:flex;align-items:center;justify-content:space-between;padding:8px 0;border-bottom:1px solid #333">';
      html += '<span style="font-size:13px;color:#ccc">' + cat.label + '</span>';
      html += '<span style="font-size:12px;font-weight:500;padding:4px 10px;border-radius:12px;background:' + style.bg + ';color:' + style.color + '">' + escapeHtml(rating || "N/A") + '</span>';
      html += '</div>';
    });

    html += '</div>';
  }

  // Inspection date
  if (data.inspection_date) {
    html += '<div class="info-item" style="margin-top:12px">';
    html += '<div class="info-label">Last Inspection</div>';
    html += '<div class="info-value info-value-sm">' + formatDate(data.inspection_date) + '</div>';
    html += '</div>';
  }

  html += '<div class="widget-footer">';
  html += '<span>' + escapeHtml(data.data_source || "Care Quality Commission") + '</span>';
  if (data.retrieved_at) {
    html += '<span>Updated ' + formatTime(data.retrieved_at) + '</span>';
  }
  html += '</div>';
  html += '</div>';

  app.innerHTML = html;
}
</script>
''',
    "charity-info": '''
<div id="app"><div class="loading"><span class="loading-dot"></span><span class="loading-dot"></span><span class="loading-dot"></span></div></div>
<script>
function getStatusStyle(status) {
  if (!status) return { bg: "rgba(100,100,100,0.15)", color: "#888" };
  const s = status.toLowerCase();
  if (s.includes("registered") || s.includes("active")) {
    return { bg: "rgba(34, 197, 94, 0.15)", color: "#4ade80" };
  }
  if (s.includes("removed")) {
    return { bg: "rgba(239, 68, 68, 0.15)", color: "#f87171" };
  }
  return { bg: "rgba(245, 158, 11, 0.15)", color: "#fbbf24" };
}

window.render = function(data) {
  const app = document.getElementById("app");

  if (!data || data.error) {
    app.innerHTML = '<div class="error-state">' + escapeHtml(data?.error || "Unable to load charity data") + '</div>';
    return;
  }

  const statusStyle = getStatusStyle(data.registration_status);

  let html = '<div class="widget-container">';

  // Header
  html += '<div class="widget-header" style="margin-bottom:20px">';
  html += '<div style="display:flex;justify-content:space-between;align-items:flex-start;gap:12px">';
  html += '<div style="flex:1">';
  html += '<h1 class="widget-title">' + escapeHtml(data.charity_name || "Unknown Charity") + '</h1>';
  html += '<p class="widget-subtitle" style="font-family:monospace">No. ' + escapeHtml(data.charity_number || "N/A") + '</p>';
  html += '</div>';
  if (data.registration_status) {
    html += '<span class="company-status" style="background:' + statusStyle.bg + ';color:' + statusStyle.color + '">' + escapeHtml(data.registration_status) + '</span>';
  }
  html += '</div>';
  html += '</div>';

  // Details grid
  html += '<div class="widget-section">';
  html += '<div class="info-grid">';

  if (data.charity_type) {
    html += '<div class="info-item">';
    html += '<div class="info-label">Type</div>';
    html += '<div class="info-value info-value-sm">' + escapeHtml(data.charity_type) + '</div>';
    html += '</div>';
  }

  if (data.registration_date) {
    html += '<div class="info-item">';
    html += '<div class="info-label">Registered</div>';
    html += '<div class="info-value">' + formatDate(data.registration_date) + '</div>';
    html += '</div>';
  }

  if (data.removal_date) {
    html += '<div class="info-item">';
    html += '<div class="info-label">Removed</div>';
    html += '<div class="info-value">' + formatDate(data.removal_date) + '</div>';
    html += '</div>';
  }

  html += '</div>';
  html += '</div>';

  // Activities
  if (data.activities) {
    html += '<div class="widget-section">';
    html += '<div class="section-title">Activities</div>';
    const activitiesText = data.activities.substring(0, 300) + (data.activities.length > 300 ? "..." : "");
    html += '<div style="font-size:13px;color:#ccc;line-height:1.5;background:#2a2a2a;padding:12px;border-radius:8px">' + escapeHtml(activitiesText) + '</div>';
    html += '</div>';
  }

  html += '<div class="widget-footer">';
  html += '<span>' + escapeHtml(data.data_source || "Charity Commission") + '</span>';
  if (data.retrieved_at) {
    html += '<span>Updated ' + formatTime(data.retrieved_at) + '</span>';
  }
  html += '</div>';
  html += '</div>';

  app.innerHTML = html;
}
</script>
''',
    "voting-record": '''
<div id="app"><div class="loading"><span class="loading-dot"></span><span class="loading-dot"></span><span class="loading-dot"></span></div></div>
<script>
window.render = function(data) {
  const app = document.getElementById("app");

  if (data?.message && !data.votes) {
    app.innerHTML = '<div class="widget-container"><div class="widget-header"><h1 class="widget-title">Voting Record</h1></div><div class="empty-state"><div class="empty-text">' + escapeHtml(data.message) + '</div></div></div>';
    return;
  }

  if (!data || data.error) {
    let errorHtml = '<div class="error-state">' + escapeHtml(data?.error || "Unable to load voting data") + '</div>';
    if (data?.raw) {
      errorHtml += '<div style="margin-top:10px;padding:10px;background:#1a1a1a;font-size:10px;color:#888;max-height:200px;overflow:auto;word-break:break-all"><strong>Raw:</strong> ' + escapeHtml(data.raw) + '</div>';
    }
    app.innerHTML = errorHtml;
    return;
  }

  let html = '<div class="widget-container">';
  html += '<div class="widget-header">';
  html += '<h1 class="widget-title">Voting Record</h1>';
  html += '<p class="widget-subtitle">' + escapeHtml(data.total_votes || 0) + ' recent votes</p>';
  html += '</div>';

  const votes = data.votes || [];

  if (votes.length > 0) {
    votes.slice(0, 10).forEach(v => {
      const isAye = v.vote === "ayes" || v.vote === "aye";
      const voteColor = isAye ? "#4ade80" : "#f87171";
      const voteBg = isAye ? "rgba(34, 197, 94, 0.15)" : "rgba(239, 68, 68, 0.15)";
      const voteText = isAye ? "AYE" : "NO";

      const totalVotes = (v.ayes_count || 0) + (v.noes_count || 0);
      const ayePct = totalVotes > 0 ? Math.round((v.ayes_count / totalVotes) * 100) : 50;

      html += '<div class="status-card" style="border-left:none">';
      html += '<div style="display:flex;justify-content:space-between;align-items:flex-start;gap:10px;margin-bottom:8px">';
      html += '<div style="flex:1;min-width:0">';
      const titleText = (v.title || "Unknown Division").substring(0, 80);
      html += '<div style="font-size:13px;color:#fff;font-weight:500;margin-bottom:4px">' + escapeHtml(titleText) + '</div>';
      html += '<div style="font-size:11px;color:#666">' + formatDate(v.date) + '</div>';
      html += '</div>';
      html += '<span style="font-size:11px;font-weight:600;padding:4px 10px;border-radius:12px;background:' + voteBg + ';color:' + voteColor + ';flex-shrink:0">' + voteText + '</span>';
      html += '</div>';

      // Vote bar
      html += '<div style="display:flex;align-items:center;gap:8px;font-size:10px">';
      html += '<span style="color:#4ade80">' + (v.ayes_count || 0) + '</span>';
      html += '<div style="flex:1;height:6px;background:#333;border-radius:3px;overflow:hidden;display:flex">';
      html += '<div style="width:' + ayePct + '%;background:#4ade80"></div>';
      html += '<div style="width:' + (100 - ayePct) + '%;background:#f87171"></div>';
      html += '</div>';
      html += '<span style="color:#f87171">' + (v.noes_count || 0) + '</span>';
      html += '</div>';

      html += '</div>';
    });
  }

  html += '<div class="widget-footer">';
  html += '<span>' + escapeHtml(data.data_source || "Commons Votes") + '</span>';
  if (data.retrieved_at) {
    html += '<span>Updated ' + formatTime(data.retrieved_at) + '</span>';
  }
  html += '</div>';
  html += '</div>';

  app.innerHTML = html;
}
</script>
''',
    "bike-points": '''
<div id="app"><div class="loading"><span class="loading-dot"></span><span class="loading-dot"></span><span class="loading-dot"></span></div></div>
<script>
window.render = function(data) {
  const app = document.getElementById("app");

  if (!data || data.error) {
    let errorHtml = '<div class="error-state">' + escapeHtml(data?.error || "Unable to load bike points") + '</div>';
    if (data?.raw) {
      errorHtml += '<div style="margin-top:10px;padding:10px;background:#1a1a1a;font-size:10px;color:#888;max-height:200px;overflow:auto;word-break:break-all"><strong>Raw:</strong> ' + escapeHtml(data.raw) + '</div>';
    }
    app.innerHTML = errorHtml;
    return;
  }

  const points = data.bike_points || [];

  let html = '<div class="widget-container">';
  html += '<div class="widget-header">';
  html += '<h1 class="widget-title">Santander Cycles</h1>';
  html += '<p class="widget-subtitle">' + escapeHtml(data.total_results) + ' docking stations</p>';
  html += '</div>';

  if (points.length > 0) {
    points.slice(0, 8).forEach(p => {
      const bikes = parseInt(p.bikes_available, 10) || 0;
      const empty = parseInt(p.empty_docks, 10) || 0;
      const total = parseInt(p.total_docks, 10) || (bikes + empty);
      const bikePct = total > 0 ? Math.round((bikes / total) * 100) : 0;

      const availColor = bikes > 5 ? "#4ade80" : bikes > 0 ? "#fbbf24" : "#f87171";

      html += '<div class="status-card" style="border-left-color:' + availColor + '">';
      html += '<div class="status-header">';
      html += '<div style="flex:1;min-width:0">';
      const stationName = (p.name || "Unknown Station").replace("Santander Cycles:", "").trim();
      html += '<div class="status-name" style="font-size:13px">' + escapeHtml(stationName) + '</div>';
      html += '</div>';
      html += '<div style="text-align:right">';
      html += '<div style="font-size:18px;font-weight:600;color:' + availColor + '">' + bikes + '</div>';
      html += '<div style="font-size:10px;color:#666">bikes</div>';
      html += '</div>';
      html += '</div>';

      // Availability bar
      html += '<div style="margin-top:8px">';
      html += '<div style="display:flex;justify-content:space-between;font-size:10px;color:#666;margin-bottom:4px">';
      html += '<span>Bikes: ' + bikes + '</span>';
      html += '<span>Empty: ' + empty + '</span>';
      html += '</div>';
      html += '<div class="score-bar"><div class="score-fill" style="width:' + bikePct + '%;background:linear-gradient(90deg, #ef4444, #fbbf24, #4ade80)"></div></div>';
      html += '</div>';

      html += '</div>';
    });
  } else {
    html += '<div class="empty-state"><div class="empty-text">No bike points found</div></div>';
  }

  html += '<div class="widget-footer">';
  html += '<span>' + escapeHtml(data.data_source || "Transport for London") + '</span>';
  if (data.retrieved_at) {
    html += '<span>Updated ' + formatTime(data.retrieved_at) + '</span>';
  }
  html += '</div>';
  html += '</div>';

  app.innerHTML = html;
}
</script>
''',
    "journey-planner": '''
<div id="app"><div class="loading"><span class="loading-dot"></span><span class="loading-dot"></span><span class="loading-dot"></span></div></div>
<script>
const MODE_ICONS = {
  "tube": "🚇",
  "bus": "🚌",
  "walking": "🚶",
  "overground": "🚆",
  "dlr": "🚈",
  "elizabeth-line": "🚇",
  "national-rail": "🚂",
  "tram": "🚊",
  "river-bus": "⛴️",
  "cable-car": "🚡"
};

const MODE_COLORS = {
  "tube": "#0019A8",
  "bus": "#E32017",
  "walking": "#666",
  "overground": "#EE7C0E",
  "dlr": "#00A4A7",
  "elizabeth-line": "#6950a1",
  "national-rail": "#333",
  "tram": "#84B817"
};

window.render = function(data) {
  const app = document.getElementById("app");

  if (!data || data.error) {
    app.innerHTML = '<div class="error-state">' + escapeHtml(data?.error || "Unable to plan journey") + '</div>';
    return;
  }

  const journeys = data.journey_options || [];

  let html = '<div class="widget-container">';
  html += '<div class="widget-header">';
  html += '<h1 class="widget-title">Journey Planner</h1>';
  html += '<p class="widget-subtitle">' + escapeHtml(data.from || "?") + ' → ' + escapeHtml(data.to || "?") + '</p>';
  html += '</div>';

  if (journeys.length > 0) {
    journeys.slice(0, 3).forEach((j, idx) => {
      const legs = j.legs || [];

      html += '<div class="status-card" style="border-left-color:#0019A8">';

      // Journey header
      html += '<div class="status-header" style="margin-bottom:10px">';
      html += '<div>';
      html += '<div style="font-size:11px;color:#666">Option ' + (idx + 1) + '</div>';
      html += '<div style="font-size:15px;font-weight:600;color:#fff">' + escapeHtml(j.duration) + ' mins</div>';
      html += '</div>';
      html += '<div style="text-align:right;font-size:12px;color:#888">';
      html += formatTime(j.start_time) + ' → ' + formatTime(j.arrival_time);
      html += '</div>';
      html += '</div>';

      // Journey legs
      html += '<div style="border-left:2px solid #333;margin-left:8px;padding-left:16px">';
      legs.forEach((leg, legIdx) => {
        const mode = (leg.mode || "walking").toLowerCase();
        const icon = MODE_ICONS[mode] || "•";
        const color = MODE_COLORS[mode] || "#666";

        html += '<div style="position:relative;padding:8px 0;' + (legIdx < legs.length - 1 ? 'border-bottom:1px dashed #333;' : '') + '">';
        html += '<div style="position:absolute;left:-24px;top:8px;width:16px;height:16px;background:#1a1a1a;border:2px solid ' + color + ';border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:8px">' + icon + '</div>';
        html += '<div style="display:flex;justify-content:space-between;align-items:center">';
        html += '<div>';
        html += '<div style="font-size:12px;color:#fff">' + escapeHtml(leg.departure_point || "Start") + '</div>';
        if (leg.instruction) {
          html += '<div style="font-size:11px;color:#888;margin-top:2px">' + escapeHtml(leg.instruction) + '</div>';
        }
        html += '</div>';
        html += '<span style="font-size:11px;color:#888">' + (leg.duration || 0) + ' min</span>';
        html += '</div>';
        html += '</div>';
      });
      html += '</div>';

      html += '</div>';
    });
  } else {
    html += '<div class="empty-state"><div class="empty-text">No routes found</div></div>';
  }

  html += '<div class="widget-footer">';
  html += '<span>' + escapeHtml(data.data_source || "Transport for London") + '</span>';
  if (data.retrieved_at) {
    html += '<span>Updated ' + formatTime(data.retrieved_at) + '</span>';
  }
  html += '</div>';
  html += '</div>';

  app.innerHTML = html;
}
</script>
''',
    "road-status": '''
<div id="app"><div class="loading"><span class="loading-dot"></span><span class="loading-dot"></span><span class="loading-dot"></span></div></div>
<script>
function getStatusStyle(severity) {
  const s = (severity || "").toLowerCase();
  if (s.includes("good") || s.includes("no")) {
    return { class: "status-good", badge: "badge-good", color: "#4ade80" };
  }
  if (s.includes("minor") || s.includes("moderate")) {
    return { class: "status-warning", badge: "badge-warning", color: "#fbbf24" };
  }
  if (s.includes("serious") || s.includes("severe")) {
    return { class: "status-error", badge: "badge-error", color: "#f87171" };
  }
  return { class: "", badge: "", color: "#888" };
}

window.render = function(data) {
  const app = document.getElementById("app");

  if (!data || data.error) {
    app.innerHTML = '<div class="error-state">' + escapeHtml(data?.error || "Unable to load road status") + '</div>';
    return;
  }

  const roads = data.roads || [];

  let html = '<div class="widget-container">';
  html += '<div class="widget-header">';
  html += '<h1 class="widget-title">Road Status</h1>';
  html += '<p class="widget-subtitle">' + roads.length + ' road' + (roads.length !== 1 ? 's' : '') + '</p>';
  html += '</div>';

  if (roads.length > 0) {
    roads.forEach(r => {
      const style = getStatusStyle(r.status_description);

      html += '<div class="status-card ' + style.class + '">';
      html += '<div class="status-header">';
      html += '<div>';
      html += '<div class="status-name">' + escapeHtml(r.display_name || r.id) + '</div>';
      html += '</div>';
      html += '<span class="status-badge ' + style.badge + '">' + escapeHtml(r.status_description || "Unknown") + '</span>';
      html += '</div>';
      html += '</div>';
    });
  } else {
    html += '<div class="empty-state"><div class="empty-text">No road data available</div></div>';
  }

  html += '<div class="widget-footer">';
  html += '<span>' + escapeHtml(data.data_source || "Transport for London") + '</span>';
  if (data.retrieved_at) {
    html += '<span>Updated ' + formatTime(data.retrieved_at) + '</span>';
  }
  html += '</div>';
  html += '</div>';

  app.innerHTML = html;
}
</script>
''',
    "nhs-services": '''
<div id="app"><div class="loading"><span class="loading-dot"></span><span class="loading-dot"></span><span class="loading-dot"></span></div></div>
<script>
function formatDistance(d) {
  if (!d && d !== 0) return "";
  const km = parseFloat(d);
  if (km < 1) {
    return Math.round(km * 1000) + "m";
  }
  return km.toFixed(1) + "km";
}

window.render = function(data) {
  const app = document.getElementById("app");

  if (!data || data.error) {
    app.innerHTML = '<div class="error-state">' + escapeHtml(data?.error || "Unable to load NHS services") + '</div>';
    return;
  }

  // Find the services array (could be services, hospitals, pharmacies)
  let services = data.services || data.hospitals || data.pharmacies || [];
  let serviceType = "Services";
  if (data.hospitals) serviceType = "Hospitals";
  if (data.pharmacies) serviceType = "Pharmacies";
  if (data.services) serviceType = "GP Surgeries";

  let html = '<div class="widget-container">';
  html += '<div class="widget-header">';
  html += '<h1 class="widget-title">NHS ' + escapeHtml(serviceType) + '</h1>';
  html += '<p class="widget-subtitle">Near ' + escapeHtml(data.search_postcode || "your location") + '</p>';
  html += '</div>';

  if (services.length > 0) {
    services.slice(0, 8).forEach(s => {
      html += '<div class="status-card" style="border-left-color:#005EB8">';
      html += '<div class="status-header">';
      html += '<div style="flex:1;min-width:0">';
      html += '<div class="status-name" style="font-size:13px">' + escapeHtml(s.name || "Unknown") + '</div>';
      const addressParts = [s.address, s.city, s.postcode].filter(Boolean).map(p => escapeHtml(p));
      if (addressParts.length > 0) {
        html += '<div style="font-size:11px;color:#888;margin-top:4px">' + addressParts.join(", ") + '</div>';
      }
      html += '</div>';
      if (s.distance !== undefined && s.distance !== null) {
        html += '<div style="text-align:right;flex-shrink:0">';
        html += '<div style="font-size:14px;font-weight:600;color:#005EB8">' + formatDistance(s.distance) + '</div>';
        html += '</div>';
      }
      html += '</div>';

      if (s.phone) {
        html += '<div style="margin-top:8px;font-size:12px">';
        html += '<span style="color:#666">Tel:</span> <span style="color:#4ade80">' + escapeHtml(s.phone) + '</span>';
        html += '</div>';
      }

      html += '</div>';
    });
  } else {
    html += '<div class="empty-state"><div class="empty-text">No services found nearby</div></div>';
  }

  html += '<div class="widget-footer">';
  html += '<span>' + escapeHtml(data.data_source || "NHS") + '</span>';
  if (data.retrieved_at) {
    html += '<span>Updated ' + formatTime(data.retrieved_at) + '</span>';
  }
  html += '</div>';
  html += '</div>';

  app.innerHTML = html;
}
</script>
'''
}

def _get_widget_html(widget_name: str) -> str:
    """Generate MCP Apps compliant widget HTML."""
    widget_content = WIDGETS.get(widget_name, '<div id="app">Widget not found</div><script>function render(){}</script>')

    return f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <style>{WIDGET_STYLES}</style>
  <script>
    // Utility functions - defined in head so they're available to all widget scripts

    // Debug logging (console only)
    const debug = (msg) => console.log('[MCP Widget]', msg);

    // HTML escaping to prevent XSS - use for ALL user/API data inserted into HTML
    const escapeHtml = (str) => {{
      if (str === null || str === undefined) return '';
      return String(str).replace(/[&<>"']/g, c => ({{
        '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
      }})[c]);
    }};

    // Shared date formatting utility
    const formatDate = (dateStr) => {{
      if (!dateStr) return '';
      try {{
        const d = new Date(dateStr);
        if (isNaN(d.getTime())) return dateStr;
        return d.toLocaleDateString('en-GB', {{ day: 'numeric', month: 'short', year: 'numeric' }});
      }} catch (e) {{
        return dateStr;
      }}
    }};

    // Format time from ISO string
    const formatTime = (dateStr) => {{
      if (!dateStr) return '';
      try {{
        const d = new Date(dateStr);
        if (isNaN(d.getTime())) return '';
        return d.toLocaleTimeString('en-GB', {{ hour: '2-digit', minute: '2-digit' }});
      }} catch (e) {{
        return '';
      }}
    }};
  </script>
</head>
<body>
  {widget_content}
  <script>
    let requestId = 1;
    const pendingRequests = new Map();

    // Security: Store trusted parent origin from first message
    let trustedOrigin = null;

    // Send JSON-RPC 2.0 request to host
    function sendRequest(method, params) {{
      const id = requestId++;
      debug('Sending request: ' + method + ' (id=' + id + ')');
      // Use stored trusted origin if available, otherwise fall back to '*' for initial setup
      const targetOrigin = trustedOrigin || '*';
      window.parent.postMessage({{
        jsonrpc: '2.0',
        id: id,
        method: method,
        params: params || {{}}
      }}, targetOrigin);
      return new Promise((resolve, reject) => {{
        pendingRequests.set(id, {{ resolve, reject }});
        // Timeout after 10s
        setTimeout(() => {{
          if (pendingRequests.has(id)) {{
            pendingRequests.delete(id);
            reject(new Error('Request timeout'));
          }}
        }}, 10000);
      }});
    }}

    // Send JSON-RPC 2.0 notification to host
    function sendNotification(method, params) {{
      debug('Sending notification: ' + method);
      const targetOrigin = trustedOrigin || '*';
      window.parent.postMessage({{
        jsonrpc: '2.0',
        method: method,
        params: params || {{}}
      }}, targetOrigin);
    }}

    // Listen for messages from host
    window.addEventListener('message', (event) => {{
      const data = event.data;
      if (!data) return;

      // Security: Store origin from first valid JSON-RPC message as trusted
      if (!trustedOrigin && data.jsonrpc === '2.0' && event.origin) {{
        trustedOrigin = event.origin;
        debug('Trusted origin set: ' + trustedOrigin);
      }}

      // Security: Validate origin for subsequent messages (if we have a trusted origin)
      if (trustedOrigin && event.origin !== trustedOrigin) {{
        debug('Ignoring message from untrusted origin: ' + event.origin);
        return;
      }}

      // Log messages for debugging
      debug('MSG: ' + JSON.stringify(data).substring(0, 200));

      // Handle JSON-RPC 2.0 responses (to our requests)
      if (data.jsonrpc === '2.0' && data.id !== undefined) {{
        const pending = pendingRequests.get(data.id);
        if (pending) {{
          pendingRequests.delete(data.id);
          if (data.error) {{
            pending.reject(new Error(data.error.message || JSON.stringify(data.error)));
          }} else {{
            debug('Response received for id=' + data.id);
            pending.resolve(data.result);
          }}
        }}
        return;
      }}

      // Handle JSON-RPC 2.0 notifications from host
      if (data.jsonrpc === '2.0' && data.method) {{
        // Tool input notification - sent after initialized, contains tool arguments
        if (data.method === 'ui/notifications/tool-input') {{
          debug('Tool input received: ' + JSON.stringify(data.params || {{}}).substring(0, 100));
          return;
        }}

        // Tool result notification - contains the actual tool output
        if (data.method === 'ui/notifications/tool-result') {{
          debug('Tool result received!');
          const params = data.params || {{}};
          debug('Result params: ' + JSON.stringify(params).substring(0, 300));

          let toolData = null;

          // Try structuredContent first (preferred for widgets)
          if (params.structuredContent) {{
            debug('Using structuredContent');
            toolData = params.structuredContent;
          }}
          // If content array, try to parse text content
          else if (params.content && Array.isArray(params.content)) {{
            const textItem = params.content.find(c => c.type === 'text');
            if (textItem?.text) {{
              debug('Parsing content text: ' + textItem.text.substring(0, 100));
              try {{
                toolData = JSON.parse(textItem.text);
              }} catch(e) {{
                debug('JSON parse error: ' + e.message);
                debug('Raw text starts with: ' + textItem.text.substring(0, 300));
                // Include more debug info in error for troubleshooting
                toolData = {{
                  error: 'Failed to parse response: ' + e.message,
                  raw: textItem.text.substring(0, 500),
                  parseError: e.message
                }};
              }}
            }}
          }}

          if (!toolData) {{
            debug('No data found in params');
            toolData = params;
          }}

          // Call render with error handling
          try {{
            debug('Calling render with: ' + JSON.stringify(toolData).substring(0, 150));
            if (typeof render === 'function') {{
              render(toolData);
            }} else if (typeof window.render === 'function') {{
              window.render(toolData);
            }} else {{
              debug('render function not found, trying to dispatch event');
              window.dispatchEvent(new CustomEvent('mcp-data', {{ detail: toolData }}));
            }}
          }} catch(e) {{
            debug('Render error: ' + e.message + ' - ' + e.stack);
            document.getElementById('app').innerHTML = '<div class="error-state">Render error: ' + e.message + '</div>';
          }}
          return;
        }}
      }}

      // Legacy/fallback message formats
      if (data.type === 'ui/tool-result' || data.toolOutput) {{
        debug('Legacy format received');
        render(data.toolOutput || data.result || data.data || data);
        return;
      }}
    }});

    debug('Widget loaded');

    // Initialize using MCP Apps protocol
    // MCPJam expects appInfo, appCapabilities, and protocolVersion params
    sendRequest('ui/initialize', {{
      protocolVersion: '2025-06-18',
      appInfo: {{ name: 'gov-uk-widget', version: '1.0.0' }},
      appCapabilities: {{}}
    }}).then(result => {{
      debug('Initialize OK');

      // CRITICAL: Send ui/notifications/initialized to signal we're ready for data
      // Host waits for this before sending tool-input and tool-result
      debug('Sending ui/notifications/initialized');
      sendNotification('ui/notifications/initialized', {{}});

    }}).catch(err => {{
      debug('Initialize error: ' + err.message);
    }});
  </script>
</body>
</html>'''


# MCP Apps MIME type for UI widgets (SEP-1865)
MCP_APPS_MIME = "text/html;profile=mcp-app"


@mcp.resource("ui://tube-status", mime_type=MCP_APPS_MIME)
def tube_status_widget() -> str:
    """Tube status visualization widget showing London Underground line status."""
    return _get_widget_html("tube-status")


@mcp.resource("ui://postcode-lookup", mime_type=MCP_APPS_MIME)
def postcode_lookup_widget() -> str:
    """Postcode lookup widget with map and location details."""
    return _get_widget_html("postcode-lookup")


@mcp.resource("ui://company-info", mime_type=MCP_APPS_MIME)
def company_info_widget() -> str:
    """Company information widget showing Companies House data."""
    return _get_widget_html("company-info")


@mcp.resource("ui://food-hygiene", mime_type=MCP_APPS_MIME)
def food_hygiene_widget() -> str:
    """Food hygiene ratings widget showing FSA ratings."""
    return _get_widget_html("food-hygiene")


@mcp.resource("ui://flood-warnings", mime_type=MCP_APPS_MIME)
def flood_warnings_widget() -> str:
    """Flood warnings widget showing Environment Agency alerts."""
    return _get_widget_html("flood-warnings")


@mcp.resource("ui://mp-info", mime_type=MCP_APPS_MIME)
def mp_info_widget() -> str:
    """MP information widget showing Parliament member details."""
    return _get_widget_html("mp-info")


@mcp.resource("ui://bank-holidays", mime_type=MCP_APPS_MIME)
def bank_holidays_widget() -> str:
    """Bank holidays widget showing upcoming UK bank holidays."""
    return _get_widget_html("bank-holidays")


@mcp.resource("ui://crime-stats", mime_type=MCP_APPS_MIME)
def crime_stats_widget() -> str:
    """Crime statistics widget showing crime breakdown by category."""
    return _get_widget_html("crime-stats")


@mcp.resource("ui://cqc-rating", mime_type=MCP_APPS_MIME)
def cqc_rating_widget() -> str:
    """CQC rating widget showing care quality inspection results."""
    return _get_widget_html("cqc-rating")


@mcp.resource("ui://charity-info", mime_type=MCP_APPS_MIME)
def charity_info_widget() -> str:
    """Charity information widget showing Charity Commission data."""
    return _get_widget_html("charity-info")


@mcp.resource("ui://voting-record", mime_type=MCP_APPS_MIME)
def voting_record_widget() -> str:
    """Voting record widget showing MP's parliamentary votes."""
    return _get_widget_html("voting-record")


@mcp.resource("ui://bike-points", mime_type=MCP_APPS_MIME)
def bike_points_widget() -> str:
    """Bike points widget showing Santander Cycles availability."""
    return _get_widget_html("bike-points")


@mcp.resource("ui://journey-planner", mime_type=MCP_APPS_MIME)
def journey_planner_widget() -> str:
    """Journey planner widget showing TfL journey details."""
    return _get_widget_html("journey-planner")


@mcp.resource("ui://road-status", mime_type=MCP_APPS_MIME)
def road_status_widget() -> str:
    """Road status widget showing London road conditions."""
    return _get_widget_html("road-status")


@mcp.resource("ui://nhs-services", mime_type=MCP_APPS_MIME)
def nhs_services_widget() -> str:
    """NHS services widget showing nearby GP surgeries, hospitals, and pharmacies."""
    return _get_widget_html("nhs-services")


def main():
    """Run the MCP server."""
    logger.info("Starting Gov.uk MCP Server...")
    mcp.run()


if __name__ == "__main__":
    main()
