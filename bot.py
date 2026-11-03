import os, json, urllib.request, urllib.parse, yt_dlp, requests, time, threading
from http.server import HTTPServer, BaseHTTPRequestHandler

TOKEN = os.environ.get("BOT_TOKEN", "9057252752:AAHNiDeVgIn0YhokiLK9um-16sSE3eQdeVM")

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'Bot is alive!')

def run_web():
    port = int(os.environ.get("PORT", 10000))
    HTTPServer(('0.0.0.0', port), Handler).serve_forever()

threading.Thread(target=run_web, daemon=True).start()

def api(m, d=None):
    url = f"https://api.telegram.org/bot{TOKEN}/{m}"
    if d:
        d = urllib.parse.urlencode(d).encode()
    try:
        with urllib.request.urlopen(url, d, timeout=60) as r:
            return json.loads(r.read().decode())
    except:
        return {}

print("Bot LIVE!")
offset = 0
while True:
    try:
        upd = api(f"getUpdates?offset={offset}&timeout=40")
        if not upd.get('result'):
            continue
        for u in upd['result']:
            offset = u['update_id'] + 1
            if 'message' not in u:
                continue
            chat_id = u['message']['chat']['id']
            text = u['message'].get('text','')
            if text.startswith('/start'):
                api("sendMessage", {'chat_id': chat_id, 'text': 'Я онлайн 24/7! Кидай ссылку 📥'})
            elif "instagram.com" in text:
                api("sendMessage", {'chat_id': chat_id, 'text': '⏳ Качаю...'})
                fname=None
                try:
                    opts={'outtmpl':'/tmp/%(id)s.%(ext)s','format':'best[filesize<45M]/worst','quiet':True}
                    with yt_dlp.YoutubeDL(opts) as ydl:
                        info=ydl.extract_info(text,download=True)
                        fname=ydl.prepare_filename(info)
                    with open(fname,'rb') as f:
                        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendVideo", data={'chat_id':chat_id}, files={'video':f}, timeout=120)
                except Exception as e:
                    api("sendMessage", {'chat_id':chat_id,'text':f'❌ {e}'})
                finally:
                    try:
                        if fname and os.path.exists(fname):
                            os.remove(fname)
                    except:
                        pass
    except:
        time.sleep(5)
