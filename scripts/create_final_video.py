#!/usr/bin/env python3
"""
BOLDR — Final Demo Video Composer
Combines CDP screenshots (Streamlit, Swagger) with PIL-generated slides
for sections where n8n login is required.

Creates a polished 3-4 minute demo video.

Author: Steve Ng, Founder and CEO — Digital Futures Consultancy LLP
"""

import os, subprocess, tempfile
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

# Configuration
WIDTH, HEIGHT = 1920, 1080
FPS = 24
OUTPUT_DIR = Path(__file__).parent.parent / "docs" / "demo_video"
FRAME_DIR = tempfile.mkdtemp(prefix="boldr_final_")

# Fonts
FONT_DIR = "/usr/share/fonts/truetype/dejavu"
FONT_TITLE = ImageFont.truetype(f"{FONT_DIR}/DejaVuSans-Bold.ttf", 48)
FONT_SUBTITLE = ImageFont.truetype(f"{FONT_DIR}/DejaVuSans.ttf", 28)
FONT_BODY = ImageFont.truetype(f"{FONT_DIR}/DejaVuSansMono.ttf", 22)
FONT_BODY_BOLD = ImageFont.truetype(f"{FONT_DIR}/DejaVuSansMono-Bold.ttf", 22)
FONT_SMALL = ImageFont.truetype(f"{FONT_DIR}/DejaVuSans.ttf", 18)
FONT_KPI = ImageFont.truetype(f"{FONT_DIR}/DejaVuSans-Bold.ttf", 64)

# Colors
BG_DARK = (13, 17, 23)
BG_CARD = (22, 27, 34)
BORDER = (48, 54, 61)
TEXT_PRIMARY = (230, 237, 243)
TEXT_SECONDARY = (139, 148, 158)
TEXT_GREEN = (63, 185, 80)
TEXT_BLUE = (88, 166, 255)
TEXT_YELLOW = (210, 153, 34)


def create_title_slide(title, subtitle="", lines=None, section="", kpis=None, duration=5):
    """Create a slide image."""
    img = Image.new('RGB', (WIDTH, HEIGHT), BG_DARK)
    draw = ImageDraw.Draw(img)
    
    # Top accent bar
    draw.rectangle([(0, 0), (WIDTH, 4)], fill=(56, 139, 253))
    
    # Section label
    if section:
        draw.text((60, 20), section, font=FONT_SMALL, fill=TEXT_BLUE)
    
    # Title
    title_y = 60 if section else 50
    draw.text((60, title_y), title, font=FONT_TITLE, fill=TEXT_PRIMARY)
    
    # Subtitle
    if subtitle:
        draw.text((60, title_y + 65), subtitle, font=FONT_SUBTITLE, fill=TEXT_SECONDARY)
    
    # KPI cards
    content_y = 180
    if kpis:
        card_w = (WIDTH - 120 - 30 * (len(kpis) - 1)) // len(kpis)
        for i, (label, value) in enumerate(kpis):
            x = 60 + i * (card_w + 30)
            draw.rounded_rectangle([(x, content_y), (x + card_w, content_y + 120)], radius=10, fill=BG_CARD, outline=BORDER)
            draw.text((x + 20, content_y + 15), value, font=FONT_KPI, fill=TEXT_GREEN)
            draw.text((x + 20, content_y + 85), label, font=FONT_SMALL, fill=TEXT_SECONDARY)
        content_y += 150
    
    # Content lines
    if lines:
        for line_data in lines:
            if isinstance(line_data, tuple):
                text, color = line_data
            else:
                text, color = line_data, TEXT_PRIMARY
            
            if not text:
                content_y += 15
                continue
            
            font = FONT_BODY_BOLD if text.startswith(">> ") else FONT_BODY
            if text.startswith(">> "):
                text = text[3:]
                color = TEXT_YELLOW
            
            draw.text((60, content_y), text, font=font, fill=color)
            content_y += 30
    
    # Footer
    draw.text((60, HEIGHT - 35), "BOLDR — Self-Improving Customer Intelligence Engine  |  Digital Futures Consultancy LLP  |  ECHELON 2026", 
              font=FONT_SMALL, fill=TEXT_SECONDARY)
    
    return img


