
import json
import os
import time
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import errors, types


# --------------------------------------------------
# PROJECT CONFIGURATION
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent

load_dotenv(BASE_DIR / ".env")

API_KEY = os.getenv("GEMINI_API_KEY")

PROMPT_FILE = BASE_DIR / "diagnose_prompt.md"

# Use a currently supported Gemini model ID.
MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

MAX_RETRIES = 3
RETRY_DELAY = 2


# --------------------------------------------------
# LOAD DIAGNOSIS PROMPT
# --------------------------------------------------

def load_prompt():
    """Load the diagnosis instructions from diagnose_prompt.md."""

    if not PROMPT_FILE.exists():
        raise FileNotFoundError(
            f"Prompt file not found: {PROMPT_FILE}"
        )

    prompt = PROMPT_FILE.read_text(encoding="utf-8").strip()

    if not prompt:
        raise ValueError("diagnose_prompt.md is empty.")

    return prompt


# --------------------------------------------------
# CREATE GEMINI CLIENT
# --------------------------------------------------

def create_client():
    """Create and return the Gemini API client."""

    if not API_KEY:
        raise ValueError(
            "GEMINI_API_KEY is missing. Add it to your .env file."
        )

    return genai.Client(api_key=API_KEY)


# --------------------------------------------------
# PARSE GEMINI RESPONSE
# --------------------------------------------------

def parse_response(response):
    """Convert Gemini JSON response into a Python dictionary."""

    response_text = getattr(response, "text", None)

    if not response_text:
        raise ValueError("Gemini returned an empty response.")

    response_text = response_text.strip()

    # Handle optional Markdown code fences.
    if response_text.startswith("```"):
        lines = response_text.splitlines()

        if lines and lines[0].startswith("```"):
            lines = lines[1:]

        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]

        response_text = "\n".join(lines).strip()

    try:
        result = json.loads(response_text)
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"Gemini returned invalid JSON: {exc}\n"
            f"Response: {response_text}"
        ) from exc

    if not isinstance(result, dict):
        raise ValueError("Gemini response must be a JSON object.")

    return result


# --------------------------------------------------
# AI NETWORK DIAGNOSIS
# --------------------------------------------------

def diagnose_with_ai(evidence):
    """
    Analyze network evidence using Gemini.

    Args:
        evidence: Network diagnostic evidence as a string.

    Returns:
        Dictionary containing Gemini's diagnosis.
    """

    if not isinstance(evidence, str) or not evidence.strip():
        return {
            "success": False,
            "error": "No network evidence was provided."
        }

    client = None

    try:
        prompt = load_prompt()

        full_prompt = f"""
{prompt}

--------------------------------------------------
NETWORK DIAGNOSTIC EVIDENCE
--------------------------------------------------

{evidence}

--------------------------------------------------
IMPORTANT
--------------------------------------------------

Return only one valid JSON object.
Do not include Markdown code fences.
Do not include explanations outside the JSON object.
"""

        client = create_client()

        for attempt in range(1, MAX_RETRIES + 1):

            try:
                response = client.models.generate_content(
                    model=MODEL_NAME,
                    contents=full_prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        temperature=0.2
                    )
                )

                result = parse_response(response)

                result["success"] = True
                return result

            except errors.APIError as exc:

                status_code = getattr(exc, "code", None)

                if status_code == 429:
                    if attempt < MAX_RETRIES:
                        time.sleep(RETRY_DELAY * attempt)
                        continue

                    return {
                        "success": False,
                        "error": "Gemini API quota or rate limit exceeded."
                    }

                if status_code in (500, 503, 504):
                    if attempt < MAX_RETRIES:
                        time.sleep(RETRY_DELAY * attempt)
                        continue

                return {
                    "success": False,
                    "error": f"Gemini API error: {exc}"
                }

            except (ValueError, json.JSONDecodeError) as exc:
                return {
                    "success": False,
                    "error": str(exc)
                }

            except Exception as exc:
                return {
                    "success": False,
                    "error": f"AI diagnosis failed: {exc}"
                }

    except Exception as exc:
        return {
            "success": False,
            "error": str(exc)
        }

    finally:
        if client is not None:
            close_method = getattr(client, "close", None)

            if callable(close_method):
                close_method()


# --------------------------------------------------
# TEST AI ENGINE
# --------------------------------------------------

if __name__ == "__main__":

    sample_evidence = """
    Device: Windows PC
    Interface: Wi-Fi
    IP Address: 192.168.1.10
    Gateway: 192.168.1.1
    DNS Server: 8.8.8.8
    Ping Gateway: Successful
    Ping 8.8.8.8: Successful
    DNS Resolution: Failed
    """

    print("\nStarting NetSage AI diagnosis...\n")

    diagnosis = diagnose_with_ai(sample_evidence)

    print(json.dumps(
        diagnosis,
        indent=4,
        ensure_ascii=False
    ))
