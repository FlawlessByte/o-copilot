from decimal import Decimal
from typing import Any

import httpx
from fastapi import APIRouter, HTTPException

from app.costs import compute_credits

import structlog

logger = structlog.get_logger("o-copilot.usage")

router = APIRouter()

MESSAGES_URL = "https://owpublic.blob.core.windows.net/tech-task/messages/current-period"
REPORT_URL_TEMPLATE = "https://owpublic.blob.core.windows.net/tech-task/reports/{report_id}"


def _to_json_number(d: Decimal) -> float:
    # Keep response stable: 2dp is enough for 0.05/0.1/0.2/0.3 increments.
    return float(d.quantize(Decimal("0.01")))


async def _fetch_messages(client: httpx.AsyncClient):
    resp = await client.get(MESSAGES_URL)
    resp.raise_for_status()
    
    payload = resp.json()
    messages = payload.get("messages", None)
    
    if not messages:
        raise ValueError("Upstream payload is missing 'messages'")
    logger.debug("fetched_messages", count=len(messages))
    return messages


async def _fetch_report(
    client: httpx.AsyncClient, report_id: int
) -> dict[str, Any] | None:
    """
    Returns report JSON on 200, None on 404. Other errors raise.
    """
    url = REPORT_URL_TEMPLATE.format(report_id=report_id)
    resp = await client.get(url)
    if resp.status_code == 404:
        logger.info("report_not_found", report_id=report_id)
        return None
    resp.raise_for_status()
    return resp.json()


def _parse_message(msg: dict[str, Any]):

    message_id = msg.get("id")
    timestamp = msg.get("timestamp")
    text = msg.get("text", "")
    report_id = msg.get("report_id", None)

    return message_id, timestamp, str(text), report_id


def _report_to_name_and_cost(report_id: int, report: dict[str, Any]) -> tuple[str, Decimal]:
    name = report.get("name")
    credit_cost = report.get("credit_cost")

    return name, Decimal(str(credit_cost))


async def _compute_credits_for_message(
        client: httpx.AsyncClient,
        report_cache: dict[int, dict[str, Any] | None],
        text: str,
        report_id: int | None,
    ):
    if report_id is None:
        return compute_credits(text), None

    if report_id not in report_cache:
        report_cache[report_id] = await _fetch_report(client, report_id)

    report = report_cache[report_id]
    if report is None:
        logger.info("report_fallback_to_text_cost", report_id=report_id)
        return compute_credits(text), None

    report_name = report.get('name', None)
    credits = Decimal(str(report.get('credit_cost')))
    
    return credits, report_name


@router.get("/usage")
async def usage():
    """
    Contract:
      {
        "usage": [
          {
            "message_id": number,
            "timestamp": string,
            "report_name"?: string,
            "credits_used": number
          }
        ]
      }
    """
    try:
        logger.debug("usage_request_start")
        async with httpx.AsyncClient(timeout=10.0) as client:
            messages = await _fetch_messages(client)

            # per-request report cache to avoid repeated upstream calls.
            report_cache = {}

            usage_items = []
            
            for msg in messages:
                message_id, timestamp, text, report_id = _parse_message(msg)
                credits, report_name = await _compute_credits_for_message(
                    client=client,
                    report_cache=report_cache,
                    text=text,
                    report_id=report_id,
                )

                item: dict[str, Any] = {
                    "message_id": message_id,
                    "timestamp": timestamp,
                    "credits_used": _to_json_number(credits),
                }
                if report_name is not None:
                    item["report_name"] = report_name

                usage_items.append(item)

            logger.debug("usage_request_done", messages=len(messages))
            return {"usage": usage_items}
    except httpx.HTTPError as e:
        logger.exception("upstream_http_error")
        raise HTTPException(status_code=502, detail=f"Upstream request failed: {e}") from e
    except ValueError as e:
        logger.exception("usage_value_error")
        raise HTTPException(status_code=502, detail=str(e)) from e

