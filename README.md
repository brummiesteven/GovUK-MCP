# Gov.uk MCP Server

A comprehensive Model Context Protocol (MCP) server providing access to 27 UK government data sources and services. Built for Claude Desktop and other MCP-compatible clients.
NOTE: This is a hobby project of which around 80% is vibe coded, expect issues and use for demonstration purposes only. 

## 🌟 Features

- **33 Government APIs**: Companies House, Parliament, NHS, Transport, and more
- **Production-Ready**: Comprehensive input validation, error sanitization, rate limiting
- **Well-Tested**: 185+ test cases covering critical functionality
- **Type-Safe**: Full input validation with regex patterns
- **Secure**: Sanitized errors, secure authentication, no information disclosure
- **Fast**: Concurrent execution for bulk operations (voting records)
- **Maintainable**: Tool registry pattern, modular architecture

## 📦 Installation

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/govmcp.git
cd govmcp

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
