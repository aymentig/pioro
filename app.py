import os
import json
from flask import Flask, render_template, request, jsonify
import anthropic

app = Flask(__name__)
client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

SYSTEM_PROMPT = """You are an expert multilingual writing assistant. The user will send you text in any language.

Your job:
1. Detect the language automatically
2. Fix grammar, spelling, punctuation, and style
3. Return a JSON response with this exact structure:

{
  "language": "detected language name in English",
  "corrected": "the fully corrected text",
  "changes": [
    {
      "original": "the original phrase",
      "fixed": "the corrected phrase",
      "explanation": "short explanation in the same language as the input text"
    }
  ],
  "overall": "one sentence overall feedback in the same language as the input text"
}

Rules:
- If the text has no errors, return an empty changes array and say so in overall
- Keep the tone and meaning of the original text
- Explanations and overall feedback must be in the SAME language as the input
- Only return valid JSON, nothing else
"""

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/check", methods=["POST"])
def check():
    data = request.get_json()
    text = data.get("text", "").strip()
    if not text:
        return jsonify({"error": "No text provided"}), 400

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2048,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": text}]
    )

    raw = message.content[0].text.strip()
    # Strip markdown code fences if present
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[1]
        raw = raw.rsplit("```", 1)[0]

    result = json.loads(raw)
    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True, port=5000)
