"""
API Routes - Archivo principal refactorizado
Registra todas las rutas modulares de la API
"""

from flask import Blueprint
from flask_cors import CORS
import logging

# Importar blueprints modulares
from app.api.status_route import status_bp
from app.api.start_conversation_route import start_conversation_bp
from app.api.resume_route import resume_bp

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Blueprint principal de la API
api_bp = Blueprint("api", __name__, url_prefix="/api")
CORS(api_bp)

# Registrar rutas modulares
api_bp.register_blueprint(status_bp)
api_bp.register_blueprint(start_conversation_bp)
api_bp.register_blueprint(resume_bp)
