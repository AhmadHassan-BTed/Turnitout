#!/bin/bash

# Check if python3 is installed
if ! command -v python3 &> /dev/null; then
    echo "[Turnitout] Python3 is not detected on your system."
    echo "[Turnitout] Attempting to install Python3..."
    
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        if command -v brew &> /dev/null; then
            brew install python
        else
            echo "[Turnitout] Homebrew is not installed. Please install Python manually."
            exit 1
        fi
    elif command -v apt-get &> /dev/null; then
        # Debian/Ubuntu
        sudo apt-get update && sudo apt-get install -y python3 python3-pip python3-venv
    elif command -v yum &> /dev/null; then
        # CentOS/RHEL
        sudo yum install -y python3 python3-pip
    else
        echo "[Turnitout] Unsupported OS. Please install Python manually."
        exit 1
    fi
fi

# Initialize virtualenv and dependencies
if [ ! -d "env" ]; then
    python3 -m venv env
fi
source env/bin/activate
pip install -e . &> /dev/null

python3 run.py "$@"
