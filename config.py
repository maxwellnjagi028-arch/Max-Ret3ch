import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

DB_PATH = DATA_DIR / "maxretch.db"
SECRET_KEY = os.getenv("SECRET_KEY", "maxret3ch_super_secret_ai_key_2026_futuristic_navy_kenya")
SESSION_COOKIE_NAME = "mrt_session"

# Business Information & Real Kenyan Presence
COMPANY_NAME = "MaxReT3ch AI"
COMPANY_TAGLINE = "Next-Generation AI Solutions, High-Performance Computing & Sustainable Tech"
COMPANY_EMAIL = "contact@maxret3ch.ai"
COMPANY_PHONE = "+254 111 641 296"
COMPANY_PHONE_RAW = "+254111641296"
COMPANY_WHATSAPP = "https://wa.me/254111641296"
COMPANY_ADDRESS = "Nairobi Innovation Hub, Silicon Savannah, Kenya"
TED_NAME = "Ted"
TED_TITLE = "Chief Autonomous AI Operations Specialist"

# Currency & Financial Standards (Kenya Shilling)
CURRENCY_SYMBOL = "KSh"
CURRENCY_CODE = "KES"
VAT_RATE = 0.16 # Standard 16% VAT

# 6 Core Business Verticals
VERTICALS = {
    "ai_solutions": "Artificial Intelligence Solutions",
    "software_dev": "Website & Software Development",
    "hardware": "Computer Hardware Sales, Repair & Refurbishment",
    "it_support": "IT Technical Support & Managed Services",
    "green_tech": "Green Tech & Electronic Waste Recycling",
    "education": "Technology Education & Programming Tutorials"
}

# Optional LLM API Key (if provided)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
