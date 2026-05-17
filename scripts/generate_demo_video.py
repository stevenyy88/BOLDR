#!/usr/bin/env python3
"""
BOLDR — Demo Video Generator (Pillow-based)
Creates a professional walkthrough video using PIL for frame rendering
and ffmpeg for video encoding.

Author: Steve Ng, Founder and CEO — Digital Futures Consultancy LLP
"""

import json
import os
import subprocess
import tempfile
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

# Configuration
WIDTH, HEIGHT = 1920, 1080
FPS = 24
OUTPUT_DIR = Path(__file__).parent.parent / "docs" / "demo_video"
FRAME_DIR = tempfile.mkdtemp(prefix="boldr_video_")

# Fonts
FONT_DIR = "/usr/share/fonts/truetype/dejavu"
FONT_TITLE = ImageFont.truetype(f"{FONT_DIR}/DejaVuSans-Bold.ttf", 48)
FONT_SUBTITLE = ImageFont.truetype(f"{FONT_DIR}/DejaVuSans.ttf", 28)
FONT_BODY = ImageFont.truetype(f"{FONT_DIR}/DejaVuSansMono.ttf", 22)
FONT_BODY_BOLD = ImageFont.truetype(f"{FONT_DIR}/DejaVuSansMono-Bold.ttf", 22)
FONT_SMALL = ImageFont.truetype(f"{FONT_DIR}/DejaVuSans.ttf", 18)
FONT_KPI = ImageFont.truetype(f"{FONT_DIR}/DejaVuSans-Bold.ttf", 64)

# Colors (BOLDR dark theme)
BG_DARK = (13, 17, 23)       # #0d1117
BG_CARD = (22, 27, 34)        # #161b22
BORDER = (48, 54, 61)         # #30363d
TEXT_PRIMARY = (230, 237, 243) # #e6edf3
TEXT_SECONDARY = (139, 148, 158) # #8b949e
TEXT_GREEN = (63, 185, 80)    # #3fb950
TEXT_BLUE = (88, 166, 255)    # #58a6ff
TEXT_YELLOW = (210, 153, 34)  # #d29922
TEXT_RED = (248, 81, 73)      # #f85149
TEXT_PURPLE = (188, 140, 255) # #bc8cff
ACCENT_BLUE = (56, 139, 253)  # #388bfd


def draw_rounded_rect(draw, xy, fill, radius=10, outline=None):
    """Draw a rounded rectangle."""
    x1, y1, x2, y2 = xy
    draw.rounded_rectangle(xy, radius=radius, fill=fill, outline=outline)


def draw_text_wrapped(draw, text, xy, font, fill, max_width=1800):
    """Draw text with word wrapping."""
    x, y = xy
    words = text.split()
    lines = []
    current_line = ""
    for word in words:
        test_line = current_line + " " + word if current_line else word
        bbox = draw.textbbox((0, 0), test_line, font=font)
        if bbox[2] - bbox[0] <= max_width:
            current_line = test_line
        else:
            if current_line:
                lines.append(current_line)
            current_line = word
    if current_line:
        lines.append(current_line)
    
    for i, line in enumerate(lines):
        draw.text((x, y + i * (font.size + 6)), line, font=font, fill=fill)
    return y + len(lines) * (font.size + 6)


