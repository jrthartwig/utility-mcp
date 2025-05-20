import azure.functions as func
import datetime
import json
import logging
import requests
import os

app = func.FunctionApp()

@app.route(route="UtilityRatesFunction", auth_level="function")
def UtilityRatesFunction(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('UtilityRatesFunction HTTP trigger received a request.')

    # Get lat/lon from query or body
    lat = req.params.get('lat')
    lon = req.params.get('lon')
    if not lat or not lon:
        try:
            req_body = req.get_json()
        except ValueError:
            req_body = {}
        lat = lat or req_body.get('lat')
        lon = lon or req_body.get('lon')

    if not lat or not lon:
        return func.HttpResponse(
            json.dumps({"error": "Missing required parameters: lat and lon."}),
            status_code=400,
            mimetype="application/json"
        )

    api_key = os.environ.get("NREL_API_KEY")
    if not api_key:
        return func.HttpResponse(
            json.dumps({"error": "NREL_API_KEY environment variable not set."}),
            status_code=500,
            mimetype="application/json"
        )
    url = f"https://developer.nrel.gov/api/utility_rates/v3.json?api_key={api_key}&lat={lat}&lon={lon}"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        return func.HttpResponse(
            json.dumps(data),
            status_code=200,
            mimetype="application/json"
        )
    except requests.RequestException as e:
        logging.error(f"Error calling NREL API: {e}")
        return func.HttpResponse(
            json.dumps({"error": "Failed to fetch utility data from NREL API."}),
            status_code=502,
            mimetype="application/json"
        )

@app.route(route="v1/context", auth_level="function", methods=["POST"])
def mcp_context(req: func.HttpRequest) -> func.HttpResponse:
    """
    MCP /v1/context endpoint: expects a POST with a context request, returns context response per MCP spec.
    """
    try:
        req_body = req.get_json()
    except ValueError:
        return func.HttpResponse(
            json.dumps({"error": "Invalid JSON in request body."}),
            status_code=400,
            mimetype="application/json"
        )
    # Example: expects lat/lon in context request
    lat = req_body.get("lat")
    lon = req_body.get("lon")
    if not lat or not lon:
        return func.HttpResponse(
            json.dumps({"error": "Missing required parameters: lat and lon in request body."}),
            status_code=400,
            mimetype="application/json"
        )
    api_key = os.environ.get("NREL_API_KEY")
    if not api_key:
        return func.HttpResponse(
            json.dumps({"error": "NREL_API_KEY environment variable not set."}),
            status_code=500,
            mimetype="application/json"
        )
    url = f"https://developer.nrel.gov/api/utility_rates/v3.json?api_key={api_key}&lat={lat}&lon={lon}"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        nrel_data = response.json()
        # Format as MCP context response (example, adjust as needed)
        mcp_response = {
            "context": {
                "location": {"lat": lat, "lon": lon},
                "utility_data": nrel_data.get("outputs", {})
            },
            "provider": "utility-mcp-azure-function",
            "timestamp": datetime.datetime.utcnow().isoformat() + "Z"
        }
        return func.HttpResponse(
            json.dumps(mcp_response),
            status_code=200,
            mimetype="application/json"
        )
    except requests.RequestException as e:
        logging.error(f"Error calling NREL API: {e}")
        return func.HttpResponse(
            json.dumps({"error": "Failed to fetch utility data from NREL API."}),
            status_code=502,
            mimetype="application/json"
        )

@app.route(route="v1/metadata", auth_level="function", methods=["GET"])
def mcp_metadata(req: func.HttpRequest) -> func.HttpResponse:
    """
    MCP /v1/metadata endpoint: returns metadata about this MCP server.
    """
    metadata = {
        "name": "utility-mcp-azure-function",
        "description": "MCP server for utility data using the NREL API.",
        "version": "0.1.0",
        "provider": "utility-mcp-azure-function",
        "endpoints": ["/v1/context", "/v1/metadata", "/v1/health"]
    }
    return func.HttpResponse(
        json.dumps(metadata),
        status_code=200,
        mimetype="application/json"
    )

@app.route(route="v1/health", auth_level="function", methods=["GET"])
def mcp_health(req: func.HttpRequest) -> func.HttpResponse:
    """
    MCP /v1/health endpoint: returns health status.
    """
    health = {
        "status": "ok",
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z"
    }
    return func.HttpResponse(
        json.dumps(health),
        status_code=200,
        mimetype="application/json"
    )