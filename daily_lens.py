import os
import requests
import urllib.parse

# 1. Fetch Telegram credentials
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

print(f"Checking credentials -> Token present: {bool(TELEGRAM_BOT_TOKEN)}, Chat ID present: {bool(TELEGRAM_CHAT_ID)}")

if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
    raise ValueError(
        "CRITICAL: Secrets were not passed to Python! "
        "Verify that .github/workflows/daily_run.yml has the 'env:' block mapped to secrets.TELEGRAMBOTTOKEN."
    )

ai_prompt = """
You are an expert Snapchat Lens Studio GenAI prompt engineer.
Your task:
1. Pick a trending AR lens aesthetic (e.g., Y2K chrome, cute anime accessories, surreal face distortion).
2. Write a precise prompt compatible with Snapchat Lens Studio AI.
3. Provide a descriptive image prompt for an AI image generator to predict what the user's face will look like with this lens.

Output format strictly like this:
[CONCEPT]: <1 line description>
[SNAP PROMPT]: <The exact text to paste into Snap Lens AI>
[IMAGE PROMPT]: <A portrait photo description showing a person wearing this AR filter>
"""

print("Requesting AI concept from free text API (No Key Required)...")
encoded_req = urllib.parse.quote(ai_prompt)

# Pollinations Free Text API
text_response = requests.get(f"https://text.pollinations.ai/{encoded_req}")
if text_response.status_code != 200:
    print(f"TEXT API ERROR: {text_response.text}")
    text_response.raise_for_status()

output_text = text_response.text

# Parse prompts
concept = "Trending Snap Lens"
snap_prompt = ""
image_prompt = "portrait with creative AR face filter"

for line in output_text.splitlines():
    if line.startswith("[CONCEPT]:"):
        concept = line.replace("[CONCEPT]:", "").strip()
    elif line.startswith("[SNAP PROMPT]:"):
        snap_prompt = line.replace("[SNAP PROMPT]:", "").strip()
    elif line.startswith("[IMAGE PROMPT]:"):
        image_prompt = line.replace("[IMAGE PROMPT]:", "").strip()

if not snap_prompt:
    snap_prompt = output_text

print("Generating mockup image (Keyless)...")
encoded_img_prompt = urllib.parse.quote(image_prompt)
image_url = f"https://image.pollinations.ai/prompt/{encoded_img_prompt}?width=768&height=1024&nologo=true"

image_data = requests.get(image_url).content
with open("mockup.jpg", "wb") as f:
    f.write(image_data)

print("Sending to Telegram...")
message_caption = (
    f"✨ Daily Snap Lens Concept\n\n"
    f"Trend: {concept}\n\n"
    f"📋 Copy-Paste for Snap Lens AI:\n{snap_prompt}\n\n"
    f"🔍 Image Reference: Compare Snap's output to this mockup to catch errors."
)

telegram_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto"
with open("mockup.jpg", "rb") as photo:
    tg_response = requests.post(
        telegram_url,
        data={
            "chat_id": TELEGRAM_CHAT_ID,
            "caption": message_caption,
        },
        files={"photo": photo},
    )

if tg_response.status_code != 200:
    print(f"TELEGRAM ERROR: {tg_response.text}")
    tg_response.raise_for_status()

print("Daily prompt and mockup successfully sent!")
