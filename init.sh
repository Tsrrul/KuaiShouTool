#!/bin/bash

if [! -d "*.venv"]; then
  python -m venv .venv
fi

echo ""
read  -n 1 -s -r p"Press any key to continue"
