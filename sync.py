import json, os, sys, tempfile
from pathlib import Path
import requests
from yt_dlp import YoutubeDL

channel=os.environ["YOUTUBE_CHANNEL"]
token=os.environ.get("TELEGRAM_BOT_TOKEN")
chat_id=os.environ.get("TELEGRAM_CHAT_ID")
if not token or not chat_id: sys.exit("Missing Telegram secrets")

state_file=Path("state.json")
state=json.loads(state_file.read_text()) if state_file.exists() else {"processed":[]}
done=set(state.get("processed",[]))

with YoutubeDL({"quiet":True,"extract_flat":True,"playlistend":10}) as ydl:
    info=ydl.extract_info(channel+"/videos", download=False)
entries=[e for e in (info.get("entries") or []) if e and e.get("id")]
entries.reverse()
new=[e for e in entries if e["id"] not in done]

with tempfile.TemporaryDirectory(prefix="yt_tg_") as tmp:
    tmp=Path(tmp)
    for e in new:
        vid=e["id"]; url=e.get("url") or "https://www.youtube.com/watch?v="+vid
        opts={"format":"bv*[height<=360][ext=mp4]+ba[ext=m4a]/b[height<=360][ext=mp4]/b[height<=360]","merge_output_format":"mp4","outtmpl":str(tmp/"%(id)s.%(ext)s"),"noplaylist":True}
        with YoutubeDL(opts) as ydl: ydl.download([url])
        video=next(iter(tmp.glob(vid+".mp4")),None)
        if not video: raise RuntimeError("No MP4 produced: "+vid)
        with video.open("rb") as f:
            r=requests.post(f"https://api.telegram.org/bot{token}/sendVideo",data={"chat_id":chat_id,"caption":e.get("title","New video")},files={"video":f},timeout=1800)
        r.raise_for_status()
        done.add(vid)
        video.unlink(missing_ok=True)

state_file.write_text(json.dumps({"processed":list(done)[-500:]},indent=2))
print("Done")
