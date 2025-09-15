"""Health check blueprint for the application."""
from flask import Blueprint, jsonify

from ..utils import check_health

health_bp = Blueprint('health', __name__)

@health_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    health_status = check_health()
    status_code = 200 if health_status['status'] == 'healthy' else 503
    return jsonify(health_status), status_code
