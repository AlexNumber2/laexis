#!/usr/bin/env bash
# exit on error
set -o errexit

# Install Python dependencies
pip install -r requirements.txt

# Install Playwright browser and its OS-level dependencies
playwright install chromium
playwright install-deps chromium
