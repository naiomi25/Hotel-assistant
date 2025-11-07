from flask import Flask, jsonify
from app.api.routes import api_bp
from app.graph import build_graph

def create_app():
    
    app = Flask(__name__)

    app.graph = build_graph()

    app.register_blueprint(api_bp, url_prefix="/api")
    
    @app.route("/")
    def check():
        return jsonify({"msg": "api funcionando correctamente"})


    return app