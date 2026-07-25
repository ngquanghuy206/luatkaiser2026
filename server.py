import os
import base64
from flask import Flask, request, jsonify, Response, stream_with_context
from flask_cors import CORS
from google import genai
from google.genai import types as genai_types

app = Flask(__name__)
CORS(app)

GEMINI_KEY   = os.environ.get("GEMINI_API_KEY", "AIzaSyCX3YoB6WHhnXTtlp742fUjuC_9PHaUM4Q")
GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.0-flash-lite")

@app.route("/api/analyze", methods=["POST", "OPTIONS"])
def analyze():
    if request.method == "OPTIONS":
        return "", 200

    try:
        body = request.get_json(force=True)
        parts_raw = body.get("parts", [])

        contents = []
        for p in parts_raw:
            if "text" in p:
                contents.append(p["text"])
            elif "inlineData" in p:
                mime = p["inlineData"]["mimeType"]
                data = p["inlineData"]["data"]
                img_bytes = base64.b64decode(data)
                contents.append(
                    genai_types.Part.from_bytes(data=img_bytes, mime_type=mime)
                )

        client = genai.Client(api_key=GEMINI_KEY)

        def generate():
            try:
                for chunk in client.models.generate_content_stream(
                    model=GEMINI_MODEL,
                    contents=contents,
                    config=genai_types.GenerateContentConfig(
                        temperature=0.3,
                        max_output_tokens=1500,
                    ),
                ):
                    try:
                        text = chunk.text or ""
                    except Exception:
                        try:
                            text = chunk.candidates[0].content.parts[0].text or ""
                        except Exception:
                            text = ""
                    if text:
                        yield text
            except Exception as e:
                yield f"\n[LỖI: {str(e)}]"

        return Response(
            stream_with_context(generate()),
            mimetype="text/plain; charset=utf-8",
            headers={
                "X-Accel-Buffering": "no",
                "Cache-Control": "no-cache",
                "Access-Control-Allow-Origin": "*",
            }
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/", methods=["GET"])
def index():
    return jsonify({"status": "ok", "model": GEMINI_MODEL})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
