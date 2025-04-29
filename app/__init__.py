"""
Application initialization module.
Sets up the Flask application and its components.
"""
import os # <--- Added import os
from flask import Flask, jsonify # Import jsonify for error handling
from .config import settings
from .modules.logger import app_logger

def create_app():
    """
    Create and configure the Flask application.
    
    Returns:
        Flask: Configured Flask application instance
    """
    app = Flask(__name__, 
                static_folder='static', 
                template_folder='templates')
    
    # Load configuration from settings object
    app.config.from_object(settings)
    # Override Flask defaults with our settings if needed
    app.config['MAX_CONTENT_LENGTH'] = settings.MAX_CONTENT_LENGTH
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'a-very-secret-key-in-prod') # Use env var or default
    app.config['DEBUG'] = settings.DEBUG

    app_logger.info(f"Flask App Name: {app.name}")
    app_logger.info(f"Debug Mode: {app.config['DEBUG']}")
    app_logger.info(f"Max Content Length: {app.config['MAX_CONTENT_LENGTH']}")

    # --- Register Blueprints --- #
    try:
        from .main import main_bp
        app.register_blueprint(main_bp)
        app_logger.info("Registered 'main' blueprint.")
    except ImportError as e:
        app_logger.error(f"Failed to import or register blueprint: {e}", exc_info=True)
        # Depending on severity, you might want to raise an exception or exit

    # --- Global Error Handlers --- #
    # It's often better to define these here or in a dedicated errors module
    # than within the blueprint itself, especially for common HTTP errors.

    @app.errorhandler(404)
    def not_found_error(error):
        app_logger.warning(f"404 Not Found: {error}")
        # Optionally render an error template
        # from flask import render_template
        # return render_template('error.html', error_title="الصفحة غير موجودة", error_message="لم نتمكن من العثور على الصفحة التي طلبتها.", app_name=settings.APP_NAME), 404
        return jsonify({"status": "error", "message": "الصفحة غير موجودة"}), 404 # Page not found

    @app.errorhandler(413)
    def request_entity_too_large(error):
        app_logger.warning(f"413 Request Entity Too Large: {error}")
        return jsonify({
            "status": "error",
            "message": f"الملف كبير جداً. الحد الأقصى هو {settings.MAX_CONTENT_LENGTH // (1024*1024)} ميجابايت." # File too large
        }), 413

    @app.errorhandler(500)
    def internal_error(error):
        app_logger.error(f"500 Internal Server Error: {error}", exc_info=True) # Log traceback for 500s
        return jsonify({"status": "error", "message": "خطأ داخلي في الخادم"}), 500 # Internal server error

    @app.errorhandler(Exception)
    def handle_exception(e):
        # Catch-all for any unhandled exceptions
        # Log the exception details
        app_logger.critical(f"Unhandled Exception: {e}", exc_info=True)
        # Return a generic 500 error response
        # Avoid exposing detailed error messages to the client in production
        if settings.DEBUG:
             # In debug mode, maybe return more details
             return jsonify({"status": "error", "message": f"Unhandled Exception: {str(e)}"}), 500
        else:
             return jsonify({"status": "error", "message": "حدث خطأ غير متوقع"}), 500 # An unexpected error occurred

    # Log application startup
    app_logger.info(f"Application '{settings.APP_NAME}' created and configured.")
    
    return app
