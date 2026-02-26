#!/bin/bash
cd $(dirname $0)
pkill -f run_calendar.py || true
python3 ./run_calendar.py > /dev/null 2>&1 &