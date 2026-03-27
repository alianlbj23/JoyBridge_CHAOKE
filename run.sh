#!/bin/bash
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR" || exit 1

VENV_PATH=""
if [ -f "$SCRIPT_DIR/.venv/bin/activate" ]; then
  VENV_PATH="$SCRIPT_DIR/.venv"
elif [ -f "$SCRIPT_DIR/venv/bin/activate" ]; then
  VENV_PATH="$SCRIPT_DIR/venv"
fi

if [ -n "$VENV_PATH" ]; then
  echo "Activating virtual environment: $VENV_PATH"
  # shellcheck disable=SC1090
  source "$VENV_PATH/bin/activate"
else
  echo "No local virtual environment found (.venv or venv). Running with system Python."
fi

echo "Starting JoyBridge..."
python main.py config.yaml
