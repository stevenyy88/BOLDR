#!/usr/bin/env python3
"""
BOLDR — CDP Walkthrough (Simplified, Robust)
Uses Chrome DevTools Protocol to navigate and capture screenshots.
"""

import json, time, base64, websocket, urllib.request
from pathlib import Path

CDP_PORT = 9222
OUTPUT_DIR = Path(__file__).parent.parent / "docs" / "demo_video"
FASTAPI_URL = "http://localhost:8000"
N8N_URL = "http://localhost:5678"
STREAMLIT_URL = "http://localhost:8501"
SWAGGER_URL = f"{FASTAPI_URL}/docs"
N8N_USER = "steve@digitalfutures.sg"
N8N_PASS = "BolDR2026!demo"

def get_page_ws():
    resp = urllib.request.urlopen(f"http://localhost:{CDP_PORT}/json")
    for p in json.loads(resp.read()):
        if p.get("type") == "page":
            return p["webSocketDebuggerUrl"]
    return None

def cdp(ws, method, params=None, mid=1, timeout=10):
    cmd = {"id": mid, "method": method}
    if params: cmd["params"] = params
    ws.send(json.dumps(cmd))
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            ws.settimeout(2)
            r = json.loads(ws.recv())
            if r.get("id") == mid:
                return r
        except websocket.WebSocketTimeoutException:
            continue
        except: break
    return None

def snap(ws, name, mid=100):
    r = cdp(ws, "Page.captureScreenshot", {"format": "png", "quality": 90}, mid=mid, timeout=15)
    if r and "result" in r and "data" in r["result"]:
        data = base64.b64decode(r["result"]["data"])
        p = OUTPUT_DIR / name
        p.write_bytes(data)
        print(f"  ✓ {name} ({len(data)//1024}KB)")
    else:
        print(f"  ✗ {name} FAILED")

def nav(ws, url, wait=5, mid=1):
    cdp(ws, "Page.navigate", {"url": url}, mid=mid, timeout=10)
    time.sleep(wait)

def js(ws, expr, mid=1):
    r = cdp(ws, "Runtime.evaluate", {"expression": expr, "returnByValue": True}, mid=mid, timeout=10)
    if r and "result" in r:
        return r["result"].get("result", {}).get("value")
    return None

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

print("=" * 55)
print("  BOLDR — CDP Browser Walkthrough")
print("=" * 55)

ws_url = get_page_ws()
if not ws_url:
    print("ERROR: No Chromium pages found"); exit(1)
ws = websocket.create_connection(ws_url, timeout=10)
print(f"Connected to Chromium CDP")

# 1. n8n Login
print("\n[1/8] n8n Login Page")
nav(ws, f"{N8N_URL}/signin", wait=5, mid=1)
snap(ws, "cdp_01_n8n_login.png", mid=2)

# Analyze form
result = js(ws, """
(function() {
    var inputs = document.querySelectorAll('input');
    var info = 'Inputs:' + inputs.length;
    for (var i = 0; i < inputs.length; i++) {
        info += ' [' + i + ']type=' + inputs[i].type + ' name=' + inputs[i].name;
    }
    var btns = document.querySelectorAll('button');
    info += ' Buttons:' + btns.length;
    for (var j = 0; j < Math.min(btns.length, 3); j++) {
        info += ' "' + btns[j].textContent.trim().substring(0,20) + '"';
    }
    return info;
})()
""", mid=3)
print(f"  Form: {result}")

# Fill login form
print("\n[2/8] Logging in...")
js(ws, f"""
(function() {{
    var setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
    var inputs = document.querySelectorAll('input');
    for (var i = 0; i < inputs.length; i++) {{
        if (inputs[i].type === 'email' || inputs[i].name === 'email' || inputs[i].id === 'email') {{
            setter.call(inputs[i], '{N8N_USER}');
            inputs[i].dispatchEvent(new Event('input', {{bubbles: true}}));
            inputs[i].dispatchEvent(new Event('change', {{bubbles: true}}));
        }}
        if (inputs[i].type === 'password') {{
            setter.call(inputs[i], '{N8N_PASS}');
            inputs[i].dispatchEvent(new Event('input', {{bubbles: true}}));
            inputs[i].dispatchEvent(new Event('change', {{bubbles: true}}));
        }}
    }}
    var btn = document.querySelector('button[type="submit"]');
    if (btn) {{ btn.click(); return 'submitted'; }}
    return 'filled, no submit btn';
}})()
""", mid=4)
time.sleep(8)
snap(ws, "cdp_02_after_login.png", mid=5)

url = js(ws, "window.location.href", mid=6)
print(f"  Current URL: {url}")

# 3. Workflows
print("\n[3/8] n8n Workflows List")
nav(ws, f"{N8N_URL}/workflows", wait=6, mid=10)
snap(ws, "cdp_03_n8n_workflows.png", mid=11)

# 4. Individual workflows
print("\n[4/8] Individual Workflows")
for i, name in enumerate(["Chat_Intake", "WhatsApp_Intake", "Email_Intake", "Instagram_Intake", "KB_Gap_Detection"]):
    print(f"  {i+1}. {name}")
    nav(ws, f"{N8N_URL}/workflow/{i+1}", wait=5, mid=20+i)
    snap(ws, f"cdp_04_workflow_{i+1}_{name}.png", mid=30+i)

# 5. Streamlit
print("\n[5/8] Streamlit Dashboard")
nav(ws, STREAMLIT_URL, wait=10, mid=40)
snap(ws, "cdp_05_streamlit_dashboard.png", mid=41)

# 6. Swagger
print("\n[6/8] Swagger UI")
nav(ws, SWAGGER_URL, wait=5, mid=50)
snap(ws, "cdp_06_swagger_ui.png", mid=51)

# 7. Live ticket
print("\n[7/8] Live Ticket Processing")
try:
    data = json.dumps({"message": "Hi, is the BOLDR Venture suitable for diving?", "channel": "chat", "sender_name": "Demo User"}).encode()
    req = urllib.request.Request(f"{FASTAPI_URL}/api/v1/intake", data=data, headers={"Content-Type": "application/json"})
    resp = json.loads(urllib.request.urlopen(req, timeout=30).read())
    print(f"  Ticket: {resp.get('ticket_id')} -> {resp.get('question_type')} ({resp.get('buyer_persona')})")
except Exception as e:
    print(f"  Error: {e}")

# 8. Closing
print("\n[8/8] Closing")
nav(ws, f"{N8N_URL}/workflows", wait=5, mid=60)
snap(ws, "cdp_08_closing.png", mid=61)

ws.close()
print("\nDone! All screenshots captured.")
print("ffmpeg is still recording. To stop: kill $(pgrep -f 'ffmpeg.*x11grab')")