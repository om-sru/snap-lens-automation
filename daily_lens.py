import os
import requests
import urllib.parse
from google import genai
from google.genai import types

# 1. Fetch credentials from environment variables
GEMINI_KEY = os.environ.get("GEMINI_API_KEY")
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

client = genai.Client(api_key=GEMINI_KEY)

# 2. Instruct Gemini to conceptualize, format, and self-review
system_instruction = """
You are an expert Snapchat Lens Studio GenAI prompt engineer.
Your task:
1. Pick a high-engagement, trending AR lens aesthetic (e.g., Y2K chrome, cute anime accessories, surreal face distortion, glow neon, aesthetic grain).
2. Write a precise prompt compatible with Snapchat Lens Studio AI / Easy Lens:
   - Must use direct imperative instructions (e.g., 'Place...', 'Add...', 'Attach to forehead...').
   - Clearly state facial placement (e.g., 'sitting on head', 'around eyes', 'mouth open trigger').
   - Keep it focused on one strong visual transformation.
3. Self-review: Ensure no vague buzzwords like 'cinematic' or 'photorealistic'. The prompt must be concrete instructions.
4. Provide a descriptive image prompt for an AI image generator to predict what the user's face will look like with this lens.

Output format strictly:
[CONCEPT]: <1 line description>
[SNAP PROMPT]: <The exact text to paste into Snap Lens AI>
[IMAGE PROMPT]: <A portrait photo description showing a person wearing this AR filter, neutral lighting, looking at camera>
"""

response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents="Generate today's trending Snapchat AR lens concept, verified Snap AI prompt, and mockup image prompt.",
    config=types.GenerateContentConfig(
        system_instruction=system_instruction,
        temperature=0.8,
    ),
)

output_text = response.text

# 3. Parse out the prompts
concept = ""
snap_prompt = ""
image_prompt = ""

for line in output_text.splitlines():
    if line.startswith("[CONCEPT]:"):
        concept = line.replace("[CONCEPT]:", "").strip()
    elif line.startswith("[SNAP PROMPT]:"):
        snap_prompt = line.replace("[SNAP PROMPT]:", "").strip()
    elif line.startswith("[IMAGE PROMPT]:"):
        image_prompt = line.replace("[IMAGE PROMPT]:", "").strip()

# Fallback if structure varies
if not snap_prompt:
    snap_prompt = output_text

# 4. Generate the Mockup Image using Pollinations (100% Free)
encoded_prompt = urllib.parse.quote(image_prompt if image_prompt else "portrait with creative AR face filter")
image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=768&height=1024&nologo=true"

# Download the generated mockup
image_data = requests.get(image_url).content
with open("mockup.jpg", "wb") as f:
    f.write(image_data)

# 5. Send to Telegram
message_caption = (
    f"✨ *Daily Snap Lens Concept*\n\n"
    f"*Trend:* {concept}\n\n"
    f"*📋 Copy-Paste for Snap Lens AI:*\n`{snap_prompt}`\n\n"
    f"🔍 *Image Reference:* Compare Snap's output to this mockup to catch errors."
)

telegram_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto"
with open("mockup.jpg", "rb") as photo:
    requests.post(
        telegram_url,
        data={
            "chat_id": TELEGRAM_CHAT_ID,
            "caption": message_caption,
            "parse_mode": "Markdown",
        },
        files={"photo": photo},
    )

print("Daily prompt and mockup successfully sent!")
