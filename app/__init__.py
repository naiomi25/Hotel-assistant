from flask import Flask, jsonify, send_from_directory
from app.api.routes import api_bp
from app.graph import build_graph
import os


def create_app():

    app = Flask(__name__)

    app.graph = build_graph()

    app.register_blueprint(api_bp, url_prefix="/api")

    @app.route("/")
    def check():
        return jsonify({"msg": "api funcionando correctamente"})

    # ⭐ SERVIR ARCHIVOS DESDE DATA_DB (PDFs, datos, etc.)
    @app.route("/data_db/<path:filename>")
    def serve_data_db(filename):
        data_db_dir = os.path.join(app.root_path, "data_db")
        return send_from_directory(data_db_dir, filename)

    return app
