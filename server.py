import os
import base64
from flask import Flask, request, jsonify
from flask_cors import CORS
from google import genai
from google.genai import types as genai_types

app = Flask(__name__)
CORS(app)

GEMINI_KEY   = os.environ.get("GEMINI_API_KEY", "AIzaSyCX3YoB6WHhnXTtlp742fUjuC_9PHaUM4Q")
GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.0-flash-lite")

def get_client():
    return genai.Client(api_key=GEMINI_KEY)

@app.route("/api/analyze", methods=["POST", "OPTIONS"])
def analyze():
    if request.method == "OPTIONS":
        return "", 200

    if not GEMINI_KEY:
        return jsonify({"error": "Chua cau hinh GEMINI_API_KEY"}), 500

    try:
        body = request.get_json(force=True)
        parts_raw = body.get("parts", [])

        # Build contents cho SDK
        contents = []
        for p in parts_raw:
            if "text" in p:
                contents.append(p["text"])
            elif "inlineData" in p:
                # Anh base64
                mime = p["inlineData"]["mimeType"]
                data = p["inlineData"]["data"]
                img_bytes = base64.b64decode(data)
                contents.append(
                    genai_types.Part.from_bytes(data=img_bytes, mime_type=mime)
                )

        client = get_client()
        resp = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=contents,
            config=genai_types.GenerateContentConfig(
                temperature=0.3,
                max_output_tokens=1500,
            ),
        )

        text = ""
        try:
            text = resp.text or ""
        except Exception:
            try:
                text = resp.candidates[0].content.parts[0].text or ""
            except Exception:
                pass

        if not text:
            return jsonify({"error": "Khong co phan hoi tu AI"}), 500

        return jsonify({"text": text})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/", methods=["GET"])
def index():
    return jsonify({"status": "ok", "model": GEMINI_MODEL})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
