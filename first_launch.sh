#!/bin/bash

python3.11 -m venv venv
source venv/bin/activate || exit 1
pip install -U pip setuptools wheel || exit 1
pip install -r requirements.txt || exit 1

python3.11 from_env_to_creds.py || exit 1
