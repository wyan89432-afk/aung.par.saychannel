import json, os, sys
from pathlib import Path
import requests
from yt_dlp import YoutubeDL

channel=os.environ.get("YOUTUBE_CHANNEL","@htunmin7245")
token=os.environ.get("TELEGRAM_BOT_TOKEN")
chat_id=os.environ.get("TELEGRAM_CHAT_ID")
if not token or not chat_id: sys.exit("Missing TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID")

state_file=Path("processed_ids.json")
try:
    processed=set(json.loads(state_file.read_text(encoding="utf-8"))) if state_file.exists() else set()
except Exception:
    processed=set()

with YoutubeDL({"quiet":True,"extract_flat":True,"playlistend":10}) as ydl:
    info=ydl.extract_info(f"https://www.youtube.com/{channel}/videos",download=False)

entries=[v for v in (info.get("entries") or []) if v and v.get("id")]
entries.reverse()
new=[v for v in entries if v["id"] not in processed]

for v in new:
    url=f"https://www.youtube.com/watch?v={v['id']}"
    message=f"🎬 {v.get('title','New YouTube video')}\n\n{url}"
    r=requests.post(f"https://api.telegram.org/bot{token}/sendMessage",json={"chat_id":chat_id,"text":message,"disable_web_page_preview":False},timeout=30)
    if not r.ok: raise RuntimeError(f"Telegram error {r.status_code}: {r.text}")
    processed.add(v["id"])
    print("Sent:",url)

state_file.write_text(json.dumps(sorted(processed)[-500:],indent=2),encoding="utf-8")
print("Done. New links:",len(new))
