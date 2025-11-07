from app import create_app
from flask_cors import CORS

app = create_app()
CORS(app,
     resources={r"/*": {"origins": ["http://localhost:3000", "http://127.0.0.1:3000"]}},
     supports_credentials=True,
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
     allow_headers=["Content-Type", "Authorization"])

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)