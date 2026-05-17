#!/usr/bin/env python3
"""
BOLDR — Automated Live Demo Recording
Uses Xvfb + Chromium + ffmpeg to record a real browser walkthrough.

Author: Steve Ng, Founder and CEO — Digital Futures Consultancy LLP
"""

import os
import sys
import time
import json
import subprocess
import urllib.request
import urllib.parse
from pathlib import Path

# Configuration
DISPLAY = ":99"
WIDTH, HEIGHT = 1920, 1080
FPS = 24
PROJECT_DIR = Path(__file__).parent.parent
OUTPUT_DIR = PROJECT_DIR / "docs" / "demo_video"
FINAL_VIDEO = OUTPUT_DIR / "BOLDR_demo_live.mp4"
HIGHLIGHT_VIDEO = OUTPUT_DIR / "BOLDR_demo_live_highlight.mp4"

# URLs
N8N_URL = "http://localhost:5678"
FASTAPI_URL = "http://localhost:8000"
STREAMLIT_URL = "http://localhost:8501"
SWAGGER_URL = f"{FASTAPI_URL}/docs"

# n8n credentials
N8N_USER = "steve@digitalfutures.sg"
N8N_PASS = "BolDR2026!demo"


def run(cmd, timeout=30):
    """Run shell command."""
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout,
                          env={**os.environ, "DISPLAY": DISPLAY})
    return result


def api_get(endpoint):
    """Call FastAPI endpoint."""
    try:
        resp = urllib.request.urlopen(f"{FASTAPI_URL}{endpoint}", timeout=5)
        return json.loads(resp.read())
    except:
        return {}


def wait_for_url(url, timeout=30):
    """Wait for a URL to be reachable."""
    start = time.time()
    while time.time() - start < timeout:
        try:
            resp = urllib.request.urlopen(url, timeout=3)
            if resp.status == 200:
                return True
        except:
            pass
        time.sleep(1)
    return False


def xdotool(cmd, window_id=None):
    """Execute xdotool command."""
    if window_id:
        full_cmd = f"DISPLAY={DISPLAY} xdotool {cmd} --window {window_id}"
    else:
        full_cmd = f"DISPLAY={DISPLAY} xdotool {cmd}"
    return run(full_cmd)


def type_text(text, window_id=None):
    """Type text using xdotool."""
    # Escape special characters
    text = text.replace(' ', 'space')
    for char in ['@', '!', '#', '$', '%', '&', '*', '(', ')', '-', '=', '+', '[', ']', '{', '}', '|', ';', ':', '"', "'", '<', '>', ',', '.', '?', '/', '\\', '~', '`']:
        text = text.replace(char, f'\\{char}')
    return xdotool(f"type {text}", window_id)


def key_press(key, window_id=None):
    """Press a key."""
    return xdotool(f"key {key}", window_id)


def get_active_window():
    """Get the active window ID."""
    result = run(f"DISPLAY={DISPLAY} xdotool getactivewindow")
    try:
        return result.stdout.strip()
    except:
        return None


