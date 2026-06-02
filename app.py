from flask import Flask, request, jsonify, render_template
import anthropic
import os

app = Flask(__name__)
client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/suggest", methods=["POST"])
def suggest():
    data = request.json
    meat = data.get("meat", "")
    fish = data.get("fish", "")
    vegetables = data.get("vegetables", [])
    other = data.get("other", "")

    ingredients = []
    if meat:
        ingredients.append(f"肉: {meat}")
    if fish:
        ingredients.append(f"魚: {fish}")
    if vegetables:
        ingredients.append(f"野菜: {', '.join(vegetables)}")
    if other:
        ingredients.append(f"その他: {other}")

    if not ingredients:
        return jsonify({"error": "食材を入力してください"}), 400

    ingredient_text = "\n".join(ingredients)

    prompt = f"""以下の食材を使って作れる献立を5つ提案してください。

食材:
{ingredient_text}

各献立について以下の形式で回答してください（JSONの配列形式で）:
[
  {{
    "name": "料理名",
    "description": "料理の簡単な説明（1〜2文）",
    "main_ingredients": ["使用する主な食材1", "食材2"],
    "cooking_time": "調理時間の目安（例: 30分）",
    "difficulty": "難易度（簡単/普通/難しい）"
  }}
]

JSONのみ返してください。説明文は不要です。"""

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2000,
        messages=[{"role": "user", "content": prompt}]
    )

    import json
    import re
    response_text = message.content[0].text
    json_match = re.search(r'\[.*\]', response_text, re.DOTALL)
    if json_match:
        recipes = json.loads(json_match.group())
    else:
        return jsonify({"error": "レシピの解析に失敗しました"}), 500

    return jsonify({"recipes": recipes})


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True, port=5001)
