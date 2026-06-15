from google import genai
from gtts import gTTS
import speech_recognition as sr
import os
from dotenv import load_dotenv

folder = r"C:\Users\VICTUS\Desktop\Salvator\AI Avatar\Sound_history"
os.makedirs(folder, exist_ok=True)

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

r = sr.Recognizer()
with sr.Microphone() as source:
    print("พูดได้เลย...")
    audio = r.listen(source)

try:
    text = r.recognize_google(audio, language="th-TH")
    print("คุณพูดว่า:", text)
except:
    print("ฟังไม่รู้เรื่อง")
    exit()

client = genai.Client(api_key=api_key)

response = client.models.generate_content(
    model="gemini-3.5-flash",
    contents=text
)

print("AI:", response.text)

file_path = os.path.join(folder, "output.mp3")

tts = gTTS(text=response.text, lang='th')
tts.save(file_path)

os.startfile(file_path)