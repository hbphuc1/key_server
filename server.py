import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

API_TOKEN = "hbpgamer"
FIREBASE_DB_URL = "https://keyserver-a7764-default-rtdb.asia-southeast1.firebasedatabase.app"

def token_required(func):
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if auth_header is None or not auth_header.startswith("Bearer "):
            return jsonify({"error": "Missing or invalid Authorization header"}), 401
        token = auth_header.split(" ")[1]
        if token != API_TOKEN:
            return jsonify({"error": "Invalid token"}), 401
        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper

@app.route('/verify-key', methods=['POST'])
@token_required
def verify_key():
    key = request.json.get("key")
    try:
        res = requests.get(f"{FIREBASE_DB_URL}/{key}.json")
        if res.status_code == 200:
            value = res.json()
            if value is None:
                return jsonify({"status": "not_found"}), 404
            elif value == "unused":
                return jsonify({"status": "unused"}), 200
            elif value == "used":
                return jsonify({"status": "used"}), 200
            else:
                return jsonify({"status": "invalid"}), 400
        else:
            return jsonify({"error": "Firebase error"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/mark-used', methods=['POST'])
@token_required
def mark_used():
    key = request.json.get("key")
    try:
        res = requests.put(f"{FIREBASE_DB_URL}/{key}.json", json="used")
        if res.status_code == 200:
            return jsonify({"status": "updated"}), 200
        else:
            return jsonify({"error": "Firebase error"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/')
def home():
    return "Server is alive", 200

if __name__ == '__main__':
    app.run()
