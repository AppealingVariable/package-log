#!/bin/bash
VENV_DIR="$HOME/.package-log/.venv"
PROGRAM="$HOME/.package-log/PackageLogGui.pyw"
STARTIN="$HOME/.package-log"

cd "$STARTIN"
source "$VENV_DIR/bin/activate" && python $"PROGRAM"