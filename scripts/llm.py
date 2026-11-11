"""Shared LLM client for the pipeline — DeepSeek (OpenAI-compatible).

Replaces the earlier Anthropic client (the Anthropic org was disabled). Every
structured-output step in the pipeline goes through `extract_json`, which forces
a single JSON object and parses it. Provider, base URL and model ids are all
env-overridable, so a future model rename or provider swap needs no code change.

DeepSeek specifics this module accounts for (verified against api-docs.deepseek.com,
2026-11):
  - base_url is https://api.deepseek.com (no /v1).
  - Current model ids are `deepseek-flash` (cheap/fast) and `deepseek-v4-pro`
    (stronger). The old `deepseek-chat` / `deepseek-reasoner` ids are retired.
  - Both models default to THINKING mode, under which temperature is ignored and
    forced JSON/tool output returns HTTP 400. We disable thinking on every call
    so JSON mode is reliable and temperature actually applies.
  - JSON mode (`response_format={"type":"json_object"}`) requires the word "json"
    in the prompt; if the model emits non-JSON, the API blanks the content, so we
    guard against blank/invalid output and retry.
"""
from __future__ import annotations

import json
import logging
import os
import time

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv(override=True)
log = logging.getLogger("llm")

BASE_URL = os.environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
# Cheap, fast model for scoring + classification; stronger model for long-form.
FAST_MODEL = os.environ.get("DEEPSEEK_FAST_MODEL", "deepseek-flash")
WRITER_MODEL = os.environ.get("DEEPSEEK_WRITER_MODEL", "deepseek-v4-pro")

# Disable thinking so temperature applies, output stays bounded, and JSON mode
# doesn't 400. Sent via extra_body because it's a DeepSeek-only parameter.
_NO_THINKING = {"thinking": {"type": "disabled"}}

_client: OpenAI | None = None


def client() -> OpenAI:
    global _client
    if _client is None:
        key = os.environ.get("DEEPSEEK_API_KEY")
        if not key:
            raise RuntimeError(
                "DEEPSEEK_API_KEY not set. Add it to .env locally or as a "
                "GitHub Actions secret."
            )
        _client = OpenAI(api_key=key, base_url=BASE_URL)
    return _client


def _schema_guide(schema: dict) -> tuple[str, list[str]]:
    """Render an Anthropic-style input_schema into a human-readable key guide
    plus the list of required keys."""
    props = schema.get("properties", {})
    required = schema.get("required", list(props.keys()))
    lines = []
    for name, spec in props.items():
        typ = spec.get("type", "string")
        enum = spec.get("enum")
        constraint = f" — must be exactly one of: {', '.join(map(str, enum))}" if enum else ""
        desc = spec.get("description", "")
        lines.append(f'  "{name}" ({typ}){constraint}: {desc}')
    return "\n".join(lines), required


def extract_json(
    system: str,
    user: str,
    schema: dict,
    *,
    model: str | None = None,
    max_tokens: int = 1024,
    temperature: float = 0.3,
    retries: int = 2,
) -> dict | None:
    """Force a JSON object matching `schema` (an Anthropic-style input_schema
    dict with 'properties' + 'required'). Returns the parsed dict, or None if it
    fails after retries. All required keys are checked before returning.
    """
    guide, required = _schema_guide(schema)
    json_instruction = (
        "\n\nReturn your answer as a single valid json object and nothing else "
        "(no markdown code fences, no commentary before or after). The json "
        "object must contain exactly these keys:\n" + guide +
        "\n\nEvery one of these keys is required: " + ", ".join(required) + "."
    )
    messages = [
        {"role": "system", "content": system + json_instruction},
        {"role": "user", "content": user},
    ]

    last_err = "unknown"
    for attempt in range(retries + 1):
        try:
            resp = client().chat.completions.create(
                model=model or FAST_MODEL,
                max_tokens=max_tokens,
                temperature=temperature,
                response_format={"type": "json_object"},
                extra_body=_NO_THINKING,
                messages=messages,
            )
            content = resp.choices[0].message.content
            if not content or not content.strip():
                last_err = "blank content (DeepSeek JSON-mode guard tripped)"
                log.warning(f"  ! {last_err}; attempt {attempt + 1}/{retries + 1}")
                time.sleep(1.0)
                continue
            data = json.loads(content)
            missing = [k for k in required if k not in data]
            if missing:
                last_err = f"missing required keys {missing}"
                log.warning(f"  ! {last_err}; attempt {attempt + 1}/{retries + 1}")
                time.sleep(1.0)
                continue
            return data
        except json.JSONDecodeError as e:
            last_err = f"JSON parse error: {e}"
            log.warning(f"  ! {last_err}; attempt {attempt + 1}/{retries + 1}")
            time.sleep(1.0)
        except Exception as e:  # network / API / rate-limit
            last_err = f"API error: {e}"
            log.error(f"  ! {last_err}; attempt {attempt + 1}/{retries + 1}")
            time.sleep(2.0)

    log.error(f"  ! extract_json gave up after {retries + 1} attempts: {last_err}")
    return None
