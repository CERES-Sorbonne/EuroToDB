#!/bin/bash

python3.11 -m venv venv
source venv/bin/activate || exit 1
pip install -U pip setuptools wheel || exit 1
pip install -r requirements.txt || exit 1
