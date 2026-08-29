import os,sys,json,subprocess,requests
YOUTUBE_CHANNEL=os.environ.get("YOUTUBE_CHANNEL")
TOKEN=os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT=os.environ.get("TELEGRAM_CHAT_ID")
FILE="processed_ids.json"
def main():
 if not all([YOUTUBE_CHANNEL,TOKEN,CHAT]): sys.exit("Missing secrets")
 done=set(json.load(open(FILE))) if os.path.exists(FILE) else set()
 r=subprocess.run(["yt-dlp","--flat-playlist","--playlist-end","5","-J",f"https://www.youtube.com/{YOUTUBE_CHANNEL}/videos"],capture_output=True,text=True,check=True)
 videos=json.loads(r.stdout).get("entries",[]) or []
 new=[v for v in videos if v.get("id") not in done][:1]
 for v in new:
  vid=v["id"]; path=f"{vid}.mp4"
  try:
   subprocess.run(["yt-dlp","-f","bestvideo[height<=360]+bestaudio/best[height<=360]","--merge-output-format","mp4","-o",path,f"https://www.youtube.com/watch?v={vid}"],check=True)
   with open(path,"rb") as f:
    q=requests.post(f"https://api.telegram.org/bot{TOKEN}/sendVideo",data={"chat_id":CHAT,"caption":v.get("title","New video")},files={"video":f},timeout=300)
   q.raise_for_status(); done.add(vid)
  finally:
   if os.path.exists(path): os.remove(path)
 json.dump(sorted(done),open(FILE,"w"),indent=2)
if __name__=="__main__": main()