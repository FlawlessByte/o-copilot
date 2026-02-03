# o-copilot

FastAPI service for Orbital Copilot's **credit usage** tech task.

## What this project does (gist)

This service exposes a single usage endpoint:

- **GET `/usage`**: returns usage data for the current billing period.

It combines two upstream data sources:

- **Messages**: `GET https://owpublic.blob.core.windows.net/tech-task/messages/current-period`
- **Reports**: `GET https://owpublic.blob.core.windows.net/tech-task/reports/:id`

For each upstream message:

- If the message has a `report_id`:
  - Fetch the report.
  - If the report exists, we use the report’s fixed `credit_cost`, and include `report_name`.
  - If the report does not exist, we fall back to calculating credits from the message `text`. 
- If the message has no `report_id`, we calculate credits from the message `text`. The compute_credits function handles the algorithm to calculate the credits.

The response matches the contract documented in `test.py` comments:

```json
{
  "usage": [
    {
      "message_id": 1000,
      "timestamp": "2024-04-29T02:08:29.375Z",
      "report_name": "Tenant Obligations Report",
      "credits_used": 79
    }
  ]
}
```

Notes:
- `report_name` is not included when there is no valid report.
- Credit calculations use `Decimal` (avoiding the weird issues with float). 
- Reports are cached **per request** to avoid repeated upstream lookups when multiple messages share the same `report_id`.

## Requirements

- Python **3.11+**

## Running the server locally

```bash
make dev
```

Then:

```bash
curl http://127.0.0.1:8000/health
curl http://127.0.0.1:8000/usage
```

## Configuration (env vars)

Settings are loaded via `pydantic-settings` from the host environment (and optional `.env` file). The supported env variables are listed in the config.py

Example:

```bash
LOG_LEVEL=debug make dev
```

## Run with Docker

```bash
docker compose up --build
```

Then:

```bash
curl http://127.0.0.1:8000/health
curl http://127.0.0.1:8000/usage
```

## Tests

```bash
make test
```

or

```bash
python -m pytest -q
```

Tests currently focus on the `compute_credits()` rules in `app/costs.py`.

## Code layout

- `app/main.py`: FastAPI app setup + `/health` + router registration
- `app/routes/usage.py`: `/usage` endpoint 
- `app/costs.py`: credit calculation (`compute_credits(text)`)
- `app/config.py`: env-driven settings
- `app/logging_config.py`: structlog configuration (because json works best with the logging tools)
- `tests/`: pytest tests



## Further improvements

Things I’d add with more time (production hardening):

- **Caching**: report caching is currently per-request; use a shared cache (e.g., Redis) with a TTL to reuse report lookups across requests.
- **Rate limiting**: apply rate limits (ideally at the API gateway) to protect upstream services and control cost.
- **Authentication/authorization**: add service-to-service auth (e.g., JWT or mTLS) and restrict access to `/usage`.
- **Observability**: expose metrics (latency, error rates, upstream call counts) via OpenTelemetry or Prometheus; add tracing for upstream calls.
- **Pagination**: paginate the `usage` array (and/or allow filtering by time window) to handle large billing periods.
- **Retries**: add bounded retries with exponential backoff for transient upstream failures (while preserving correctness for billing).
- **Timeouts**: make upstream HTTP timeouts explicit and configurable via env vars (and use separate connect/read timeouts if needed).
