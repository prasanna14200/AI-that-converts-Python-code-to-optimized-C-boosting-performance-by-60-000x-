# Python to C++ Converter

Small Flask web app that converts Python source code to C++17 using the Gemini API. The original project direction is Python to C++; this app keeps that direction consistently in the UI, API, prompts, and deployment configuration.

This public demo does not compile or execute visitor-submitted code. It only sends source code to the model provider and lets visitors view, copy, and download the generated C++.

## Provider and free tier

The preserved workflow uses Google Gemini. As of October 2, 2026, Google documents that new Gemini API accounts begin on the Free Tier for eligible models, subject to free-tier rate limits. The default model here is `gemini-3.5-flash-lite`; Google now limits 2.5 model access to users who actively used those models in the past and recommends `gemini-3.5-flash-lite` or `gemini-3.8-flash` for new projects.

The app requires `google-genai>=2.0.0` because older 1.x SDK releases send a legacy Interactions API schema that the Gemini API now rejects.

Set credentials with environment variables. Do not commit real keys.

## Local setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

Edit `.env` and set `GEMINI_API_KEY`.

Run the app:

```bash
python app.py
```

Open `http://localhost:5000`.

## Tests

```bash
python -m unittest discover -s tests
python tests/sample_semantics_check.py
```

`tests/sample_semantics_check.py` compiles and runs fixed, trusted sample programs only. It is not part of the public web app and it does not execute visitor input. It requires `g++` on PATH.

## Render deployment

Use the included `render.yaml` or create a web service manually:

- Service type: Web Service
- Runtime: Python
- Root Directory: leave blank
- Build Command: `pip install -r requirements.txt`
- Start Command: `gunicorn app:app --bind 0.0.0.0:$PORT`
- Instance type: Free
- Required environment variables: `GEMINI_API_KEY`
- Optional environment variables: `GEMINI_MODEL`
- Health-check path: `/healthz`

## Limitations

Generated code is model output. Review and test it before relying on it. The app intentionally makes no performance claim and does not include a benchmark for the old "60,000x" wording.
