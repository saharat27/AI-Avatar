# python -m streamlit run web_app.py
import streamlit as st
from google import genai
from gtts import gTTS
from mutagen.mp3 import MP3
import time, os, json, uuid, base64
from dotenv import load_dotenv
import re
from io import BytesIO

# load_dotenv()
# api_key = os.getenv("GEMINI_API_KEY")
# client = genai.Client(api_key=api_key)

api_key = st.secrets["GEMINI_API_KEY"]
client = genai.Client(api_key=api_key)

Avatar = [
    r'C:\Users\VICTUS\Desktop\Salvator\AI Avatar\Avatar\open mouth_1.png',
    r'C:\Users\VICTUS\Desktop\Salvator\AI Avatar\Avatar\open mouth_3.png',
    r'C:\Users\VICTUS\Desktop\Salvator\AI Avatar\Avatar\normal.png'
]
AVATAR_NORMAL = r'C:\Users\VICTUS\Desktop\Salvator\AI Avatar\Avatar\normal.png'

CHAT_DIR = "chats"
os.makedirs(CHAT_DIR, exist_ok=True)

st.set_page_config(page_title="AI Receptionist", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
* { font-family: 'Inter', sans-serif; }
.stApp {
    background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
    min-height: 100vh;
}
.main .block-container { padding-bottom: 90px !important; }
[data-testid="stSidebar"] {
    background: rgba(255,255,255,0.05) !important;
    backdrop-filter: blur(20px);
    border-right: 1px solid rgba(255,255,255,0.1);
}
[data-testid="stSidebar"] * { color: #e0e0e0 !important; }
[data-testid="stSidebar"] .stButton button {
    background: rgba(255,255,255,0.08) !important;
    border: 1px solid rgba(255,255,255,0.15) !important;
    border-radius: 10px !important;
    color: #e0e0e0 !important;
    font-size: 13px !important;
    transition: all 0.2s !important;
}
[data-testid="stSidebar"] .stButton button:hover {
    background: rgba(99,102,241,0.4) !important;
    border-color: #6366f1 !important;
}
.stApp h1,.stApp h2,.stApp h3,.stApp p,.stApp label { color: #f0f0f0 !important; }
[data-testid="stChatMessage"] {
    background: rgba(255,255,255,0.06) !important;
    border-radius: 16px !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    margin-bottom: 12px !important;
}
[data-testid="stChatMessage"] p { color: #e2e8f0 !important; }
[data-testid="stChatInput"] {
    background: rgba(255,255,255,0.08) !important;
    border: 1px solid rgba(99,102,241,0.4) !important;
    border-radius: 16px !important;
    color: white !important;
}
[data-testid="stChatInput"]:focus-within {
    border-color: #6366f1 !important;
    box-shadow: 0 0 0 3px rgba(99,102,241,0.2) !important;
}
[data-testid="stAlert"] {
    background: rgba(99,102,241,0.15) !important;
    border: 1px solid rgba(99,102,241,0.3) !important;
    border-radius: 12px !important;
    color: #c7d2fe !important;
}
hr { border-color: rgba(255,255,255,0.1) !important; }
.main .stButton button {
    background: rgba(99,102,241,0.2) !important;
    border: 1px solid rgba(99,102,241,0.4) !important;
    color: #c7d2fe !important;
    border-radius: 12px !important;
    transition: all 0.2s !important;
}
.main .stButton button:hover {
    background: rgba(99,102,241,0.4) !important;
    transform: translateY(-1px) !important;
}
audio {
    display: none !important;
}
.stCaption { color: #64748b !important; }
</style>
""", unsafe_allow_html=True)

def img_to_b64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

b64_normal = img_to_b64(AVATAR_NORMAL)
b64_open1  = img_to_b64(Avatar[0])
b64_open2  = img_to_b64(Avatar[1])

def text_to_speech_bytes(text):
    mp3_fp = BytesIO()
    tts = gTTS(text=text, lang='th', slow=False)
    tts.write_to_fp(mp3_fp)
    mp3_fp.seek(0)
    return mp3_fp

def get_audio_duration_bytes(mp3_fp):
    mp3_fp.seek(0)
    audio = MP3(mp3_fp)
    return audio.info.length

def play_audio(mp3_fp):
    mp3_fp.seek(0)
    st.audio(mp3_fp, format="audio/mp3", autoplay=True)

def avatar_html(b64_img):
    return f"""
    <div style="
        background: rgba(255,255,255,0.07);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255,255,255,0.12);
        border-radius: 24px;
        padding: 24px 20px;
        text-align: center;
        box-shadow: 0 8px 32px rgba(0,0,0,0.3);
    ">
        <img src="data:image/png;base64,{b64_img}"
             style="width:100%; border-radius:16px; display:block;">
        <p style="color:#a5b4fc; font-size:19px; font-weight:600; margin:12px 0 4px;">AI Avatar</p>
        <p style="color:#94a3b8; font-size:13px; margin:0 0 10px;">
            <span style="display:inline-block; width:9px; height:9px; background:#22c55e;
                         border-radius:50%; margin-right:5px; animation:pulse 2s infinite;"></span>
            AI Receptionist · Online
        </p>
        <hr style="border:none; border-top:1px solid rgba(255,255,255,0.1); margin:10px 0;">
    </div>
    <style>@keyframes pulse {{ 0%,100%{{opacity:1}} 50%{{opacity:.3}} }}</style>
    """

def get_response(messages):
    try:
        system_prompt = """คุณคือ "AI Avatar" ผู้ช่วยต้อนรับ AI
        นิสัย: สุภาพ มืออาชีพ เป็นมิตร
        หน้าที่: ตอบคำถามทั่วไปและช่วยเหลือผู้เยี่ยมชม
        ตอบเป็นภาษาที่ผู้ใช้พิมพ์ กระชับและชัดเจน"""
        contents = [
            {"role": "user" if m["role"] == "user" else "model",
             "parts": [{"text": m["content"]}]}
            for m in messages
        ]
        return client.models.generate_content(
            model="gemini-2.5-flash",
            contents=contents,
            config={"system_instruction": system_prompt}
        ).text
    except Exception as e:
        if "Error" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
            return "You have hit your limit for your AI Avatar."
        return f"Error: {e}"

def clean_text_for_tts(text):
    text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
    text = text.replace("*", "")
    return text

def load_chat(cid):
    fp = f"{CHAT_DIR}/{cid}.json"
    return json.load(open(fp, encoding="utf-8")) if os.path.exists(fp) else []

def save_chat(cid, history):
    """บันทึกเฉพาะเมื่อมีข้อความอย่างน้อย 1 ข้อความ"""
    if not history:
        return
    tmp   = f"{CHAT_DIR}/{cid}.tmp"
    final = f"{CHAT_DIR}/{cid}.json"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)
    os.replace(tmp, final)

def list_chats():
    return sorted(
        [f[:-5] for f in os.listdir(CHAT_DIR) if f.endswith(".json")],
        reverse=True
    )

def delete_chat(cid):
    fp = f"{CHAT_DIR}/{cid}.json"
    if os.path.exists(fp):
        os.remove(fp)

def get_latest_chat_id():
    chats = list_chats()
    return chats[0] if chats else None
if "initialized" not in st.session_state:
    st.session_state.initialized = True
    latest = get_latest_chat_id()
    if latest:
        st.session_state.chat_id  = latest
        st.session_state.messages = load_chat(latest)
    else:
        st.session_state.chat_id  = str(uuid.uuid4())
        st.session_state.messages = []

with st.sidebar:
    st.markdown("MENU")

    if st.button("New Chat", use_container_width=True):
        save_chat(st.session_state.chat_id, st.session_state.messages)
        st.session_state.chat_id  = str(uuid.uuid4())
        st.session_state.messages = []
        st.rerun()
    st.divider()
    st.markdown("History")

    chat_ids = list_chats()
    if not chat_ids:
        st.info("No chat history.")
    else:
        for cid in chat_ids:
            data  = load_chat(cid)
            first = next((m["content"] for m in data if m["role"] == "user"), "")
            preview = (first[:22] + "…") if len(first) > 22 else first or "Empty"
            label = f"{preview}" if cid == st.session_state.chat_id else preview
            c1, c2 = st.columns([5, 1])

            with c1:
                if st.button(label, key=f"load_{cid}", use_container_width=True):
                    save_chat(st.session_state.chat_id, st.session_state.messages)
                    st.session_state.chat_id  = cid
                    st.session_state.messages = load_chat(cid)
                    st.rerun()

            with c2:
                if st.button("Delete", key=f"del_{cid}"):
                    delete_chat(cid)
                    if st.session_state.chat_id == cid:
                        st.session_state.chat_id  = str(uuid.uuid4())
                        st.session_state.messages = []
                    st.rerun()

    st.divider()
    st.caption(f"Total Chats: {len(chat_ids)}")

col_avatar, col_chat = st.columns([1, 2.5], gap="large")

with col_avatar:
    avatar_slot = st.empty()
    avatar_slot.markdown(avatar_html(b64_normal), unsafe_allow_html=True)

with col_chat:   
        if not st.session_state.messages:
                st.info("สวัสดีครับ ผมคือ AI Avatar ลองถามคำถามได้เลย")
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])    


prompt = st.chat_input("Write a message...")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.spinner("AI Avatar is thinking..."):
        response = get_response(st.session_state.messages)

    st.session_state.messages.append({"role": "assistant", "content": response})
    save_chat(st.session_state.chat_id, st.session_state.messages)
    st.session_state.pending_audio = response
    st.rerun()

if "pending_audio" in st.session_state:
    clean_text = clean_text_for_tts(st.session_state.pending_audio)
    mp3_fp = text_to_speech_bytes(clean_text)
    duration = get_audio_duration_bytes(mp3_fp)
    mp3_fp.seek(0)
    play_audio(mp3_fp)
    frames = [b64_open1, b64_open2]
    start = time.time()
    i = 0

    while time.time() - start < duration:
        avatar_slot.markdown(avatar_html(frames[i % 2]), unsafe_allow_html=True)
        time.sleep(0.3)
        i += 1

    avatar_slot.markdown(avatar_html(b64_normal), unsafe_allow_html=True)
    del st.session_state.pending_audio
