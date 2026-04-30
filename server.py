from flask import Flask, request, send_file
import edge_tts
import asyncio
from pydub import AudioSegment
import os

app = Flask(__name__)

voice_map = {
    "瀚一": "zh-TW-YunJheNeural",
    "守一": "zh-TW-HsiaoYuNeural"
}

async def generate_audio(dialogue):
    combined = AudioSegment.empty()

    for i, (speaker, text) in enumerate(dialogue):
        filename = f"part_{i}.mp3"
        voice = voice_map.get(speaker, "zh-TW-YunJheNeural")

        tts = edge_tts.Communicate(text=text, voice=voice)
        await tts.save(filename)

        seg = AudioSegment.from_mp3(filename)
        combined += seg + AudioSegment.silent(duration=500)

    combined.export("output.mp3", format="mp3")

@app.route("/tts", methods=["POST"])
def tts():
    raw = request.json["text"]
    lines = [l.strip() for l in raw.split("\n") if l.strip()]

    dialogue = []
    for line in lines:
        speaker, text = line.split("：")
        dialogue.append((speaker, text))

    asyncio.run(generate_audio(dialogue))

    return send_file("output.mp3", as_attachment=True)

port = int(os.environ.get("PORT", 5000))
app.run(host="0.0.0.0", port=port)
