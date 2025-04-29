# Arabic File Uploader (مُرفِق الملفات)

A modern Arabic RTL web application for uploading files and generating download links using the DDownload API.

## Features

- Modern Arabic UI with full RTL support
- Drag and drop file uploads
- Asynchronous file handling (using Flask async and gevent worker)
- Progress tracking
- Elegant design with responsive layout
- Secure file handling with validation

## Requirements

- Python 3.11 or higher
- Poetry package manager
- DDownload API key

## Project Structure

The application follows a modular structure:
```
arabic-file-uploader/
├── README.md                # Project documentation
├── pyproject.toml           # Poetry configuration file
├── .env                     # Environment variables (API key)
├── run.sh                   # Shell script to build and run the app
├── app/
│   ├── __init__.py          # Application initialization
│   ├── main.py              # Main application entry point
│   ├── config.py            # Configuration manager
│   ├── static/              # Static files
│   │   ├── css/
│   │   │   └── main.css     # Main stylesheet
│   │   ├── js/
│   │   │   └── main.js      # Client-side JavaScript
│   │   ├── fonts/           # Arabic fonts folder (add fonts here)
│   │   └── img/             # Images folder (add images here)
│   ├── templates/
│   │   ├── index.html       # Main page template
│   │   └── error.html       # Error page template
│   └── modules/
│       ├── __init__.py
│       ├── uploader.py      # File upload module
│       └── logger.py        # Logging module
└── logs/                    # Log files directory
```

## Setup and Installation

1.  Clone this repository
2.  Make sure you have Python 3.11+ and Poetry installed
3.  Create a `.env` file in the project root with your DDownload API key:
    ```
    DDOWNLOAD_API_KEY=your_api_key_here
    ```
4.  Make the run script executable: `chmod +x run.sh`
5.  Run the application: `./run.sh`

    This will install dependencies using Poetry and start the Gunicorn server.

## Development

-   For development mode, set `DEBUG=true` in your `.env` file.
-   The application will log to both console (if DEBUG is true) and files in the `logs/` directory.
-   The Flask development server can be run directly for easier debugging (though it's not recommended for production):
    ```bash
    poetry run flask run --debug
    ```

## License

This project is licensed under the MIT License.
