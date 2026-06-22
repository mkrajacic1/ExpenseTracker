#!/bin/bash

python seed.py

exec flask --app expense_tracker run --host=0.0.0.0