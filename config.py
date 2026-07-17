from dotenv import load_dotenv
from amadeus import Client
import googlemaps
import os

load_dotenv()

SERPAPI_API_KEY = os.getenv("SERPAPI_API_KEY")
CURRENCY_API_KEY = os.getenv("CURRENCY_API_KEY")
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")

AMADEUS_CLIENT_ID = os.getenv("AMADEUS_CLIENT_ID")
AMADEUS_CLIENT_SECRET = os.getenv("AMADEUS_CLIENT_SECRET")



REQUEST_HEADERS = {
    "Content-Type": "application/json"
}

# -----------------------------
# Ollama
# -----------------------------

OLLAMA_BASE_URL = os.getenv(
    "OLLAMA_BASE_URL",
    "http://localhost:11434",
)

OLLAMA_GENERATE_URL = f"{OLLAMA_BASE_URL}/api/generate"

OLLAMA_CHAT_URL = f"{OLLAMA_BASE_URL}/api/chat"

OLLAMA_MODEL = os.getenv(
    "OLLAMA_MODEL",
    "gemma4:e4b",
)

# -----------------------------
# Model defaults
# -----------------------------

OLLAMA_TEMPERATURE = float(
    os.getenv("OLLAMA_TEMPERATURE", "0.2")
)

OLLAMA_TOP_P = float(
    os.getenv("OLLAMA_TOP_P", "0.9")
)

OLLAMA_NUM_CTX = int(
    os.getenv("OLLAMA_NUM_CTX", "32768")
)

OLLAMA_TIMEOUT = int(
    os.getenv("OLLAMA_TIMEOUT", "120")
)

# -----------------------------
# Clients
# -----------------------------

amadeus = Client(
    client_id=AMADEUS_CLIENT_ID,
    client_secret=AMADEUS_CLIENT_SECRET,
)

gmaps = googlemaps.Client(
    key=GOOGLE_MAPS_API_KEY,
)