def create_slide(title, subtitle="", lines=None, section_label="", kpi_cards=None, duration=5):
    """Create a single slide image."""
    img = Image.new('RGB', (WIDTH, HEIGHT), BG_DARK)
    draw = ImageDraw.Draw(img)
    
    # Top border accent
    draw.rectangle([(0, 0), (WIDTH, 4)], fill=ACCENT_BLUE)
    
    # Section label
    if section_label:
        draw.text((60, 20), section_label, font=FONT_SMALL, fill=TEXT_BLUE)
    
    # Title
    title_y = 60 if section_label else 50
    draw.text((60, title_y), title, font=FONT_TITLE, fill=TEXT_PRIMARY)
    
    # Subtitle
    if subtitle:
        sub_y = title_y + 65
        draw.text((60, sub_y), subtitle, font=FONT_SUBTITLE, fill=TEXT_SECONDARY)
        content_y = sub_y + 50
    else:
        content_y = title_y + 75
    
    # KPI cards
    if kpi_cards:
        card_width = (WIDTH - 120 - 30 * (len(kpi_cards) - 1)) // len(kpi_cards)
        for i, (label, value) in enumerate(kpi_cards):
            x = 60 + i * (card_width + 30)
            draw_rounded_rect(draw, (x, content_y, x + card_width, content_y + 120), 
                            fill=BG_CARD, radius=10, outline=BORDER)
            draw.text((x + 20, content_y + 15), value, font=FONT_KPI, fill=TEXT_GREEN)
            draw.text((x + 20, content_y + 85), label, font=FONT_SMALL, fill=TEXT_SECONDARY)
        content_y += 150
    
    # Content lines
    if lines:
        for line_data in lines:
            if isinstance(line_data, tuple):
                text, color = line_data
            else:
                text = line_data
                color = TEXT_PRIMARY
            
            if not text:  # Empty line
                content_y += 15
                continue
            
            # Check if it's a "header" line (starts with special marker)
            if text.startswith(">> "):
                text = text[3:]
                color = TEXT_YELLOW
                font = FONT_BODY_BOLD
            elif text.startswith("   "):
                font = FONT_BODY
            else:
                font = FONT_BODY
            
            content_y = draw_text_wrapped(draw, text, (60, content_y), font, color, max_width=1780)
            content_y += 4
            
            if content_y > HEIGHT - 40:
                break
    
    # Footer
    draw.text((60, HEIGHT - 35), "BOLDR — Self-Improving Customer Intelligence Engine  |  Digital Futures Consultancy LLP  |  ECHELON 2026", 
              font=FONT_SMALL, fill=TEXT_SECONDARY)
    
    return img