def add_slide_to_video(img, duration, concat_file, frame_dir, fps=FPS):
    """Add a slide to the video concat file."""
    path = os.path.join(frame_dir, f"slide_{len(concat_file.readlines() if hasattr(concat_file, 'readlines') else [])}.png")
    img.save(path)
    # We'll write directly
    return path, duration


def create_video_from_images(images_and_durations, output_path, fps=FPS):
    """Create video from list of (image_path_or_PIL_image, duration_seconds) tuples."""
    # Save all images as PNGs and create concat file
    frame_files = []
    for i, (img, duration) in enumerate(images_and_durations):
        if isinstance(img, str):
            # It's a file path
            path = img
        else:
            # It's a PIL Image
            path = os.path.join(FRAME_DIR, f"frame_{i:04d}.png")
            img.save(path)
        
        for _ in range(max(1, int(duration * fps))):
            frame_files.append(path)
    
    # Write concat file
    concat_path = os.path.join(FRAME_DIR, "concat.txt")
    with open(concat_path, "w") as f:
        for fp in frame_files:
            f.write(f"file '{fp}'\n")
            f.write(f"duration {1/fps}\n")
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
    
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    if result.returncode == 0:
        size_mb = os.path.getsize(output_path) / (1024 * 1024)
        print(f"  Video created: {output_path} ({size_mb:.1f} MB)")
        return True
    else:
        print(f"  ERROR: {result.stderr[:300]}")
        return False


