#!/bin/bash
# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Change to the script's directory to ensure paths are correct
cd "$SCRIPT_DIR"

# Activate virtual environment if it exists
if [ -d ".venv" ]; then
  echo "Activating virtual environment..."
  source .venv/bin/activate
fi

# Run the python application
echo "Starting JoyBridge..."
python3 main.py config.yaml

source /home/jetson/workspace/JoyBridge_CHAOKE/venv/bin/activate
python main.py config.yaml
read -p "Press Enter to close..."