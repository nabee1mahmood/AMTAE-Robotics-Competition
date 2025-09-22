#!/bin/bash

echo "🛑 Stopping udp.py and controller.py..."

pkill -f udp.py
pkill -f controller.py

echo "✅ Both scripts stopped."
