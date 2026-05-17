#!/usr/bin/env python3
"""
BOLDR — CDP-based Browser Automation for Live Demo Recording
Uses Chrome DevTools Protocol to automate Chromium on Xvfb :99,
while ffmpeg records the screen.

Author: Steve Ng, Founder and CEO — Digital Futures Consultancy LLP
"""

import json
import time
import subprocess
import sys
import os
import websocket
import urllib.request
from pathlib import Path

# Configuration
DISPLAY = ":99"
CDP_PORT = 9222
WIDTH, HEIGHT = 1920, 1080
PROJECT_DIR = Path(__file__).parent.parent
OUTPUT_DIR = PROJECT_DIR / "docs" / "demo_video"

# URLs
N8N_URL = "http://localhost:5678"
FASTAPI_URL = "http://localhost:8000"
STREAMLIT_URL = "http://localhost:8501"
SWAGGER_URL = f"{FASTAPI_URL}/docs"

# n8n credentials
N8N_USER = "steve@digitalfutures.sg"
N8N_PASS = "BolDR2026!demo"


def get_ws_url():
    """Get the WebSocket debugger URL for the first page."""
    try:
        resp = urllib.request.urlopen(f"http://localhost:{CDP_PORT}/json")
        pages = json.loads(resp.read())
        for page in pages:
            if page.get("type") == "page":
                return page.get("webSocketDebuggerUrl")
    except Exception as e:
        print(f"  Error getting pages: {e}")
    return None


def create_new_page():
    """Create a new tab and return its WebSocket URL."""
    try:
        # Use CDP to create a new target
        ws_url = f"ws://localhost:{CDP_PORT}/devtools/browser"
        # Actually, let's use the HTTP endpoint
        resp = urllib.request.urlopen(f"http://localhost:{CDP_PORT}/json/new?{STREAMLIT_URL}")
        page = json.loads(resp.read())
        return page.get("webSocketDebuggerUrl")
    except Exception as e:
        print(f"  Error creating page: {e}")
        return None


def cdp_command(ws, method, params=None, msg_id=1):
    """Send a CDP command and return the result."""
    cmd = {"id": msg_id, "method": method}
    if params:
        cmd["params"] = params
    ws.send(json.dumps(cmd))
    # Read responses until we get our result
    while True:
        resp = json.loads(ws.recv())
        if resp.get("id") == msg_id:
            return resp
        # Skip events


