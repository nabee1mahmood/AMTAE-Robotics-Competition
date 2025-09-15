#!/bin/bash
# Upload fixed sketch name: arduio.ino

SKETCH="arduino.ino"
PORT="/dev/ttyUSB0"
BOARD="arduino:avr:nano"

echo "🔨 Compiling $SKETCH ..."
arduino-cli compile --fqbn $BOARD $SKETCH

if [ $? -eq 0 ]; then
  echo "⬆️ Uploading to $PORT ..."
  arduino-cli upload -p $PORT --fqbn $BOARD $SKETCH
else
  echo "❌ Compile failed"
fi
