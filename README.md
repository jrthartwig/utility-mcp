# Utility MCP Azure Function

This project is an Azure Function (Python) that exposes an HTTP endpoint to fetch utility rate data from the NREL API. It is designed to be called by a React app, Copilot, or any client via HTTP.

## Usage
- Deploy as an Azure Function App.
- Call the endpoint `/api/UtilityRatesFunction?lat=LAT&lon=LON` with your latitude and longitude.
- Returns utility data as JSON from the NREL API.

## Environment
- Python 3.12 (3.6–3.11 recommended for Azure)
- Azure Functions Core Tools

## Security
- The NREL API key is hardcoded for demo; move to environment variables for production.

## References
- [NREL Utility Rates API](https://developer.nrel.gov/docs/energy-apis/utility-rates-v3/)
- [Azure Functions Python](https://learn.microsoft.com/azure/azure-functions/functions-reference-python)
- [Model Context Protocol](https://modelcontextprotocol.io/llms-full.txt)

---