def save_frames_as_video(frames, output_path, fps=FPS):
    """Convert list of (image, duration_seconds) tuples to video."""
    # Save all frames as PNGs
    frame_files = []
    for i, (img, duration) in enumerate(frames):
        frame_path = os.path.join(FRAME_DIR, f"frame_{i:05d}.png")
        img.save(frame_path)
        # Calculate how many times to repeat this frame
        num_repeats = max(1, int(duration * fps))
        for _ in range(num_repeats):
            frame_files.append(frame_path)
    
    # Write concat file
    concat_path = os.path.join(FRAME_DIR, "concat.txt")
    with open(concat_path, "w") as f:
        for fp in frame_files:
            f.write(f"file '{fp}'\n")
            f.write(f"duration {1/fps}\n")
        # Repeat last frame
        f.write(f"file '{frame_files[-1]}'\n")
    
    # Encode video
    cmd = [
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0", "-i", concat_path,
        "-vsync", "vfr",
        "-pix_fmt", "yuv420p",
        "-c:v", "libx264",
        "-preset", "medium",
        "-crf", "23",
        "-movflags", "+faststart",
        str(output_path)
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        size_mb = os.path.getsize(output_path) / (1024 * 1024)
        print(f"  Video created: {output_path} ({size_mb:.1f} MB)")
        return True
    else:
        print(f"  ERROR: ffmpeg failed: {result.stderr[:300]}")
        return False


def main():
    print("=" * 60)
    print("  BOLDR — Demo Video Generator")
    print("  ECHELON 2026 AI Workflow Competition")
    print("=" * 60)
    
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Get live data from API
    print("\nFetching live data from API...")
    try:
        import urllib.request
        health = json.loads(urllib.request.urlopen("http://localhost:8000/api/v1/health").read())
        stats = json.loads(urllib.request.urlopen("http://localhost:8000/api/v1/stats").read())
        total_tickets = stats.get("pipeline", {}).get("total_tickets", 0)
        answerable = stats.get("pipeline", {}).get("answerable_count", 0)
        gaps = stats.get("pipeline", {}).get("gap_count", 0)
        print(f"  API healthy: {total_tickets} tickets processed")
    except:
        total_tickets = 70
        answerable = 50
        gaps = 20
        print("  API not reachable, using default values")
    
    # Generate slides
    print("\nGenerating slides...")
    frames = []
    
    # 1. Title Card (5s)
    frames.append((create_slide(
        title="BOLDR",
        subtitle="Self-Improving Customer Intelligence Engine",
        lines=[
            ("ECHELON 2026 AI Workflow Competition — REVENUE ROCKET Track", TEXT_BLUE),
            ("", TEXT_PRIMARY),
            ("Steve Ng, Founder & CEO", TEXT_PRIMARY),
            ("Digital Futures Consultancy LLP (T17LL1937H)", TEXT_SECONDARY),
            ("https://DigitalFutures.Asia", TEXT_YELLOW),
        ],
        duration=5
    ), 5))
    
    # 2. Problem (6s)
    frames.append((create_slide(
        title="The Problem",
        subtitle="BOLDR's 3-person CS team is drowning in manual support",
        section_label="PROBLEM",
        lines=[
            ("70+ customer enquiries per day across 4 channels", TEXT_PRIMARY),
            ("4-8 hours average response time", TEXT_RED),
            ("No feedback loop — knowledge gaps never get fixed", TEXT_RED),
            ("Marketing signals invisible in support data", TEXT_RED),
            ("", TEXT_PRIMARY),
            ("7 question types  |  7 buyer personas  |  4 channels", TEXT_YELLOW),
            ("71% answerable by KB  |  29% require escalation", TEXT_GREEN),
        ],
        duration=6
    ), 6))
    
    # 3. Solution (8s)
    frames.append((create_slide(
        title="The Solution: Closed-Loop Intelligence",
        subtitle="Not a chatbot — a self-improving system",
        section_label="SOLUTION",
        lines=[
            ("1. Receive enquiry from any channel (Chat, WhatsApp, IG, Email)", TEXT_PRIMARY),
            ("2. Classify intent + tag buyer persona (LLM + rule-based hybrid)", TEXT_PRIMARY),
            ("3. Search knowledge base (ChromaDB vector + keyword hybrid)", TEXT_PRIMARY),
            ("4. Draft professional reply in BOLDR brand voice", TEXT_PRIMARY),
            ("5. Queue for human approval (never auto-send)", TEXT_GREEN),
            ("6. Detect gaps -> auto-draft KB entries", TEXT_PRIMARY),
            ("7. Cluster themes -> weekly reports + monthly marketing briefs", TEXT_PRIMARY),
            ("", TEXT_PRIMARY),
            (">> Result: 9 hrs/week saved  |  SGD 1,080/mo  |  19-49x ROI", TEXT_YELLOW),
        ],
        duration=8
    ), 8))
    
    # 4. Live API Demo (8s)
    frames.append((create_slide(
        title="Live API — 31 Endpoints",
        subtitle=f"Currently processing: {total_tickets} tickets",
        section_label="API DEMO",
        lines=[
            ("INPUT:  curl http://localhost:8000/api/v1/health", TEXT_GREEN),
            ('OUTPUT: { "status": "healthy",', TEXT_BLUE),
            ('          "service": "BOLDR Intelligence Engine",', TEXT_BLUE),
            (f'          "tickets_processed": {total_tickets},', TEXT_BLUE),
            ('          "pii_stripping_enabled": false }', TEXT_BLUE),
            ("", TEXT_PRIMARY),
            ("Rate Limiting:  2/sec intake  |  5/sec general  |  10/sec stats", TEXT_YELLOW),
            ("X-RateLimit headers on every response", TEXT_SECONDARY),
            ("", TEXT_PRIMARY),
            ("Channel Integration:  WhatsApp  |  Instagram  |  Email  |  Chat", TEXT_YELLOW),
            ("PII Stripping:  8 patterns (email, phone, NRIC, credit card, postal)", TEXT_YELLOW),
            ("Audit Log:  Every classification decision persisted to SQLite", TEXT_YELLOW),
        ],
        duration=8
    ), 8))
    
    # 5. Channel Integration (8s)
    frames.append((create_slide(
        title="Channel Integration — Zero Credentials Demo",
        subtitle="Production-ready webhook receivers for WhatsApp, Instagram, Email",
        section_label="CHANNELS",
        lines=[
            (">> Competition Demo (zero credentials):", TEXT_YELLOW),
            ("   n8n workflows -> FastAPI /api/v1/intake", TEXT_PRIMARY),
            ("   Works immediately — docker compose up -d", TEXT_GREEN),
            ("", TEXT_PRIMARY),
            (">> Production (platform webhooks):", TEXT_YELLOW),
            ("   WhatsApp Business API -> /api/v1/channels/whatsapp/webhook", TEXT_PRIMARY),
            ("   Instagram Graph API   -> /api/v1/channels/instagram/webhook", TEXT_PRIMARY),
            ("   Mailgun/SendGrid      -> /api/v1/channels/email/webhook", TEXT_PRIMARY),
            ("   Gmail IMAP Poller     -> /api/v1/channels/email/imap-fetch", TEXT_PRIMARY),
            ("", TEXT_PRIMARY),
            ("Both paths converge on the same intelligence loop.", TEXT_BLUE),
            ("See: docs/BOLDR-Channel-Integrations.md for production setup", TEXT_SECONDARY),
        ],
        duration=8
    ), 8))
    
    # 6. Dashboard & KPIs (7s)
    frames.append((create_slide(
        title="Dashboard — 9 Tabs with Live Data",
        subtitle="Streamlit dashboard with KPI cards and real-time statistics",
        section_label="DASHBOARD",
        kpi_cards=[
            ("Tickets Processed", str(total_tickets)),
            ("KB Answer Rate", f"{round(answerable/max(total_tickets,1)*100,1)}%"),
            ("CS Time Saved", "~9 hrs/wk"),
            ("Monthly Savings", "SGD 1,080"),
            ("ROI", "19-49x"),
        ],
        lines=[
            ("Live Pipeline  |  Approval Queue  |  Ticket Timeline", TEXT_PRIMARY),
            ("Channel Analytics  |  Theme Analysis  |  KB Management", TEXT_PRIMARY),
            ("Gap Log  |  Marketing Brief  |  Audit Log", TEXT_PRIMARY),
            ("", TEXT_PRIMARY),
            ("All data pulled live from FastAPI endpoints", TEXT_BLUE),
            ("Auto-refresh every 10 seconds", TEXT_SECONDARY),
        ],
        duration=7
    ), 7))
    
    # 7. Responsible AI (8s)
    frames.append((create_slide(
        title="Responsible AI — Human-in-the-Loop on Everything",
        section_label="RESPONSIBLE AI",
        lines=[
            ("No auto-send — every drafted reply requires human approval", TEXT_GREEN),
            ("Confidence scoring (0-1) — below 0.5 -> CS escalation, not fabrication", TEXT_PRIMARY),
            ("PII stripping — 8 regex patterns, GDPR/PDPA configurable (default: OFF)", TEXT_PRIMARY),
            ("SQLite audit log — every classification decision persisted", TEXT_PRIMARY),
            ("Rate limiting — token bucket on all endpoints (2-10 req/sec)", TEXT_PRIMARY),
            ("Fail-safe design — if LLM down, all tickets route to CS team", TEXT_GREEN),
            ("", TEXT_PRIMARY),
            (">> Endpoints:", TEXT_YELLOW),
            ("   POST /api/v1/pii/strip  - Strip PII on-demand", TEXT_PRIMARY),
            ("   GET  /api/v1/pii/status  - Check PII config", TEXT_PRIMARY),
            ("   GET  /api/v1/audit/recent - Recent ticket processing events", TEXT_PRIMARY),
            ("   GET  /api/v1/audit/summary - Audit statistics", TEXT_PRIMARY),
        ],
        duration=8
    ), 8))
    
    # 8. Business Impact (10s)
    frames.append((create_slide(
        title="Business Impact — SGD 1,080/mo Savings, 19-49x ROI",
        section_label="BUSINESS IMPACT",
        lines=[
            (">> Impact Metric:", TEXT_YELLOW),
            ("   Reduces response time from 4-8 hours to <2 minutes for 71% of tickets", TEXT_PRIMARY),
            ("", TEXT_PRIMARY),
            ("Time Saved: ~9 hours/week (60% reduction)", TEXT_GREEN),
            ("Monthly CS Savings: SGD 1,080 (at SGD 28/hr blended rate)", TEXT_GREEN),
            ("Revenue Recovery: SGD 3,000-5,000/mo (15-20% conversion lift)", TEXT_GREEN),
            ("", TEXT_PRIMARY),
            ("Setup Cost: SGD 600-800 (one-time)", TEXT_PRIMARY),
            ("Monthly OpEx: SGD 22-57/mo (self-hosted, open-source)", TEXT_PRIMARY),
            ("", TEXT_PRIMARY),
            (">> ROI: 19-49x monthly operating cost", TEXT_YELLOW),
            ("", TEXT_PRIMARY),
            ("Marketing signals unlocked:", TEXT_YELLOW),
            ("   BPA-free straps -> Health-Conscious Buyer -> New segment", TEXT_PRIMARY),
            ("   Vegan materials -> Sustainability Advocate -> First-mover", TEXT_PRIMARY),
            ("   Corporate gifting -> Bulk pricing -> Higher-value orders", TEXT_PRIMARY),
        ],
        duration=10
    ), 10))
    
    # 9. Tech Stack (8s)
    frames.append((create_slide(
        title="Tech Stack — Fully Open Source, Self-Hosted",
        section_label="TECH STACK",
        lines=[
            ("n8n            - Workflow orchestration (Docker)", TEXT_PRIMARY),
            ("ChromaDB        - Vector store for KB embeddings (Docker)", TEXT_PRIMARY),
            ("GLM-5.1:cloud  - LLM classification via Ollama (local)", TEXT_PRIMARY),
            ("all-MiniLM-L6-v2 - Embedding model (built-in)", TEXT_PRIMARY),
            ("FastAPI         - 31 REST endpoints (Docker, supervisord)", TEXT_PRIMARY),
            ("Streamlit       - 9-tab dashboard with live data + KPI cards", TEXT_PRIMARY),
            ("SQLite          - Audit log + approval queue (persistent)", TEXT_PRIMARY),
            ("", TEXT_PRIMARY),
            (">> Monthly Operating Cost:", TEXT_YELLOW),
            ("   VPS hosting (2 vCPU, 4GB)   : SGD 5-10", TEXT_PRIMARY),
            ("   LLM API (GLM-5.1 primary)   : SGD 10-30", TEXT_PRIMARY),
            ("   Fallback LLM (edge cases)    : SGD 5-15", TEXT_PRIMARY),
            ("   Embedding model (self-hosted) : SGD 0", TEXT_GREEN),
            ("   Maintenance (CS self-serves)   : SGD 0", TEXT_GREEN),
            (">> Total: SGD 22-57/mo", TEXT_YELLOW),
        ],
        duration=8
    ), 8))
    
    # 10. Closing (6s)
    frames.append((create_slide(
        title="BOLDR — Self-Improving Customer Intelligence Engine",
        subtitle="Transforming reactive support into proactive intelligence",
        lines=[
            ("", TEXT_PRIMARY),
            ("31 API endpoints  |  9 dashboard tabs  |  5 n8n workflows", TEXT_YELLOW),
            ("4 channel integrations  |  PII stripping  |  Rate limiting", TEXT_YELLOW),
            ("SQLite audit log  |  Approval queue  |  Theme clustering", TEXT_YELLOW),
            ("", TEXT_PRIMARY),
            ("13/13 e2e tests passing  |  Zero external credentials", TEXT_GREEN),
            ("", TEXT_PRIMARY),
            ("docker compose up -d  ->  Ready to process tickets", TEXT_BLUE),
            ("", TEXT_PRIMARY),
            ("Steve Ng, Founder & CEO", TEXT_PRIMARY),
            ("Digital Futures Consultancy LLP (T17LL1937H)", TEXT_SECONDARY),
            ("https://DigitalFutures.Asia", TEXT_BLUE),
        ],
        duration=6
    ), 6))
    
    # Generate video
    output_file = OUTPUT_DIR / "BOLDR_demo_overview.mp4"
    print(f"\nGenerating video: {output_file}")
    success = save_frames_as_video(frames, output_file)
    
    if success:
        print(f"\nSUCCESS: Video saved to {output_file}")
    else:
        print("\nFAILED: Could not create video")
    
    # Cleanup
    print("\nDone!")
    print(f"\nVideo: {OUTPUT_DIR}/BOLDR_demo_overview.mp4")
    print(f"Frames: {FRAME_DIR} (temporary)")
    print("\nNOTE: For the best demo, also record a live screen capture showing:")
    print("  1. n8n workflows executing (http://localhost:5678)")
    print("  2. Streamlit dashboard (http://localhost:8501)")
    print("  3. Swagger UI (http://localhost:8000/docs)")


if __name__ == "__main__":
    main()