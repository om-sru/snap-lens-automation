import os
import requests
import urllib.parse

# 1. Fetch Telegram credentials
TELEGRAM_BOT_TOKEN = (
    os.environ.get("TELEGRAM_BOT_TOKEN")
    or os.environ.get("TELEGRAMBOTTOKEN")
    or os.environ.get("BOT_TOKEN")
)
TELEGRAM_CHAT_ID = (
    os.environ.get("TELEGRAM_CHAT_ID")
    or os.environ.get("TELEGRAMCHATID")
    or os.environ.get("CHATID")
    or os.environ.get("CHAT_ID")
)

if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
    raise ValueError("CRITICAL: Secrets were not passed to Python!")

# --- UPGRADED SNAP LENS GENAI PROMPT ---
ai_prompt = """
You are an elite Snapchat AR Lens Creator and TikTok Trend Analyst.
Your task:
1. Identify a highly viral, trending AR lens concept (e.g., 'Crying Makeup', 'Y2K Cyberpunk Glasses', 'Cartoon Face Morph', 'Vintage VHS Cam').
2. Write an incredibly precise, technical prompt formatted EXACTLY for Snapchat Lens Studio's GenAI Suite.
   - Snap GenAI works best with literal, physical descriptions of 3D assets, 2D face textures, and ML Face Effects.
   - Use direct commands (e.g., "Create a 3D asset of...", "Generate a face mesh texture with...").
   - Describe materials, lighting, and exact placement (e.g., "neon glowing pink plastic", "attached to the cheekbones", "soft studio lighting").
   - Never use vague buzzwords. Be a literal technical director.

Output format strictly like this:
[CONCEPT]: <Name of the Viral Trend>
[SNAP PROMPT]: <The exact, highly descriptive technical prompt to paste directly into Snap Lens GenAI>
[IMAGE PROMPT]: <A photorealistic portrait of a person wearing this exact AR filter, looking at the camera>
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
concept = "Viral Snap Lens"
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
    f"🔥 Viral Snap Lens Concept\n\n"
    f"Trend: {concept}\n\n"
    f"📋 Copy-Paste exactly into Snap Lens AI:\n{snap_prompt}\n\n"
    f"🔍 Image Reference: Try to match this visual target."
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
