from flask import Flask, request, send_file
import edge_tts
import asyncio
import os

app = Flask(__name__)

voice_map = {
    "瀚一": "zh-TW-YunJheNeural",
    "守一": "zh-TW-HsiaoYuNeural"
}

async def generate_audio(dialogue):
    output_file = "output.mp3"

    # 先清空檔案
    with open(output_file, "wb") as f:
        pass

    for i, (speaker, text) in enumerate(dialogue):
        voice = voice_map.get(speaker, "zh-TW-YunJheNeural")
        temp_file = f"part_{i}.mp3"

        tts = edge_tts.Communicate(text=text, voice=voice)
        await tts.save(temp_file)

        # 直接串接（不用 pydub）
        with open(output_file, "ab") as outfile, open(temp_file, "rb") as infile:
            outfile.write(infile.read())

    return output_file

@app.route("/tts", methods=["POST"])
def tts():
    raw = request.json["text"]
    lines = [l.strip() for l in raw.split("\n") if l.strip()]

    dialogue = []
    for line in lines:
        speaker, text = line.split("：")
        dialogue.append((speaker, text))

    output = asyncio.run(generate_audio(dialogue))

    return send_file(output, as_attachment=True)

port = int(os.environ.get("PORT", 5000))
app.run(host="0.0.0.0", port=port)
