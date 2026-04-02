"""Main API route registration."""
from flask import Flask
from api.retinal_routes import retinal_bp
from api.lifestyle_routes import lifestyle_bp
from api.advice_routes import advice_bp
from api.simulation_routes import simulation_bp
from api.auth_routes import auth_bp
from api.history_routes import history_bp
from api.results_routes import results_bp
from api.plans_routes import plans_bp
from api.reports_routes import reports_bp
from utils.logger import get_logger

logger = get_logger(__name__)


def register_routes(app: Flask):
    """
    Register all API route blueprints.

    Args:
        app: Flask application instance
    """
    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(history_bp, url_prefix='/api/history')
    app.register_blueprint(results_bp, url_prefix='/api/results')
    app.register_blueprint(plans_bp, url_prefix='/api/plans')
    app.register_blueprint(reports_bp, url_prefix='/api/reports')
    app.register_blueprint(retinal_bp, url_prefix='/api/retinal')
    app.register_blueprint(lifestyle_bp, url_prefix='/api/lifestyle')
    app.register_blueprint(advice_bp, url_prefix='/api/advice')
    app.register_blueprint(simulation_bp, url_prefix='/api/simulation')

    logger.info("All API routes registered")

    # Log registered routes
    for rule in app.url_map.iter_rules():
        logger.debug(f"Route: {rule.endpoint} -> {rule.rule}")
