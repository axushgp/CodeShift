"""
Watsonx client — thin wrapper around the watsonx.ai text generation REST API.

Uses CODESHIFT_ settings for all credentials and endpoints.
No credentials are hardcoded.

Raises WatsonxError on any call failure.
"""

from __future__ import annotations

import json
import logging
from typing import Any

import httpx

from app.config import get_settings

logger = logging.getLogger(__name__)

# Watsonx.ai text generation endpoint path
_GENERATION_PATH = "/ml/v1/text/generation"


class WatsonxError(Exception):
    """Raised when a Watsonx API call fails."""


class WatsonxClient:
    """
    Minimal synchronous Watsonx text generation client.

    Obtains an IAM token on first use and reuses it for the session lifetime.
    For the MVP, token refresh is not implemented — restart the server to
    refresh an expired token.
    """

    def __init__(self) -> None:
        self._settings = get_settings()
        self._iam_token: str | None = None

    # ── IAM authentication ─────────────────────────────────────────────────────

    def _fetch_iam_token(self) -> str:
        """Exchange the API key for an IAM bearer token."""
        api_key = self._settings.watsonx_api_key
        if not api_key:
            raise WatsonxError(
                "CODESHIFT_WATSONX_API_KEY is not set. "
                "Set it in .env or as an environment variable."
            )

        resp = httpx.post(
            "https://iam.cloud.ibm.com/identity/token",
            data={
                "grant_type": "urn:ibm:params:oauth:grant-type:apikey",
                "apikey": api_key,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=30,
        )
        if resp.status_code != 200:
            raise WatsonxError(
                f"IAM token fetch failed: HTTP {resp.status_code} — {resp.text[:200]}"
            )
        token = resp.json().get("access_token")
        if not token:
            raise WatsonxError("IAM response did not contain access_token.")
        return token

    def _get_token(self) -> str:
        if self._iam_token is None:
            self._iam_token = self._fetch_iam_token()
        return self._iam_token

    # ── Text generation ────────────────────────────────────────────────────────

    def generate(self, prompt: str, max_new_tokens: int = 1500) -> str:
        """
        Send a prompt to watsonx.ai and return the generated text.

        Raises WatsonxError on any failure.
        """
        settings = self._settings
        if not settings.watsonx_project_id:
            raise WatsonxError(
                "CODESHIFT_WATSONX_PROJECT_ID is not set. "
                "Set it in .env or as an environment variable."
            )

        url = settings.watsonx_url.rstrip("/") + _GENERATION_PATH
        payload: dict[str, Any] = {
            "model_id": settings.watsonx_model_id,
            "project_id": settings.watsonx_project_id,
            "input": prompt,
            "parameters": {
                "decoding_method": "greedy",
                "max_new_tokens": max_new_tokens,
                "repetition_penalty": 1.1,
            },
        }

        token = self._get_token()
        try:
            resp = httpx.post(
                url,
                json=payload,
                headers={
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json",
                },
                params={"version": "2023-05-29"},
                timeout=60,
            )
        except httpx.TimeoutException as exc:
            raise WatsonxError("Watsonx request timed out.") from exc
        except httpx.RequestError as exc:
            raise WatsonxError(f"Watsonx request failed: {exc}") from exc

        if resp.status_code != 200:
            raise WatsonxError(
                f"Watsonx generation failed: HTTP {resp.status_code} — {resp.text[:300]}"
            )

        try:
            data = resp.json()
            text: str = data["results"][0]["generated_text"]
        except (KeyError, IndexError, json.JSONDecodeError) as exc:
            raise WatsonxError(
                f"Unexpected Watsonx response shape: {resp.text[:300]}"
            ) from exc

        logger.debug("Watsonx generated %d chars", len(text))
        return text
