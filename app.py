import os

from flask import Flask, jsonify, render_template, request
from dotenv import load_dotenv

from converter import ConversionError, convert_python_to_cpp


load_dotenv()

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 128 * 1024


@app.get("/")
def index():
    return render_template("index.html")


@app.get("/healthz")
def healthz():
    return jsonify({"status": "ok"})


@app.post("/api/convert")
def convert():
    data = request.get_json(silent=True) or {}
    source = data.get("code", "")

    try:
        result = convert_python_to_cpp(source)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    except ConversionError as exc:
        return jsonify({"error": str(exc)}), 503

    return jsonify(
        {
            "cpp_code": result.cpp_code,
            "model": result.model,
            "provider": result.provider,
            "direction": "Python to C++",
        }
    )


if __name__ == "__main__":
    port = int(os.getenv("PORT", "5000"))
    app.run(host="0.0.0.0", port=port)
