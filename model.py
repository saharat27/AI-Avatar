from google import genai
import os
from dotenv import load_dotenv

folder = r"C:\Users\VICTUS\Desktop\Salvator\AI Avatar\Sound_history"
os.makedirs(folder, exist_ok=True)

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=api_key)

models = client.models.list()

for m in models:
    print(m.name)