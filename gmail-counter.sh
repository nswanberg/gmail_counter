#!/bin/bash

source /Users/nate/.pyenv/versions/gmail-count/bin/activate
SCRIPT_DIR="$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
python $SCRIPT_DIR/gmail-counter.py
