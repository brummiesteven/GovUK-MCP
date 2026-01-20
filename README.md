# Gov.uk MCP Server

A comprehensive Model Context Protocol (MCP) server providing access to 27 UK government data sources and services. Built for Claude Desktop and other MCP-compatible clients.

> **Note:** This is a hobby project, expect issues and use for demonstration purposes only.

## 🌟 Features

- **33 Government APIs**: Companies House, Parliament, NHS, Transport, and more
- **15 Visual Widgets**: Rich UI components via MCP Apps for data visualization
- **Production-Ready**: Comprehensive input validation, error sanitization, rate limiting
- **Type-Safe**: Full input validation with regex patterns
- **Secure**: Sanitized errors, XSS protection, origin validation
- **Fast**: Concurrent execution for bulk operations (voting records)

### 💬 Example Prompts

Try asking:
- "What are the five nearest postcodes to SW1A 1AA?"
- "When is the next Bank Holiday?"
- "How can I get from Brixton to St Pancras?"
- "What's the status of the Circle Line?"
- "Where's my nearest Hospital?"
- "Who's my MP?"
- "What's their voting record?"

## 📦 Installation

```bash
# Clone the repository
git clone https://github.com/brummiesteven/GovUK-MCP.git
cd GovUK-MCP

# Install dependencies
pip install -e .

# Or with dev dependencies
pip install -e ".[dev]"
```

## 🔑 API Keys Setup

Create a `.env` file in the project root:

```bash
# Required for Companies House tools
COMPANIES_HOUSE_API_KEY=your_companies_house_key

# Required for EPC tools
EPC_API_KEY=your_email:your_epc_key

# Optional (works without but has lower rate limits)
TFL_API_KEY=your_tfl_key
```

### API Key Requirements

**Required APIs** (2):
- **Companies House API**: https://developer.company-information.service.gov.uk/
- **EPC API**: https://epc.opendatacommunities.org/

**Optional APIs** (1):
- **TfL API**: https://api-portal.tfl.gov.uk/ (works without key but has rate limits)

**No Key Required** (24 tools):
Postcode, Food Hygiene, Bank Holidays, Gov.uk Search, Flood Warnings, Police Crime, Courts, Charity, NHS, Legislation, CQC, Parliamentary tools

## 🚀 Usage

### With Claude Desktop

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "gov-uk": {
      "command": "python",
      "args": ["-m", "gov_uk_mcp.server"],
      "env": {
        "COMPANIES_HOUSE_API_KEY": "your_key_here",
        "EPC_API_KEY": "your_email:your_key_here"
      }
    }
  }
}
```

### Standalone (For Development)

```bash
python -m gov_uk_mcp.server
```

## 🛠️ Available Tools (33)

### Transport (6)
- `get_tube_status` - All Tube lines status
- `get_line_status` - Specific line status
- `plan_journey` - Journey planner with step-by-step directions
- `get_bike_points` - Santander Cycles availability
- `get_road_status` - Major road conditions
- `search_stops` - Find bus stops, stations, etc.

### Business & Finance (6)
- `search_companies`, `get_company`, `get_company_officers`, `get_company_filing_history`
- `search_charities`, `get_charity`

### Location & Geographic (5)
- `lookup_postcode`, `nearest_postcodes`
- `search_food_establishments`, `get_flood_warnings`, `get_crime_by_postcode`

### Healthcare (5)
- `find_gp_surgeries`, `find_hospitals`, `find_pharmacies`
- `search_cqc_providers`, `get_cqc_provider`

### Parliamentary (5)
- `find_mp`, `search_hansard`, `get_voting_record`
- `search_divisions`, `search_questions`, `get_questions_by_mp`

### Other Services (4)
- `search_epc_by_postcode`, `find_courts`, `search_govuk`, `get_bank_holidays`, `search_legislation`


## 🎨 MCP Apps Widgets

This server includes 15 visual widgets compatible with [MCP Apps](https://github.com/anthropics/mcp-apps)-enabled clients. Widgets provide rich, interactive visualizations of API responses.

| Widget | Description |
|--------|-------------|
| `tube-status` | London Underground status with line colors |
| `postcode-lookup` | Location information grid |
| `company-info` | Companies House profile card |
| `food-hygiene` | FSA ratings with score indicators |
| `flood-warnings` | Environment Agency alerts |
| `mp-info` | MP profile with photo and party colors |
| `bank-holidays` | Upcoming holidays calendar |
| `crime-stats` | Crime breakdown by category |
| `cqc-rating` | Care quality ratings display |
| `charity-info` | Charity Commission details |
| `voting-record` | Parliamentary voting history |
| `bike-points` | Santander Cycles availability |
| `journey-planner` | TfL journey with step-by-step |
| `road-status` | Major road conditions |
| `nhs-services` | GP, hospital, pharmacy finder |

Widgets are automatically served when tools are called from compatible clients.


## 🧪 Testing

```bash
# Run all tests
pytest

# With coverage
pytest --cov=gov_uk_mcp --cov-report=html

# Specific test
pytest tests/test_validation.py -v
```

## 📝 License

MIT - see [LICENSE](LICENSE)

## 🙏 Credits

- [MCP](https://github.com/anthropics/mcp) by Anthropic
- UK Government Open Data APIs
- Python ecosystem

---

**Built for the UK developer community** 🇬🇧
