import os
import re
from dataclasses import dataclass

from google import genai
from google.genai import types


DEFAULT_MODEL = "gemini-3.5-flash-lite"
MAX_SOURCE_CHARS = 20000


class ConversionError(RuntimeError):
    """Raised when the model provider cannot complete a conversion."""


@dataclass(frozen=True)
class ConversionResult:
    cpp_code: str
    model: str
    provider: str = "google-gemini"


def build_prompt(python_code: str) -> str:
    return (
        "Convert the following Python code to modern, readable C++17.\n"
        "Preserve the behavior of the Python program as closely as possible.\n"
        "Use standard library facilities where appropriate, include all required "
        "headers, and return only C++ source code with no markdown fences or prose.\n\n"
        "Python code:\n"
        f"{python_code.strip()}\n"
    )


def clean_model_output(text: str) -> str:
    text = text.strip()
    fenced = re.fullmatch(r"```(?:cpp|c\+\+|cxx)?\s*(.*?)\s*```", text, re.DOTALL | re.IGNORECASE)
    if fenced:
        return fenced.group(1).strip()
    return text.replace("```cpp", "").replace("```c++", "").replace("```", "").strip()


def convert_python_to_cpp(python_code: str) -> ConversionResult:
    source = (python_code or "").strip()
    if not source:
        raise ValueError("Enter Python code before converting.")
    if len(source) > MAX_SOURCE_CHARS:
        raise ValueError(f"Source is too large. Keep input under {MAX_SOURCE_CHARS} characters.")

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ConversionError("GEMINI_API_KEY is not configured.")

    model_name = os.getenv("GEMINI_MODEL", DEFAULT_MODEL)
    try:
        client = genai.Client(api_key=api_key)
        prompt = build_prompt(source)
        try:
            response = client.interactions.create(
                model=model_name,
                input=prompt,
                generation_config={
                    "temperature": 0.2,
                    "max_output_tokens": 4096,
                },
            )
            output = getattr(response, "output_text", None)
        except AttributeError:
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.2,
                    max_output_tokens=4096,
                ),
            )
            output = getattr(response, "text", None)
    except Exception as exc:
        raise ConversionError(f"Gemini conversion failed: {exc}") from exc

    if not output:
        raise ConversionError("Gemini returned an empty response.")

    return ConversionResult(cpp_code=clean_model_output(output), model=model_name)
