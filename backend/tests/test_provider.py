import os
from types import SimpleNamespace

import httpx
import pytest

from app.ai import GeminiProvider
from app.config import get_settings


def test_gemini_timeout_is_sanitized():
    provider = GeminiProvider.__new__(GeminiProvider)
    provider.model = "test"

    def generate_content(**kwargs):
        raise httpx.ReadTimeout("private transport detail")

    provider.client = SimpleNamespace(models=SimpleNamespace(generate_content=generate_content))
    with pytest.raises(RuntimeError, match="Gemini is unreachable or timed out"):
        provider.respond([], [], "en")


@pytest.mark.skipif(os.getenv("SALESPILOT_LIVE_TEST") != "1" or not get_settings().gemini_api_key,
                    reason="Requires explicit opt-in and a Gemini API key")
def test_live_gemini():
    result = GeminiProvider().respond(
        [{"role": "user", "content": "What does the NovaCRM test plan cost?"}],
        [{"filename": "test.txt", "chunk": "The fictional NovaCRM test plan costs INR 4321."}],
        "en",
    )
    assert "4321" in result.response.replace(",", "")
