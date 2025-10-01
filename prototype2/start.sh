#!/bin/bash

cd /home/x/prototype|| exit 1

echo "▶️ Starting udp.py..."
/usr/bin/python3 udp.py &

echo "▶️ Starting controller.py..."
/usr/bin/python3 controller.py &

echo "✅ Both scripts started."
wait



