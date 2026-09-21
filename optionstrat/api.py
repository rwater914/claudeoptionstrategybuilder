from __future__ import annotations

import json
import os
from typing import Any, TypeVar

import httpx
import streamlit as st
from pydantic import BaseModel, ValidationError

from .models import Analysis, IndexPicks, MarketItem, PickCollection, VixPredictor

T = TypeVar("T", bound=BaseModel)


class OptionStratError(RuntimeError):
    pass


def configured_api_url() -> str:
    try:
        secret = st.secrets.get("OPTIONSTRAT_API_URL")
    except FileNotFoundError:
        secret = None
    value = os.getenv("OPTIONSTRAT_API_URL") or secret or "http://127.0.0.1:8080/api"
    return str(value).rstrip("/")


@st.cache_data(ttl=60, show_spinner=False)
def _request(
    base_url: str,
    method: str,
    path: str,
    params_json: str = "{}",
    body_json: str = "null",
) -> dict[str, Any]:
    try:
        response = httpx.request(
            method,
            f"{base_url}/{path.lstrip('/')}",
            params=json.loads(params_json),
            json=json.loads(body_json),
            timeout=httpx.Timeout(45.0, connect=5.0),
        )
        response.raise_for_status()
        payload = response.json()
    except httpx.TimeoutException as exc:
        raise OptionStratError("The API timed out. Try refreshing in a moment.") from exc
    except httpx.HTTPStatusError as exc:
        try:
            message = exc.response.json().get("error")
        except (ValueError, AttributeError):
            message = None
        raise OptionStratError(message or f"The API returned HTTP {exc.response.status_code}.") from exc
    except (httpx.HTTPError, ValueError) as exc:
        raise OptionStratError(f"Could not reach the options API: {exc}") from exc
    if not isinstance(payload, dict):
        raise OptionStratError("The API returned an unexpected response.")
    return payload


def _parse(model: type[T], payload: dict[str, Any]) -> T:
    try:
        return model.model_validate(payload)
    except ValidationError as exc:
        raise OptionStratError("The API response was missing expected market data.") from exc


class OptionStratClient:
    def __init__(self, base_url: str | None = None):
        self.base_url = (base_url or configured_api_url()).rstrip("/")

    def health(self) -> dict[str, Any]:
        return _request(self.base_url, "GET", "healthz")

    def analyze(self, ticker: str) -> Analysis:
        payload = _request(
            self.base_url,
            "POST",
            "analyze",
            body_json=json.dumps({"ticker": ticker.upper()}),
        )
        return _parse(Analysis, payload)

    def pick(self, path: str, params: dict[str, Any] | None = None) -> MarketItem:
        return _parse(
            MarketItem,
            _request(self.base_url, "GET", path, params_json=json.dumps(params or {})),
        )

    def picks(self, path: str) -> PickCollection:
        return _parse(PickCollection, _request(self.base_url, "GET", path))

    def vix(self) -> VixPredictor:
        return _parse(VixPredictor, _request(self.base_url, "GET", "vix-predictor"))

    def index_picks(self, index: str) -> IndexPicks:
        payload = _request(
            self.base_url,
            "GET",
            "index-picks",
            params_json=json.dumps({"index": index}),
        )
        return _parse(IndexPicks, payload)
