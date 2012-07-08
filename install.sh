#!/bin/bash
cd $(dirname $0)

INSTALL_DIR="$HOME/.scons/site_scons/site_tools"

mkdir -p "$INSTALL_DIR"
cp arduino.py "$INSTALL_DIR"
