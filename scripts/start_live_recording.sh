#!/bin/bash
# BOLDR — Live Screen Recording Script
# Records n8n workflows, Streamlit dashboard, and Swagger UI using Chromium on Xvfb
#
# Prerequisites:
#   - Xvfb running on :99 (1920x1080x24)
#   - Chromium browser installed
#   - All BOLDR services running (FastAPI :8000, n8n :5678, Streamlit :8501)
#   - ffmpeg installed
#
# Author: Steve Ng, Founder and CEO — Digital Futures Consultancy LLP

set -e

DISPLAY=:99
RECORDING_DIR="/home/steve/.openclaw/workspace/e27/1. BOLDR/BOLDR/docs/demo_video"
FINAL_VIDEO="${RECORDING_DIR}/BOLDR_demo_live.mp4"
HIGHLIGHT_VIDEO="${RECORDING_DIR}/BOLDR_demo_live_highlight.mp4"

echo "============================================================"
echo "  BOLDR — Live Screen Recording"
echo "  ECHELON 2026 AI Workflow Competition"
echo "============================================================"
echo ""
echo "Display: $DISPLAY"
echo "Output: $FINAL_VIDEO"
echo ""

# Create recording directory
mkdir -p "$RECORDING_DIR"

# Start ffmpeg screen recording in background
echo "Starting screen recording..."
ffmpeg -y \
  -f x11grab \
  -video_size 1920x1080 \
  -framerate 24 \
  -i :99 \
  -c:v libx264 \
  -preset medium \
  -crf 23 \
  -pix_fmt yuv420p \
  -movflags +faststart \
  "${RECORDING_DIR}/raw_recording.mp4" &
FFMPEG_PID=$!
echo "  Recording PID: $FFMPEG_PID"
sleep 3

# Start Chromium
echo "Starting Chromium browser..."
chromium-browser \
  --no-sandbox \
  --disable-gpu \
  --disable-dev-shm-usage \
  --window-size=1920,1080 \
  --start-maximized \
  --display=$DISPLAY \
  "http://localhost:5678" &
CHROME_PID=$!
echo "  Chromium PID: $CHROME_PID"
sleep 8

echo ""
echo "Recording started. Chromium is open on n8n."
echo ""
echo "MANUAL STEPS REQUIRED:"
echo "  1. Log in to n8n: steve@digitalfutures.sg / BolDR2026!"
echo "  2. Navigate through the 5 workflows"
echo "  3. Open Streamlit dashboard: http://localhost:8501"
echo "  4. Navigate through all 9 tabs"
echo "  5. Open Swagger UI: http://localhost:8000/docs"
echo "  6. Test some endpoints"
echo ""
echo "When done, press Ctrl+C to stop recording."
echo ""

# Wait for user to stop
wait $FFMPEG_PID 2>/dev/null || true

echo ""
echo "Recording stopped."
echo "Raw video saved to: ${RECORDING_DIR}/raw_recording.mp4"

# Trim to final video
if [ -f "${RECORDING_DIR}/raw_recording.mp4" ]; then
    DURATION=$(ffprobe -v quiet -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "${RECORDING_DIR}/raw_recording.mp4" 2>/dev/null || echo "0")
    echo "Duration: ${DURATION}s"
    
    # Copy raw to final
    cp "${RECORDING_DIR}/raw_recording.mp4" "$FINAL_VIDEO"
    echo "Final video: $FINAL_VIDEO"
    
    # Create highlight (first 60 seconds)
    if [ "$(echo "$DURATION > 60" | bc -l 2>/dev/null || echo 0)" -eq 1 ]; then
        ffmpeg -y -i "${RECORDING_DIR}/raw_recording.mp4" -t 60 -c:v libx264 -preset medium -crf 23 -pix_fmt yuv420p -movflags +faststart "$HIGHLIGHT_VIDEO" 2>/dev/null
        echo "Highlight: $HIGHLIGHT_VIDEO (60s)"
    fi
fi

echo ""
echo "Done!"