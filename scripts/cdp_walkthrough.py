#!/usr/bin/env python3
"""
BOLDR — CDP Browser Walkthrough for Demo Recording
Automates browser navigation through n8n, Streamlit, and Swagger UI
while ffmpeg records the screen on Xvfb :99.

Author: Steve Ng, Founder and CEO — Digital Futures Consultancy LLP
"""

import json
import time
import base64
import websocket
import urllib.request
from pathlib import Path

# Configuration
CDP_PORT = 9222
PROJECT_DIR = Path(__file__).parent.parent
OUTPUT_DIR = PROJECT_DIR / "docs" / "demo_video"
FASTAPI_URL = "http://localhost:8000"

# URLs
N8N_URL = "http://localhost:5678"
STREAMLIT_URL = "http://localhost:8501"
SWAGGER_URL = f"{FASTAPI_URL}/docs"

# n8n credentials
N8N_USER = "steve@digitalfutures.sg"
N8N_PASS = "BolDR2026!demo"

# Screenshot delay between actions
DELAY = 3


def cdp(ws, method, params=None, msg_id=1, timeout=10):
    """Send a CDP command and wait for the result."""
    cmd = {"id": msg_id, "method": method}
    if params:
        cmd["params"] = params
    ws.send(json.dumps(cmd))
    
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            ws.set_timeout(1)
            resp = json.loads(ws.recv())
            if resp.get("id") == msg_id:
                return resp
        except websocket.WebSocketTimeoutException:
            continue
        except Exception:
            break
    return None


def screenshot(ws, filename, msg_id=9999):
    """Take a screenshot and save it."""
    resp = cdp(ws, "Page.captureScreenshot", {"format": "png", "quality": 90}, msg_id=msg_id)
    if resp and "result" in resp and "data" in resp.get("result", {}):
        img_data = base64.b64decode(resp["result"]["data"])
        filepath = OUTPUT_DIR / filename
        with open(filepath, "wb") as f:
            f.write(img_data)
        print(f"    Screenshot: {filename} ({len(img_data)//1024} KB)")
        return True
    else:
        print(f"    Screenshot FAILED: {filename}")
        return False


def navigate(ws, url, delay=5, msg_id=1):
    """Navigate to a URL and wait for it to load."""
    cdp(ws, "Page.navigate", {"url": url}, msg_id=msg_id)
    time.sleep(delay)


def evaluate(ws, expression, msg_id=1, timeout=10):
    """Evaluate JavaScript in the page."""
    resp = cdp(ws, "Runtime.evaluate", {
        "expression": expression,
        "awaitPromise": True,
        "returnByValue": True
    }, msg_id=msg_id, timeout=timeout)
    
    if resp and "result" in resp:
        result = resp["result"].get("result", {})
        return result.get("value", result.get("description", str(result)))
    return None


