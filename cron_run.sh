#!/bin/bash
# Move to the project directory
cd /root/project/stockMailing

# Run the script using the virtual environment's python
/root/project/stockMailing/venv/bin/python run_all.py >> /root/project/stockMailing/cron.log 2>&1
