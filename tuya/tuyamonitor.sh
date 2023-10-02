#!/bin/bash

# Path to your virtual environment
VENV_PATH="/home/nathass/.venv"

# Activate the virtual environment
source $VENV_PATH/bin/activate

# Path to your python script
PYTHON_SCRIPT_PATH="/home/nathass/tuyamonitor.py"

# Run the python script
python $PYTHON_SCRIPT_PATH

# Deactivate the virtual environment (optional)
deactivate
