from flask import Flask, request, jsonify
import firebase_admin
from firebase_admin import credentials, db

app = Flask(__name__)
API_TOKEN = "hbpgamer"

# 🔐 Khởi tạo Firebase Admin SDK
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    "databaseURL": "https://keyserver-a7764-default-rtdb.asia-southeast1.firebasedatabase.app/"
})

# 📌 Hàm kiểm tra token
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

# ✅ API kiểm tra key
@app.route('/verify-key', methods=['POST'])
@token_required
def verify_key():
    data = request.json
    key = data.get('key')
    ref = db.reference(f"keys/{key}")
    value = ref.get()

    if value is None:
        return jsonify({'status': 'not_found'}), 404
    elif value == 'used':
        return jsonify({'status': 'used'}), 200
    elif value == 'unused':
        return jsonify({'status': 'unused'}), 200
    else:
        return jsonify({'status': 'invalid'}), 400

# ✅ API đánh dấu key đã dùng
@app.route('/mark-used', methods=['POST'])
@token_required
def mark_used():
    data = request.json
    key = data.get('key')
    ref = db.reference(f"keys/{key}")
    if ref.get() is None:
        return jsonify({'status': 'not_found'}), 404

    ref.set("used")
    return jsonify({'status': 'updated'}), 200

@app.route('/', methods=['GET'])
def home():
    return "Server is alive", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