def main():
    print("=" * 60)
    print("  BOLDR — Automated Live Demo Recording")
    print("  ECHELON 2026 AI Workflow Competition")
    print("=" * 60)
    
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Step 1: Verify Xvfb is running
    print("\n[1/8] Checking Xvfb display server...")
    result = run(f"DISPLAY={DISPLAY} xdpyinfo")
    if result.returncode != 0:
        print("  ERROR: Xvfb not running. Start with: Xvfb :99 -screen 0 1920x1080x24 -ac &")
        return
    print("  Xvfb is running on display :99")
    
    # Step 2: Verify all services
    print("\n[2/8] Checking BOLDR services...")
    health = api_get("/api/v1/health")
    if health.get("status") != "healthy":
        print("  ERROR: FastAPI not healthy")
        return
    print(f"  FastAPI: healthy ({health.get('tickets_processed', 0)} tickets)")
    
    n8n_ok = wait_for_url(N8N_URL, timeout=5)
    print(f"  n8n: {'healthy' if n8n_ok else 'NOT reachable'}")
    
    streamlit_ok = wait_for_url(STREAMLIT_URL, timeout=5)
    print(f"  Streamlit: {'healthy' if streamlit_ok else 'NOT reachable'}")
    
    # Step 3: Start ffmpeg recording
    print("\n[3/8] Starting screen recording...")
    recording_path = OUTPUT_DIR / "raw_live_recording.mp4"
    
    ffmpeg_cmd = (
        f"DISPLAY={DISPLAY} ffmpeg -y "
        f"-f x11grab -video_size {WIDTH}x{HEIGHT} -framerate {FPS} "
        f"-i {DISPLAY} "
        f"-c:v libx264 -preset medium -crf 23 -pix_fmt yuv420p "
        f"-movflags +faststart "
        f"{recording_path}"
    )
    
    ffmpeg_proc = subprocess.Popen(
        ffmpeg_cmd.split(),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        env={**os.environ, "DISPLAY": DISPLAY}
    )
    print(f"  Recording started (PID: {ffmpeg_proc.pid})")
    time.sleep(2)
    
    # Step 4: Start Chromium
    print("\n[4/8] Launching Chromium browser...")
    
    # Kill any existing Chromium instances
    run("pkill -f chromium 2>/dev/null || true", timeout=5)
    time.sleep(2)
    
    chrome_cmd = (
        f"DISPLAY={DISPLAY} chromium-browser "
        f"--no-sandbox --disable-gpu --disable-dev-shm-usage "
        f"--window-size={WIDTH},{HEIGHT} --start-maximized "
        f"--disable-extensions --disable-software-rasterizer "
        f"--no-first-run --no-default-browser-check "
        f'"{N8N_URL}"'
    )
    
    chrome_proc = subprocess.Popen(
        chrome_cmd,
        shell=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        env={**os.environ, "DISPLAY": DISPLAY}
    )
    print(f"  Chromium started (PID: {chrome_proc.pid})")
    
    # Wait for browser to load
    print("  Waiting for browser to load...")
    time.sleep(12)
    
    # Step 5: n8n Login
    print("\n[5/8] Logging into n8n...")
    
    # Find the Chromium window
    window_id = get_active_window()
    if window_id:
        print(f"  Active window: {window_id}")
    
    # If n8n has a login page, we need to fill it
    # The page should be at localhost:5678 - n8n login form
    # Click on email field and type
    time.sleep(3)
    
    if window_id:
        # Click in the center-ish area where the email field typically is
        xdotool(f"mousemove 960 400")
        time.sleep(0.5)
        xdotool("click 1")
        time.sleep(0.5)
        # Type email
        xdotool(f"type --window {window_id} {N8N_USER.replace('@', '\\@')}")
        time.sleep(0.5)
        # Tab to password field
        key_press("Tab", window_id)
        time.sleep(0.5)
        # Type password
        xdotool(f"type --window {window_id} {N8N_PASS.replace('!', '\\!')}")
        time.sleep(0.5)
        # Press Enter to login
        key_press("Return", window_id)
        time.sleep(5)
    
    print("  Login attempt complete")
    
    # Take a screenshot to verify
    run(f"DISPLAY={DISPLAY} ffmpeg -y -f x11grab -video_size {WIDTH}x{HEIGHT} -i {DISPLAY} -frames:v 1 {OUTPUT_DIR}/screenshot_after_login.png", timeout=10)
    print("  Screenshot saved: screenshot_after_login.png")
    
    # Step 6: Navigate through n8n workflows
    print("\n[6/8] Navigating through n8n workflows...")
    
    workflows = [
        ("Chat Intake", f"{N8N_URL}/workflow/1"),
        ("WhatsApp Intake", f"{N8N_URL}/workflow/2"),
        ("Email Intake", f"{N8N_URL}/workflow/3"),
        ("Instagram Intake", f"{N8N_URL}/workflow/4"),
        ("KB Gap Detection", f"{N8N_URL}/workflow/5"),
    ]
    
    for name, url in workflows:
        print(f"  Navigating to: {name}")
        if window_id:
            # Open new tab with Ctrl+T
            key_press("ctrl+t", window_id)
            time.sleep(1)
            # Type URL
            xdotool(f"type --window {window_id} {url}")
            time.sleep(0.5)
            key_press("Return", window_id)
            time.sleep(5)
    
    # Step 7: Open Streamlit Dashboard
    print("\n[7/8] Opening Streamlit Dashboard...")
    
    if window_id:
        # Open new tab
        key_press("ctrl+t", window_id)
        time.sleep(1)
        xdotool(f"type --window {window_id} {STREAMLIT_URL}")
        time.sleep(0.5)
        key_press("Return", window_id)
        time.sleep(8)
    
    # Navigate through Streamlit tabs
    # We'll scroll and click through the tabs
    streamlit_tabs = [
        "Live Pipeline", "Approval Queue", "Ticket Timeline",
        "Channel Analytics", "Theme Analysis", "KB Management",
        "Gap Log", "Marketing Brief", "Audit Log"
    ]
    
    for tab_name in streamlit_tabs:
        print(f"  Tab: {tab_name}")
        time.sleep(3)
        # Scroll down slowly
        for _ in range(3):
            key_press("Page_Down", window_id)
            time.sleep(1)
        for _ in range(3):
            key_press("Page_Up", window_id)
            time.sleep(1)
    
    # Step 8: Open Swagger UI
    print("\n[8/8] Opening Swagger UI...")
    
    if window_id:
        key_press("ctrl+t", window_id)
        time.sleep(1)
        xdotool(f"type --window {window_id} {SWAGGER_URL}")
        time.sleep(0.5)
        key_press("Return", window_id)
        time.sleep(5)
    
    # Scroll through Swagger UI
    print("  Scrolling through API endpoints...")
    for _ in range(15):
        key_press("Page_Down", window_id)
        time.sleep(1)
    
    # Process a live ticket to show the pipeline in action
    print("\n  Processing live ticket...")
    ticket_data = {
        "message": "Hi, I'm interested in the BOLDR Venture. Is it suitable for diving?",
        "channel": "chat",
        "sender_name": "DemoUser"
    }
    result = run(
        f"curl -s -X POST {FASTAPI_URL}/api/v1/intake "
        f"-H 'Content-Type: application/json' "
        f"-d '{json.dumps(ticket_data)}'"
    )
    try:
        parsed = json.loads(result.stdout)
        print(f"  Live ticket: {parsed.get('ticket_id', '?')} → {parsed.get('question_type', '?')} ({parsed.get('buyer_persona', '?')})")
    except:
        print(f"  Live ticket processed")
    
    time.sleep(3)
    
    # Switch back to n8n to show it processing
    print("  Switching back to n8n...")
    if window_id:
        key_press("ctrl+1", window_id)  # Switch to first tab
        time.sleep(5)
    
    # Final: stop recording
    print("\nStopping recording...")
    
    # Give it a moment
    time.sleep(3)
    
    # Stop ffmpeg gracefully
    ffmpeg_proc.terminate()
    try:
        ffmpeg_proc.wait(timeout=10)
    except:
        ffmpeg_proc.kill()
    
    # Also stop Chromium
    chrome_proc.terminate()
    try:
        chrome_proc.wait(timeout=5)
    except:
        chrome_proc.kill()
    
    print(f"\nRaw recording saved to: {recording_path}")
    
    # Check if recording was created
    if recording_path.exists() and recording_path.stat().st_size > 0:
        size_mb = recording_path.stat().st_size / (1024 * 1024)
        print(f"  Size: {size_mb:.1f} MB")
        
        # Get duration
        result = run(f"ffprobe -v quiet -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 {recording_path}", timeout=10)
        try:
            duration = float(result.stdout.strip())
            print(f"  Duration: {duration:.1f} seconds")
        except:
            duration = 0
        
        # Create highlight version (first 60 seconds)
        if duration > 60:
            print("\nCreating 60-second highlight reel...")
            run(
                f"ffmpeg -y -i {recording_path} -t 60 -c:v libx264 -preset medium -crf 23 "
                f"-pix_fmt yuv420p -movflags +faststart {HIGHLIGHT_VIDEO}",
                timeout=60
            )
            if HIGHLIGHT_VIDEO.exists():
                h_size = HIGHLIGHT_VIDEO.stat().st_size / (1024 * 1024)
                print(f"  Highlight: {HIGHLIGHT_VIDEO} ({h_size:.1f} MB)")
        
        # Copy raw to final
        import shutil
        shutil.copy2(recording_path, FINAL_VIDEO)
        print(f"\n  Final video: {FINAL_VIDEO} ({size_mb:.1f} MB)")
        
        print("\nDone! Videos created:")
        print(f"  Full recording: {FINAL_VIDEO} ({duration:.0f}s)")
        if HIGHLIGHT_VIDEO.exists():
            print(f"  60s highlight: {HIGHLIGHT_VIDEO}")
    else:
        print("\n  ERROR: Recording file is empty or missing")
        print("  This usually means Chromium didn't render properly on the virtual display")
        print("  Check the screenshot_after_login.png to verify the browser rendered")


if __name__ == "__main__":
    main()