def main():
    print("=" * 60)
    print("  BOLDR — CDP Browser Automation for Demo Recording")
    print("=" * 60)
    
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Step 1: Connect to the existing n8n page
    print("\n[1/7] Connecting to Chromium via CDP...")
    ws_url = get_ws_url()
    if not ws_url:
        print("  ERROR: No pages found. Is Chromium running with --remote-debugging-port?")
        return
    
    print(f"  Connected to: {ws_url[:60]}...")
    ws = websocket.create_connection(ws_url)
    
    # Step 2: Log in to n8n
    print("\n[2/7] Logging into n8n...")
    
    # First, navigate to n8n login page
    cdp_command(ws, "Page.navigate", {"url": N8N_URL}, msg_id=1)
    time.sleep(5)
    
    # Fill in login form using JavaScript
    js_login = f"""
    (function() {{
        // Wait for the login form to appear
        function tryLogin() {{
            // Try to find email input
            var inputs = document.querySelectorAll('input[type="email"], input[name="email"], input[placeholder*="email"], input[placeholder*="Email"]');
            if (inputs.length === 0) {{
                // Try all text inputs
                inputs = document.querySelectorAll('input[type="text"]');
            }}
            if (inputs.length > 0) {{
                // Set email
                var nativeInputValueSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
                nativeInputValueSetter.call(inputs[0], '{N8N_USER}');
                inputs[0].dispatchEvent(new Event('input', {{ bubbles: true }}));
                inputs[0].dispatchEvent(new Event('change', {{ bubbles: true }}));
                
                // Find password input
                var passInputs = document.querySelectorAll('input[type="password"]');
                if (passInputs.length > 0) {{
                    nativeInputValueSetter.call(passInputs[0], '{N8N_PASS}');
                    passInputs[0].dispatchEvent(new Event('input', {{ bubbles: true }}));
                    passInputs[0].dispatchEvent(new Event('change', {{ bubbles: true }}));
                    
                    // Click submit button
                    var submitBtn = document.querySelector('button[type="submit"]') || 
                                    document.querySelector('button[data-testid="submit"]');
                    if (submitBtn) {{
                        submitBtn.click();
                        return 'Login submitted';
                    }}
                }}
            }}
            return 'Form not found, retrying...';
        }}
        return tryLogin();
    }})()
    """
    
    result = cdp_command(ws, "Runtime.evaluate", {"expression": js_login, "awaitPromise": True}, msg_id=2)
    print(f"  Login result: {result.get('result', {}).get('result', {}).get('value', 'unknown')}")
    time.sleep(8)
    
    # Take screenshot to verify
    screenshot_result = cdp_command(ws, "Page.captureScreenshot", {"format": "png", "quality": 90}, msg_id=3)
    if screenshot_result.get("result", {}).get("result"):
        import base64
        img_data = base64.b64decode(screenshot_result["result"]["result"]["data"])
        with open(OUTPUT_DIR / "cdp_after_login.png", "wb") as f:
            f.write(img_data)
        print(f"  Screenshot saved: cdp_after_login.png ({len(img_data)} bytes)")
    
    # Step 3: Navigate through n8n workflows
    print("\n[3/7] Navigating through n8n workflows...")
    
    # Get list of workflows from n8n API
    try:
        # First, get n8n API key by logging in
        login_data = json.dumps({"email": N8N_USER, "password": N8N_PASS}).encode()
        req = urllib.request.Request(
            f"{N8N_URL}/rest/login",
            data=login_data,
            headers={"Content-Type": "application/json"}
        )
        resp = urllib.request.urlopen(req)
        login_resp = json.loads(resp.read())
        # n8n returns a session cookie, we'll need it for API calls
        print("  n8n login via API: success")
    except Exception as e:
        print(f"  n8n login via API: {e}")
    
    # Navigate to the workflows page
    cdp_command(ws, "Page.navigate", {"url": f"{N8N_URL}/workflows"}, msg_id=10)
    time.sleep(5)
    
    # Screenshot workflows list
    screenshot_result = cdp_command(ws, "Page.captureScreenshot", {"format": "png"}, msg_id=11)
    if screenshot_result.get("result", {}).get("result"):
        import base64
        img_data = base64.b64decode(screenshot_result["result"]["result"]["data"])
        with open(OUTPUT_DIR / "cdp_workflows_list.png", "wb") as f:
            f.write(img_data)
        print(f"  Workflows list screenshot saved ({len(img_data)} bytes)")
    
    # Step 4: Open Streamlit Dashboard
    print("\n[4/7] Opening Streamlit Dashboard...")
    cdp_command(ws, "Page.navigate", {"url": STREAMLIT_URL}, msg_id=20)
    time.sleep(8)
    
    # Screenshot Streamlit
    screenshot_result = cdp_command(ws, "Page.captureScreenshot", {"format": "png"}, msg_id=21)
    if screenshot_result.get("result", {}).get("result"):
        import base64
        img_data = base64.b64decode(screenshot_result["result"]["result"]["data"])
        with open(OUTPUT_DIR / "cdp_streamlit_dashboard.png", "wb") as f:
            f.write(img_data)
        print(f"  Streamlit dashboard screenshot saved ({len(img_data)} bytes)")
    
    # Step 5: Open Swagger UI
    print("\n[5/7] Opening Swagger UI...")
    cdp_command(ws, "Page.navigate", {"url": SWAGGER_URL}, msg_id=30)
    time.sleep(5)
    
    # Screenshot Swagger
    screenshot_result = cdp_command(ws, "Page.captureScreenshot", {"format": "png"}, msg_id=31)
    if screenshot_result.get("result", {}).get("result"):
        import base64
        img_data = base64.b64decode(screenshot_result["result"]["result"]["data"])
        with open(OUTPUT_DIR / "cdp_swagger_ui.png", "wb") as f:
            f.write(img_data)
        print(f"  Swagger UI screenshot saved ({len(img_data)} bytes)")
    
    # Step 6: Process a live ticket and show the result
    print("\n[6/7] Processing live ticket via API...")
    ticket_data = json.dumps({
        "message": "Hi, I'm interested in the BOLDR Venture. Is it suitable for diving?",
        "channel": "chat",
        "sender_name": "Demo User"
    }).encode()
    
    req = urllib.request.Request(
        f"{FASTAPI_URL}/api/v1/intake",
        data=ticket_data,
        headers={"Content-Type": "application/json"}
    )
    try:
        resp = urllib.request.urlopen(req, timeout=30)
        result = json.loads(resp.read())
        print(f"  Ticket: {result.get('ticket_id')} → {result.get('question_type')} ({result.get('buyer_persona')})")
        print(f"  Confidence: {result.get('confidence', 0):.2f}")
        print(f"  Channel: {result.get('channel')}")
    except Exception as e:
        print(f"  Error: {e}")
    
    # Navigate back to n8n to show the workflow processing
    print("  Navigating back to n8n to show processing...")
    cdp_command(ws, "Page.navigate", {"url": f"{N8N_URL}/workflows"}, msg_id=40)
    time.sleep(5)
    
    # Step 7: Navigate to each n8n workflow
    print("\n[7/7] Screenshotting individual workflows...")
    
    workflow_names = [
        "Chat Intake",
        "WhatsApp Intake",
        "Email Intake",
        "Instagram Intake",
        "KB Gap Detection"
    ]
    
    for i, name in enumerate(workflow_names):
        print(f"  Opening workflow: {name}")
        # Navigate to workflow by index (1-based)
        cdp_command(ws, "Page.navigate", {"url": f"{N8N_URL}/workflow/{i+1}"}, msg_id=50+i)
        time.sleep(5)
        
        # Screenshot
        screenshot_result = cdp_command(ws, "Page.captureScreenshot", {"format": "png"}, msg_id=60+i)
        if screenshot_result.get("result", {}).get("result"):
            import base64
            img_data = base64.b64decode(screenshot_result["result"]["result"]["data"])
            fname = f"cdp_workflow_{i+1}_{name.lower().replace(' ', '_')}.png"
            with open(OUTPUT_DIR / fname, "wb") as f:
                f.write(img_data)
            print(f"    Saved: {fname} ({len(img_data)} bytes)")
    
    # Final: Back to workflows list
    cdp_command(ws, "Page.navigate", {"url": f"{N8N_URL}/workflows"}, msg_id=100)
    time.sleep(3)
    
    # Close CDP connection
    ws.close()
    print("\n  CDP connection closed.")
    
    print("\n" + "=" * 60)
    print("  Screenshots captured!")
    print("=" * 60)
    
    # List all screenshots
    print("\nScreenshots:")
    for f in sorted(OUTPUT_DIR.glob("cdp_*.png")):
        size_kb = f.stat().st_size / 1024
        print(f"  {f.name} ({size_kb:.0f} KB)")
    
    print("\nffmpeg is still recording in the background.")
    print("To stop: kill $(pgrep -f 'ffmpeg.*x11grab')")


if __name__ == "__main__":
    main()