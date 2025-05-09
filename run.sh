#!/bin/bash

# Colors for terminal output
GREEN=' 33[0;32m'
YELLOW=' 33[1;33m'
RED=' 33[0;31m'
NC=' 33[0m' # No Color

echo -e "${YELLOW}Starting Arabic File Uploader setup...${NC}"

# Check if poetry is installed
if ! command -v poetry &> /dev/null; then
    echo -e "${RED}Poetry is not installed. Please install it first.${NC}"
    echo "Visit https://python-poetry.org/docs/#installation for installation instructions."
    exit 1
fi

# Make sure .env file exists
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}Creating .env file...${NC}"
    echo "DDOWNLOAD_API_KEY=the_api_key" > .env
    echo -e "${GREEN}.env file created successfully.${NC}"
fi

# Install dependencies
echo -e "${YELLOW}Installing dependencies...${NC}"
poetry install

# Ensure logs directory exists
mkdir -p logs

# Start the application
echo -e "${GREEN}Starting the application...${NC}"
# Using gevent worker as per original brief
poetry run gunicorn --worker-class=gevent --workers=2 --bind=0.0.0.0:5000 "app:create_app()"

echo -e "${GREEN}Application stopped.${NC}"
