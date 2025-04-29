"""
File upload module.
Handles file upload operations and DDownload API integration.
Uses aiohttp for async server check and requests for blocking file upload.
"""
import asyncio
import aiohttp
import requests # Using requests for the file upload part as in the brief
from typing import Dict, Any, Tuple
from ..config import settings
from ..modules.logger import app_logger

class FileUploader:
    """Handles file uploads to DDownload API."""
    
    def __init__(self):
        """Initialize the uploader with API key and URLs."""
        self.api_key = settings.DDOWNLOAD_API_KEY
        self.api_url = settings.DDOWNLOAD_API_URL
        self.download_url_base = settings.DDOWNLOAD_DOWNLOAD_URL
    
    def _validate_file(self, filename: str) -> bool:
        """
        Validate if the file has an allowed extension.
        
        Args:
            filename: Name of the file to validate
            
        Returns:
            bool: True if file extension is allowed, False otherwise
        """
        # Check if filename is not empty and contains a dot
        if not filename or '.' not in filename:
            app_logger.warning(f"Invalid filename rejected (no extension): {filename}")
            return False
        
        # Extract extension and check against allowed set
        ext = filename.rsplit(".", 1)[1].lower()
        allowed = ext in settings.ALLOWED_EXTENSIONS
        if not allowed:
            app_logger.warning(f"Invalid file type rejected: {filename} (extension: {ext})")
        return allowed
    
    async def get_upload_server(self) -> Tuple[bool, Dict[str, Any]]:
        """
        Asynchronously get upload server details from DDownload API.
        
        Returns:
            Tuple[bool, Dict]: Success status and server information or error message.
        """
        if not self.api_key:
            app_logger.error("DDownload API Key is missing.")
            return False, {"error": "API Key not configured"}

        server_url = f"{self.api_url}/upload/server?key={self.api_key}"
        app_logger.debug(f"Requesting upload server from: {server_url}")
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(server_url, timeout=30) as response: # Added timeout
                    response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
                    server_info = await response.json()
                    app_logger.debug(f"Upload server response: {server_info}")
                    
                    # DDownload API v2 uses 'msg' for status message and 'status' code
                    if server_info.get('status') == 200 and server_info.get('result'):
                        app_logger.info("Successfully obtained upload server.")
                        return True, {
                            "upload_url": server_info['result'],
                            "sess_id": server_info.get('sess_id') # sess_id might not always be present
                        }
                    else:
                        error_msg = server_info.get('msg', "Unknown error from DDownload API")
                        app_logger.error(f"Failed to get upload server: {error_msg} (Status: {server_info.get('status')})")
                        return False, {"error": f"API Error: {error_msg}"}
                        
        except aiohttp.ClientError as e:
            app_logger.error(f"Network error getting upload server: {str(e)}")
            return False, {"error": f"Network error: {str(e)}"}
        except asyncio.TimeoutError:
            app_logger.error("Timeout getting upload server.")
            return False, {"error": "Request timed out"}
        except Exception as e:
            app_logger.error(f"Unexpected error getting upload server: {str(e)}", exc_info=True)
            return False, {"error": "An unexpected error occurred"}
    
    # This part remains synchronous as per the brief, using requests
    # It will block the event loop if run within an async context without care.
    # Consider running this in a thread pool executor in a real async app.
    def upload_file_sync(self, file_data, filename: str, upload_url: str, sess_id: str = None) -> Tuple[bool, Dict[str, Any]]:
        """
        Synchronously uploads file data using the requests library.

        Args:
            file_data: The file stream/data to upload.
            filename: The name of the file.
            upload_url: The URL provided by get_upload_server.
            sess_id: The session ID from get_upload_server (optional).

        Returns:
            Tuple[bool, Dict]: Success status and upload results or error message.
        """
        app_logger.debug(f"Starting synchronous upload for {filename} to {upload_url}")
        data = {
            'utype': 'prem', # Or 'anon' depending on API key type
        }
        if sess_id:
            data['sess_id'] = sess_id
            
        files = {'file': (filename, file_data)}
        
        try:
            # Using requests.post for the actual file upload (blocking)
            upload_response = requests.post(upload_url, data=data, files=files, timeout=300) # 5 min timeout for upload
            upload_response.raise_for_status()
            upload_result = upload_response.json()
            app_logger.debug(f"Upload response data: {upload_result}")

            # Check response format - it's often a list
            if isinstance(upload_result, list) and upload_result:
                first_result = upload_result[0]
                if first_result.get('file_status') == 'OK' and first_result.get('file_code'):
                    file_code = first_result['file_code']
                    download_link = f"{self.download_url_base}/{file_code}"
                    app_logger.info(f"File '{filename}' uploaded successfully. Code: {file_code}")
                    return True, {
                        "file_code": file_code,
                        "download_link": download_link
                    }
                else:
                    error_msg = first_result.get('error', "Upload failed according to API status")
                    app_logger.error(f"Upload failed for '{filename}': {error_msg}")
                    return False, {"error": f"API Upload Error: {error_msg}"}
            else:
                 app_logger.error(f"Unexpected API response format during upload: {upload_result}")
                 return False, {"error": "Unexpected API response format"}

        except requests.exceptions.RequestException as e:
            app_logger.error(f"Error during requests file upload for '{filename}': {str(e)}")
            return False, {"error": f"Upload network error: {str(e)}"}
        except Exception as e:
            app_logger.error(f"Unexpected error during synchronous upload for '{filename}': {str(e)}", exc_info=True)
            return False, {"error": "An unexpected error occurred during upload"}

    async def upload_file(self, file_data, filename: str) -> Tuple[bool, Dict[str, Any]]:
        """
        Orchestrates the file upload process: validates, gets server (async), uploads (sync).
        
        Args:
            file_data: File data object (e.g., file stream).
            filename: Name of the file.
            
        Returns:
            Tuple[bool, Dict]: Success status and upload results or error message.
        """
        if not self._validate_file(filename):
            return False, {"error": "نوع الملف غير مسموح به"} # File type not allowed (Arabic)
        
        app_logger.info(f"Attempting to upload file: {filename}")
        
        # Get upload server asynchronously
        success, server_info = await self.get_upload_server()
        if not success:
            # server_info already contains the error message
            return False, server_info 
        
        upload_url = server_info.get("upload_url")
        sess_id = server_info.get("sess_id")

        if not upload_url:
             app_logger.error("Upload URL not found in server info response.")
             return False, {"error": "Could not retrieve upload URL"}

        # Run the synchronous upload part in a separate thread 
        # to avoid blocking the main async event loop.
        loop = asyncio.get_running_loop()
        try:
            # Use loop.run_in_executor to run the blocking requests.post call
            success, result = await loop.run_in_executor(
                None, # Use default thread pool executor
                self.upload_file_sync, 
                file_data, 
                filename, 
                upload_url, 
                sess_id
            )
            return success, result
        except Exception as e:
            # Catch potential errors from run_in_executor itself
            app_logger.error(f"Error running upload_file_sync in executor: {str(e)}", exc_info=True)
            return False, {"error": "Failed to execute upload task"}

# Create uploader instance for use in the application
uploader = FileUploader()
