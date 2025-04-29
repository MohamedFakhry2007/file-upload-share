"""
Main application routes and views.
Defines the main blueprint and routes for the application.
"""
import asyncio # Required for async route
from flask import (
    Blueprint, 
    render_template, 
    request, 
    jsonify, 
    current_app # Access the current Flask app instance
)
from werkzeug.utils import secure_filename
from .modules.uploader import uploader
from .modules.logger import app_logger
from .config import settings

# Create Blueprint
main_bp = Blueprint(
    'main', 
    __name__, 
    template_folder='../templates', # Point to the templates folder relative to this file
    static_folder='../static' # Point to the static folder relative to this file
)

@main_bp.route('/')
def index():
    """Render the main application page (index.html)."""
    try:
        return render_template('index.html', app_name=settings.APP_NAME)
    except Exception as e:
        app_logger.error(f"Error rendering index template: {e}", exc_info=True)
        # Render a generic error page or return a JSON error
        return render_template('error.html', 
                               error_title="خطأ في عرض الصفحة", 
                               error_message="حدث خطأ أثناء تحميل الصفحة الرئيسية.",
                               app_name=settings.APP_NAME), 500

@main_bp.route('/upload', methods=['POST'])
async def upload_file_route(): # Renamed function to avoid clash with uploader.upload_file
    """
    Handle file upload requests asynchronously.
    
    Returns:
        JSON response with upload status and download link or error message.
    """
    app_logger.debug(f"Received request to /upload: {request.method}")

    # 1. Check if file part exists in the request
    if 'file' not in request.files:
        app_logger.warning("Upload request received with no file part.")
        return jsonify({
            "status": "error",
            "message": "لم يتم اختيار ملف"  # No file selected (Arabic)
        }), 400
    
    file = request.files['file']
    
    # 2. Check if filename is empty (user submitted form without selecting file)
    if not file or file.filename == '':
        app_logger.warning("Upload request received with an empty filename.")
        return jsonify({
            "status": "error",
            "message": "الرجاء اختيار ملف للرفع"  # Please select a file to upload (Arabic)
        }), 400
    
    # 3. Secure the filename
    original_filename = file.filename
    filename = secure_filename(original_filename) # Sanitize filename
    app_logger.info(f"Processing upload for file: '{original_filename}' (secured as: '{filename}')")

    # 4. Perform the upload using the uploader module
    try:
        # The uploader.upload_file handles validation and the actual upload process
        # It uses run_in_executor internally for the blocking part
        success, result = await uploader.upload_file(file.stream, filename)
        
        if success:
            app_logger.info(f"Successfully uploaded '{filename}'. Link: {result.get('download_link')}")
            return jsonify({
                "status": "success",
                "message": "تم رفع الملف بنجاح",  # File uploaded successfully (Arabic)
                "download_link": result.get("download_link", "")
            })
        else:
            # Uploader returns specific error message in result['error']
            error_msg = result.get("error", "خطأ غير معروف أثناء الرفع") # Unknown upload error (Arabic)
            app_logger.error(f"Upload failed for '{filename}': {error_msg}")
            # Determine appropriate status code based on error if possible
            status_code = 500 if "API" in error_msg or "Network" in error_msg else 400
            return jsonify({
                "status": "error",
                "message": f"{error_msg}" # Directly use the error from uploader
            }), status_code
        
    except Exception as e:
        # Catch unexpected errors during the route handling itself
        app_logger.error(f"Unexpected error in /upload route handler: {str(e)}", exc_info=True)
        return jsonify({
            "status": "error",
            "message": "حدث خطأ غير متوقع أثناء معالجة الرفع"  # Unexpected error during upload processing (Arabic)
        }), 500

# Note: Common error handlers (404, 413, 500) are now defined globally in app/__init__.py
# You could keep specific blueprint error handlers here if needed.
# @main_bp.app_errorhandler(413)
# def bp_request_entity_too_large(error):
#     # Blueprint specific handler if different logic is needed
#     pass
