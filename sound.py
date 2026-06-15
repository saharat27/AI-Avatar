# from gtts import gTTS
# import os

# text = "สวัสดี ยินดีต้อนรับครับ"

# tts = gTTS(text=text, lang='th')
# tts.save("output.mp3")

# os.system("start output.mp3")

import speech_recognition as sr

r = sr.Recognizer()

with sr.Microphone() as source:
    print("พูดได้เลย...")
    audio = r.listen(source)

try:
    text = r.recognize_google(audio, language="th-TH")
    print("คุณพูดว่า:", text)
except:
    print("ฟังไม่รู้เรื่อง")