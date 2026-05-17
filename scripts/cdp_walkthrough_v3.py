#!/usr/bin/env python3
"""
BOLDR — CDP Walkthrough V3 (Robust, Event-Driven)
Navigates through the app and captures screenshots.
"""

import json, websocket, urllib.request, base64, time
from pathlib import Path

OUTPUT_DIR = Path(__file__).parent.parent / "docs" / "demo_video"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

FASTAPI = "http://localhost:8000"
N8N = "http://localhost:5678"
STREAMLIT = "http://localhost:8501"

def get_ws():
    resp = urllib.request.urlopen("http://localhost:9222/json")
    for p in json.loads(resp.read()):
        if p.get("type") == "page":
            return p["webSocketDebuggerUrl"]
    return None

def cdp_simple(ws, method, params=None, mid=1):
    """Send CDP command and wait for matching response ID."""
    cmd = {"id": mid, "method": method}
    if params: cmd["params"] = params
    ws.send(json.dumps(cmd))

def read_response(ws, expected_id, timeout=10):
    """Read from websocket until we get the expected response ID."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            ws.settimeout(1)
            r = json.loads(ws.recv())
            if r.get("id") == expected_id:
                return r
            # Skip events (id=None) and other responses
        except websocket.WebSocketTimeoutException:
            continue
        except Exception as e:
            print(f"    WS error: {e}")
            break
    return None

def navigate(ws, url, wait=6, mid=1):
    """Navigate and wait for page to load."""
    cdp_simple(ws, "Page.navigate", {"url": url}, mid=mid)
    r = read_response(ws, mid, timeout=5)
    frame_id = r.get("result", {}).get("frameId", "?") if r else "TIMEOUT"
    print(f"    → {url[:50]}... (frame={frame_id})")
    time.sleep(wait)

def screenshot(ws, filename, mid=100):
    """Take a screenshot and save it."""
    cdp_simple(ws, "Page.captureScreenshot", {"format": "png", "quality": 90}, mid=mid)
    r = read_response(ws, mid, timeout=15)
    if r and "result" in r and "data" in r.get("result", {}):
        data = base64.b64decode(r["result"]["data"])
        (OUTPUT_DIR / filename).write_bytes(data)
        print(f"    ✓ {filename} ({len(data)//1024}KB)")
        return True
    else:
        print(f"    ✗ {filename} FAILED")
        return False

def eval_js(ws, expr, mid=50):
    """Evaluate JS and return the value."""
    cdp_simple(ws, "Runtime.evaluate", {"expression": expr, "returnByValue": True}, mid=mid)
    r = read_response(ws, mid, timeout=5)
    if r and "result" in r:
        return r["result"].get("result", {}).get("value")
    return None

print("=" * 55)
print("  BOLDR — CDP Browser Walkthrough V3")
print("=" * 55)

ws_url = get_ws()
if not ws_url:
    print("ERROR: No Chromium pages"); exit(1)

print(f"\nConnecting to Chromium...")
ws = websocket.create_connection(ws_url, timeout=10)
print("Connected!")

# Enable Page events
cdp_simple(ws, "Page.enable", mid=0)
time.sleep(0.5)

# 1. n8n Login
print("\n[1/8] n8n Login Page")
navigate(ws, f"{N8N}/signin", wait=6, mid=1)
screenshot(ws, "cdp_01_n8n_login.png", mid=2)

# 2. Login attempt
print("\n[2/8] Logging in...")
eval_js(ws, """
(function() {
    var setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
    var inputs = document.querySelectorAll('input');
    var result = 'Inputs:' + inputs.length;
    for (var i = 0; i < inputs.length; i++) {
        var inp = inputs[i];
        result += ' [' + i + ']type=' + inp.type + ' name=' + inp.name;
        if (inp.type === 'email' || inp.name === 'email') {
            setter.call(inp, 'steve@digitalfutures.sg');
            inp.dispatchEvent(new Event('input', {bubbles: true}));
            inp.dispatchEvent(new Event('change', {bubbles: true}));
        }
        if (inp.type === 'password') {
            setter.call(inp, 'BolDR2026!demo');
            inp.dispatchEvent(new Event('input', {bubbles: true}));
            inp.dispatchEvent(new Event('change', {bubbles: true}));
        }
    }
    var btn = document.querySelector('button[type="submit"]');
    if (btn) { btn.click(); result += ' CLICKED'; }
    return result;
})()
""", mid=3)
time.sleep(8)
screenshot(ws, "cdp_02_after_login.png", mid=4)
current_url = eval_js(ws, "window.location.href", mid=5)
print(f"    Current URL: {current_url}")

# 3. Workflows
print("\n[3/8] n8n Workflows List")
navigate(ws, f"{N8N}/workflows", wait=6, mid=10)
screenshot(ws, "cdp_03_n8n_workflows.png", mid=11)

# 4. Individual workflows
print("\n[4/8] Individual Workflows")
for i, name in enumerate(["Chat_Intake", "WhatsApp_Intake", "Email_Intake", "Instagram_Intake", "KB_Gap_Detection"]):
    print(f"  {i+1}. {name}")
    navigate(ws, f"{N8N}/workflow/{i+1}", wait=5, mid=20+i)
    screenshot(ws, f"cdp_04_workflow_{i+1}_{name}.png", mid=30+i)

# 5. Streamlit
print("\n[5/8] Streamlit Dashboard")
navigate(ws, STREAMLIT, wait=10, mid=40)
screenshot(ws, "cdp_05_streamlit_dashboard.png", mid=41)

# 6. Swagger UI
print("\n[6/8] Swagger UI")
navigate(ws, f"{FASTAPI}/docs", wait=5, mid=50)
screenshot(ws, "cdp_06_swagger_ui.png", mid=51)

# 7. Live ticket
print("\n[7/8] Processing live ticket...")
try:
    data = json.dumps({"message": "Is the BOLDR Venture suitable for diving?", "channel": "chat", "sender_name": "Demo User"}).encode()
    req = urllib.request.Request(f"{FASTAPI}/api/v1/intake", data=data, headers={"Content-Type": "application/json"})
    resp = json.loads(urllib.request.urlopen(req, timeout=30).read())
    print(f"    Ticket: {resp.get('ticket_id')} -> {resp.get('question_type')} ({resp.get('buyer_persona')})")
except Exception as e:
    print(f"    Error: {e}")

# 8. Closing
print("\n[8/8] Closing")
navigate(ws, f"{N8N}/workflows", wait=5, mid=60)
screenshot(ws, "cdp_08_closing.png", mid=61)

ws.close()
print("\n✅ All screenshots captured!")
print("ffmpeg is still recording in background.")
for f in sorted(OUTPUT_DIR.glob("cdp_*.png")):
    print(f"  {f.name} ({f.stat().st_size // 1024}KB)")