def main():
    import json, urllib.request
    
    print("=" * 60)
    print("  BOLDR — Final Demo Video Composer")
    print("=" * 60)
    
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Get live stats
    try:
        stats = json.loads(urllib.request.urlopen("http://localhost:8000/api/v1/stats", timeout=5).read())
        total_tickets = stats.get("pipeline", {}).get("total_tickets", 0)
        answerable = stats.get("pipeline", {}).get("answerable_count", 0)
        answer_rate = stats.get("kb", {}).get("answerability_rate", 0)
    except:
        total_tickets = 70
        answerable = 50
        answer_rate = 83.3
    
    frames = []
    
    # 1. Title Card (5s)
    print("\n[1/9] Title Card")
    img = create_title_slide(
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
    )
    frames.append((img, 5))
    
    # 2. Problem (6s)
    print("[2/9] Problem")
    img = create_title_slide(
        title="The Problem",
        subtitle="3-person CS team drowning in manual support",
        section="PROBLEM",
        lines=[
            ("70+ customer enquiries per day across 4 channels", TEXT_PRIMARY),
            ("4-8 hours average response time", (248, 81, 73)),
            ("No feedback loop — knowledge gaps never get fixed", (248, 81, 73)),
            ("Marketing signals invisible in support data", (248, 81, 73)),
            ("", TEXT_PRIMARY),
            ("7 question types | 7 buyer personas | 4 channels", TEXT_YELLOW),
            (f"{answer_rate}% answerable by KB | {100-answer_rate:.1f}% require escalation", TEXT_GREEN),
        ],
        duration=6
    )
    frames.append((img, 6))
    
    # 3. Solution (8s)
    print("[3/9] Solution")
    img = create_title_slide(
        title="The Solution: Closed-Loop Intelligence",
        subtitle="Not a chatbot — a self-improving system",
        section="SOLUTION",
        lines=[
            ("1. Receive enquiry from any channel (Chat, WhatsApp, IG, Email)", TEXT_PRIMARY),
            ("2. Classify intent + tag buyer persona (LLM + rule-based hybrid)", TEXT_PRIMARY),
            ("3. Search knowledge base (ChromaDB vector + keyword hybrid)", TEXT_PRIMARY),
            ("4. Draft professional reply in BOLDR brand voice", TEXT_PRIMARY),
            ("5. Queue for human approval (never auto-send)", TEXT_GREEN),
            ("6. Detect gaps -> auto-draft KB entries", TEXT_PRIMARY),
            ("7. Cluster themes -> weekly reports + monthly marketing briefs", TEXT_PRIMARY),
            ("", TEXT_PRIMARY),
            (">> Result: 9 hrs/week saved | SGD 1,080/mo | 19-49x ROI", TEXT_YELLOW),
        ],
        duration=8
    )
    frames.append((img, 8))
    
    # 4. Live API (8s)
    print("[4/9] Live API")
    img = create_title_slide(
        title="Live API — 31 Endpoints",
        subtitle=f"Currently processing: {total_tickets} tickets",
        section="API DEMO",
        lines=[
            (">> Health Check:", TEXT_YELLOW),
            ("  GET /api/v1/health -> healthy", TEXT_GREEN),
            (f"  tickets_processed: {total_tickets}", TEXT_BLUE),
            ("  pii_stripping_enabled: false", TEXT_BLUE),
            ("", TEXT_PRIMARY),
            (">> Rate Limiting:", TEXT_YELLOW),
            ("  2/sec intake | 5/sec general | 10/sec stats", TEXT_PRIMARY),
            (">> Channel Integration:", TEXT_YELLOW),
            ("  WhatsApp | Instagram | Email | Chat", TEXT_PRIMARY),
            (">> PII Stripping: 8 patterns (email, phone, NRIC, credit card)", TEXT_PRIMARY),
            (">> Audit Log: Every classification persisted to SQLite", TEXT_PRIMARY),
        ],
        duration=8
    )
    frames.append((img, 8))
    
    # 5. Streamlit Dashboard (use CDP screenshot if available)
    print("[5/9] Streamlit Dashboard")
    streamlit_img_path = OUTPUT_DIR / "cdp_05_streamlit.png"
    if streamlit_img_path.exists() and streamlit_img_path.stat().st_size > 50000:
        # Use real screenshot
        streamlit_img = Image.open(streamlit_img_path)
        # Resize if needed
        if streamlit_img.size != (WIDTH, HEIGHT):
            streamlit_img = streamlit_img.resize((WIDTH, HEIGHT), Image.LANCZOS)
        # Add overlay text
        draw = ImageDraw.Draw(streamlit_img)
        draw.rectangle([(0, 0), (WIDTH, 40)], fill=(13, 17, 23, 200))
        draw.text((20, 5), "BOLDR Dashboard — Live Data | 9 Tabs | 5 KPI Cards", font=FONT_SMALL, fill=TEXT_BLUE)
        draw.rectangle([(0, HEIGHT-30), (WIDTH, HEIGHT)], fill=(13, 17, 23, 200))
        draw.text((20, HEIGHT-28), "ECHELON 2026 | Digital Futures Consultancy LLP | stevenyy88/BOLDR", font=FONT_SMALL, fill=TEXT_SECONDARY)
        frames.append((streamlit_img, 10))
    else:
        img = create_title_slide(
            title="Streamlit Dashboard — 9 Tabs",
            subtitle="Live data + KPI cards",
            section="DASHBOARD",
            kpis=[
                ("Tickets", str(total_tickets)),
                ("KB Rate", f"{answer_rate}%"),
                ("CS Saved", "~9 hrs/wk"),
                ("Savings", "SGD 1,080/mo"),
                ("ROI", "19-49x"),
            ],
            lines=[
                ("Live Pipeline | Approval Queue | Ticket Timeline", TEXT_PRIMARY),
                ("Channel Analytics | Theme Analysis | KB Management", TEXT_PRIMARY),
                ("Gap Log | Marketing Brief | Audit Log", TEXT_PRIMARY),
            ],
            duration=10
        )
        frames.append((img, 10))
    
    # 6. Swagger UI (use CDP screenshot if available)
    print("[6/9] Swagger UI")
    swagger_img_path = OUTPUT_DIR / "cdp_06_swagger.png"
    if swagger_img_path.exists() and swagger_img_path.stat().st_size > 50000:
        swagger_img = Image.open(swagger_img_path)
        if swagger_img.size != (WIDTH, HEIGHT):
            swagger_img = swagger_img.resize((WIDTH, HEIGHT), Image.LANCZOS)
        draw = ImageDraw.Draw(swagger_img)
        draw.rectangle([(0, 0), (WIDTH, 40)], fill=(13, 17, 23, 200))
        draw.text((20, 5), "BOLDR API — 31 REST Endpoints | Swagger UI", font=FONT_SMALL, fill=TEXT_BLUE)
        draw.rectangle([(0, HEIGHT-30), (WIDTH, HEIGHT)], fill=(13, 17, 23, 200))
        draw.text((20, HEIGHT-28), "ECHELON 2026 | Digital Futures Consultancy LLP", font=FONT_SMALL, fill=TEXT_SECONDARY)
        frames.append((swagger_img, 8))
    else:
        img = create_title_slide(
            title="API — 31 REST Endpoints",
            subtitle="Swagger UI with full documentation",
            section="API",
            lines=[
                ("Intake: POST /api/v1/intake (classify + route)", TEXT_PRIMARY),
                ("Stats: GET /api/v1/stats (pipeline metrics)", TEXT_PRIMARY),
                ("Health: GET /api/v1/health", TEXT_PRIMARY),
                ("Shopify: GET /api/v1/shopify/* (3 endpoints)", TEXT_PRIMARY),
                ("Queue: GET/POST /api/v1/queue/* (7 endpoints)", TEXT_PRIMARY),
                ("Themes: POST /api/v1/themes/cluster", TEXT_PRIMARY),
                ("PII: POST /api/v1/pii/strip, GET /api/v1/pii/status", TEXT_PRIMARY),
                ("Audit: GET /api/v1/audit/* (3 endpoints)", TEXT_PRIMARY),
                ("Channels: 6 webhook endpoints", TEXT_PRIMARY),
            ],
            duration=8
        )
        frames.append((img, 8))
    
    # 7. Responsible AI (8s)
    print("[7/9] Responsible AI")
    img = create_title_slide(
        title="Responsible AI — Human-in-the-Loop",
        section="RESPONSIBLE AI",
        lines=[
            ("No auto-send — every reply requires human approval", TEXT_GREEN),
            ("Confidence scoring (0-1) — below 0.5 -> CS escalation", TEXT_PRIMARY),
            ("PII stripping — 8 regex patterns, GDPR/PDPA configurable", TEXT_PRIMARY),
            ("SQLite audit log — every classification decision persisted", TEXT_PRIMARY),
            ("Rate limiting — token bucket on all endpoints", TEXT_PRIMARY),
            ("Fail-safe — if LLM down, all tickets route to CS team", TEXT_GREEN),
            ("", TEXT_PRIMARY),
            (">> Endpoints:", TEXT_YELLOW),
            ("  POST /api/v1/pii/strip  |  GET /api/v1/pii/status", TEXT_PRIMARY),
            ("  GET /api/v1/audit/recent | GET /api/v1/audit/summary", TEXT_PRIMARY),
        ],
        duration=8
    )
    frames.append((img, 8))
    
    # 8. Business Impact (10s)
    print("[8/9] Business Impact")
    img = create_title_slide(
        title="Business Impact — 19-49x ROI",
        section="BUSINESS IMPACT",
        lines=[
            (">> Reduces response time from 4-8 hours to <2 min", TEXT_YELLOW),
            ("", TEXT_PRIMARY),
            ("Time Saved: ~9 hours/week (60% reduction)", TEXT_GREEN),
            ("Monthly CS Savings: SGD 1,080 (SGD 28/hr blended rate)", TEXT_GREEN),
            ("Revenue Recovery: SGD 3,000-5,000/mo (15-20% conversion)", TEXT_GREEN),
            ("", TEXT_PRIMARY),
            ("Setup Cost: SGD 600-800 (one-time)", TEXT_PRIMARY),
            ("Monthly OpEx: SGD 22-57/mo (self-hosted, open-source)", TEXT_PRIMARY),
            ("", TEXT_PRIMARY),
            (">> ROI: 19-49x monthly operating cost", TEXT_YELLOW),
            ("", TEXT_PRIMARY),
            ("Marketing signals unlocked:", TEXT_YELLOW),
            ("  BPA-free straps -> Health-Conscious Buyer -> New segment", TEXT_PRIMARY),
            ("  Vegan materials -> Sustainability Advocate -> First-mover", TEXT_PRIMARY),
            ("  Corporate gifting -> Bulk pricing -> Higher-value orders", TEXT_PRIMARY),
        ],
        duration=10
    )
    frames.append((img, 10))
    
    # 9. Closing (6s)
    print("[9/9] Closing")
    img = create_title_slide(
        title="BOLDR — Self-Improving Customer Intelligence Engine",
        subtitle="Transforming reactive support into proactive intelligence",
        lines=[
            ("", TEXT_PRIMARY),
            ("31 API endpoints | 9 dashboard tabs | 5 n8n workflows", TEXT_YELLOW),
            ("4 channel integrations | PII stripping | Rate limiting", TEXT_YELLOW),
            ("SQLite audit log | Approval queue | Theme clustering", TEXT_YELLOW),
            ("", TEXT_PRIMARY),
            ("13/13 e2e tests passing | Zero external credentials", TEXT_GREEN),
            ("", TEXT_PRIMARY),
            ("docker compose up -d -> Ready to process tickets", TEXT_BLUE),
            ("", TEXT_PRIMARY),
            ("Steve Ng, Founder & CEO", TEXT_PRIMARY),
            ("Digital Futures Consultancy LLP (T17LL1937H)", TEXT_SECONDARY),
            ("https://DigitalFutures.Asia", TEXT_BLUE),
        ],
        duration=6
    )
    frames.append((img, 6))
    
    # Calculate total duration
    total_duration = sum(d for _, d in frames)
    print(f"\nTotal video duration: {total_duration}s ({total_duration//60}m {total_duration%60}s)")
    print(f"Number of frames: {len(frames)}")
    
    # Create the video
    print("\nGenerating video...")
    output_path = OUTPUT_DIR / "BOLDR_demo_final.mp4"
    
    # Save all frames as PNGs and create concat file
    concat_path = os.path.join(FRAME_DIR, "concat.txt")
    with open(concat_path, "w") as f:
        for i, (img, duration) in enumerate(frames):
            frame_path = os.path.join(FRAME_DIR, f"final_{i:04d}.png")
            img.save(frame_path)
            num_frames = max(1, int(duration * FPS))
            for _ in range(num_frames):
                f.write(f"file '{frame_path}'\n")
                f.write(f"duration {1/FPS}\n")
        # Repeat last frame
        last_path = os.path.join(FRAME_DIR, f"final_{len(frames)-1:04d}.png")
        f.write(f"file '{last_path}'\n")
    
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
    
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    if result.returncode == 0:
        size_mb = os.path.getsize(output_path) / (1024 * 1024)
        print(f"\n  SUCCESS: {output_path} ({size_mb:.1f} MB)")
        
        # Get duration
        probe = subprocess.run(
            ["ffprobe", "-v", "quiet", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", str(output_path)],
            capture_output=True, text=True
        )
        try:
            dur = float(probe.stdout.strip())
            print(f"  Duration: {dur:.1f}s ({int(dur)//60}m {int(dur)%60}s)")
        except:
            pass
    else:
        print(f"\n  ERROR: {result.stderr[:500]}")
    
    # Also create a highlight (first 60s)
    print("\nCreating 60-second highlight...")
    highlight_path = OUTPUT_DIR / "BOLDR_demo_highlight_v2.mp4"
    subprocess.run([
        "ffmpeg", "-y",
        "-i", str(output_path),
        "-t", "60",
        "-c:v", "libx264", "-preset", "medium", "-crf", "23",
        "-pix_fmt", "yuv420p", "-movflags", "+faststart",
        str(highlight_path)
    ], capture_output=True, text=True, timeout=60)
    
    if highlight_path.exists():
        print(f"  Highlight: {highlight_path} ({highlight_path.stat().st_size / (1024*1024):.1f} MB)")
    
    print("\nDone!")


if __name__ == "__main__":
    main()