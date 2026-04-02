"""Main Flask application entry point."""
from flask import Flask, jsonify
from flask_cors import CORS
from config import Config
from utils.logger import setup_logger
from api.routes import register_routes
from models.database import db, init_db

def create_app():
    """Create and configure Flask application."""
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize configuration
    Config.init_app()

    # Setup CORS
    CORS(app,
         resources={r"/api/*": {"origins": Config.CORS_ORIGINS}},
         supports_credentials=True,
         allow_headers=["Content-Type", "Authorization"],
         methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])

    # Setup logging
    logger = setup_logger(Config.LOG_LEVEL, Config.LOG_FILE)
    app.logger.handlers = logger.handlers
    app.logger.setLevel(logger.level)

    # Initialize database
    init_db(app)

    # Register API routes
    register_routes(app)

    # Health check endpoint
    @app.route('/health', methods=['GET'])
    def health_check():
        return jsonify({
            'status': 'healthy',
            'service': 'Diabetes Detection AI Backend',
            'version': '1.0.0'
        }), 200

    # Model status endpoint
    @app.route('/model-status', methods=['GET'])
    def model_status():
        from agents.retinal_agent import retinal_agent
        from agents.lifestyle_agent import lifestyle_agent

        return jsonify({
            'retinal_model': {
                'loaded': retinal_agent.model_loaded if hasattr(retinal_agent, 'model_loaded') else False,
                'version': retinal_agent.model.version if retinal_agent.model else None
            },
            'lifestyle_model': {
                'loaded': lifestyle_agent.model.is_loaded if lifestyle_agent.model else False,
                'version': lifestyle_agent.model.version if lifestyle_agent.model else None,
                'features': len(lifestyle_agent.model.feature_names) if lifestyle_agent.model else 0
            }
        }), 200

    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Not found'}), 404

    @app.errorhandler(500)
    def internal_error(error):
        app.logger.error(f'Internal error: {error}')
        return jsonify({'error': 'Internal server error'}), 500

    app.logger.info('Diabetes Detection AI Backend initialized')
    return app


if __name__ == '__main__':
    app = create_app()
    app.run(
        host='0.0.0.0',
        port=Config.PORT,
        debug=Config.DEBUG
    )