def main():
    print("=" * 60)
    print("  BOLDR — CDP Browser Walkthrough")
    print("  ECHELON 2026 AI Workflow Competition")
    print("=" * 60)
    
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Step 1: Connect to Chromium
    print("\n[1/8] Connecting to Chromium via CDP...")
    try:
        resp = urllib.request.urlopen(f"http://localhost:{CDP_PORT}/json")
        pages = json.loads(resp.read())
    except Exception as e:
        print(f"  ERROR: Cannot connect to Chromium CDP: {e}")
        return
    
    ws_url = None
    for p in pages:
        if p.get("type") == "page":
            ws_url = p.get("webSocketDebuggerUrl")
            break
    
    if not ws_url:
        print("  ERROR: No pages found in Chromium")
        return
    
    ws = websocket.create_connection(ws_url)
    print(f"  Connected!")
    
    # Enable page events
    cdp(ws, "Page.enable", msg_id=1)
    
    # Step 2: Log in to n8n
    print("\n[2/8] Logging into n8n...")
    navigate(ws, f"{N8N_URL}/signin", delay=5, msg_id=10)
    screenshot(ws, "step_02_n8n_login_page.png", msg_id=11)
    
    # Try to fill login form using JavaScript
    result = evaluate(ws, f"""
    (function() {{
        // Find and fill email field
        var inputs = document.querySelectorAll('input');
        var emailFilled = false;
        var passFilled = false;
        
        for (var i = 0; i < inputs.length; i++) {{
            var input = inputs[i];
            var type = (input.type || '').toLowerCase();
            var name = (input.name || '').toLowerCase();
            var placeholder = (input.placeholder || '').toLowerCase();
            var id = (input.id || '').toLowerCase();
            
            // Email field
            if (type === 'email' || name.includes('email') || placeholder.includes('email') || id.includes('email')) {{
                var nativeSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
                nativeSetter.call(input, '{N8N_USER}');
                input.dispatchEvent(new Event('input', {{ bubbles: true }}));
                input.dispatchEvent(new Event('change', {{ bubbles: true }}));
                emailFilled = true;
            }}
            
            // Password field
            if (type === 'password') {{
                var nativeSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
                nativeSetter.call(input, '{N8N_PASS}');
                input.dispatchEvent(new Event('input', {{ bubbles: true }}));
                input.dispatchEvent(new Event('change', {{ bubbles: true }}));
                passFilled = true;
            }}
        }}
        
        // If we found both fields, try to submit
        if (emailFilled && passFilled) {{
            var submitBtn = document.querySelector('button[type="submit"]') || 
                           document.querySelector('button[data-testid="submit"]');
            if (submitBtn) {{
                submitBtn.click();
                return 'Login submitted';
            }}
            return 'Form filled, no submit button found';
        }}
        
        return 'Form fields: email=' + emailFilled + ' pass=' + passFilled + ' total_inputs=' + inputs.length;
    }})()
    """, msg_id=12)
    print(f"  Login JS result: {result}")
    
    time.sleep(8)
    screenshot(ws, "step_02_after_login.png", msg_id=13)
    
    # Step 3: Navigate to n8n workflows list
    print("\n[3/8] n8n Workflows...")
    navigate(ws, f"{N8N_URL}/workflows", delay=5, msg_id=20)
    screenshot(ws, "step_03_n8n_workflows.png", msg_id=21)
    
    # Step 4: Navigate to each workflow individually
    print("\n[4/8] Individual n8n Workflows...")
    workflow_urls = [
        (f"{N8N_URL}/workflow/1", "Chat_Intake"),
        (f"{N8N_URL}/workflow/2", "WhatsApp_Intake"),
        (f"{N8N_URL}/workflow/3", "Email_Intake"),
        (f"{N8N_URL}/workflow/4", "Instagram_Intake"),
        (f"{N8N_URL}/workflow/5", "KB_Gap_Detection"),
    ]
    
    for i, (url, name) in enumerate(workflow_urls):
        print(f"  Workflow {i+1}: {name}")
        navigate(ws, url, delay=5, msg_id=30+i)
        screenshot(ws, f"step_04_workflow_{i+1}_{name}.png", msg_id=40+i)
        time.sleep(2)
    
    # Step 5: Process a live ticket
    print("\n[5/8] Processing live ticket...")
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
        print(f"  Ticket: {result.get('ticket_id')} -> {result.get('question_type')} ({result.get('buyer_persona')})")
        print(f"  Confidence: {result.get('confidence', 0):.2f}")
    except Exception as e:
        print(f"  Error: {e}")
    
    # Step 6: Streamlit Dashboard
    print("\n[6/8] Streamlit Dashboard...")
    navigate(ws, STREAMLIT_URL, delay=10, msg_id=50)
    screenshot(ws, "step_06_streamlit_dashboard.png", msg_id=51)
    
    # Try clicking through Streamlit tabs
    for tab_name in ["Approval Queue", "Ticket Timeline", "Channel Analytics", "Theme Analysis", "Audit Log"]:
        print(f"  Clicking tab: {tab_name}")
        evaluate(ws, f"""
        (function() {{
            var tabs = document.querySelectorAll('[data-baseweb="tab"], .stTab, button[role="tab"]');
            for (var i = 0; i < tabs.length; i++) {{
                if (tabs[i].textContent.includes('{tab_name}')) {{
                    tabs[i].click();
                    return 'Clicked: {tab_name}';
                }}
            }}
            return 'Tab not found: {tab_name}';
        }})()
        """, msg_id=52)
        time.sleep(3)
        safe_name = tab_name.lower().replace(" ", "_")
        screenshot(ws, f"step_06_streamlit_{safe_name}.png", msg_id=53)
    
    # Step 7: Swagger UI
    print("\n[7/8] Swagger UI...")
    navigate(ws, SWAGGER_URL, delay=5, msg_id=60)
    screenshot(ws, "step_07_swagger_ui.png", msg_id=61)
    
    # Scroll through Swagger to show all endpoints
    print("  Scrolling through endpoints...")
    for scroll_pos in [500, 1000, 1500, 2000, 2500, 3000]:
        evaluate(ws, f"window.scrollTo(0, {scroll_pos})", msg_id=62)
        time.sleep(1)
    screenshot(ws, "step_07_swagger_scrolled.png", msg_id=63)
    
    # Step 8: Back to n8n for closing
    print("\n[8/8] Closing - n8n workflows...")
    navigate(ws, f"{N8N_URL}/workflows", delay=5, msg_id=70)
    screenshot(ws, "step_08_n8n_closing.png", msg_id=71)
    
    # Close CDP connection
    ws.close()
    print("\n  CDP connection closed.")
    
    # List all screenshots
    print("\n" + "=" * 60)
    print("  Screenshots Captured:")
    print("=" * 60)
    for f in sorted(OUTPUT_DIR.glob("step_*.png")):
        size_kb = f.stat().st_size / 1024
        print(f"  {f.name} ({size_kb:.0f} KB)")
    
    print(f"\nffmpeg is still recording in the background.")
    print(f"To stop recording: kill $(pgrep -f 'ffmpeg.*x11grab')")


if __name__ == "__main__":
    main()