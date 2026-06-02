import base64, hashlib, html, json, os, secrets
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse
BASE_DIR=Path(__file__).resolve().parent; SERVICE_DIR=BASE_DIR.parent; FRONTEND_DIR=SERVICE_DIR/"frontend"; TEMPLATE_DIR=FRONTEND_DIR/"templates"; STATIC_DIR=FRONTEND_DIR/"static"; DATA_DIR=Path(os.environ.get("DATA_DIR",str(SERVICE_DIR/"data"))); STORE_DIR=DATA_DIR/"store"
CHECKER_TOKEN=os.environ.get("CHECKER_TOKEN","checker-secret"); CHALLENGE="trimodal"; NAME="Tri-Modal Stego AD"
def ensure_state(): STORE_DIR.mkdir(parents=True,exist_ok=True)
def read_store(flag_id):
    p=STORE_DIR/(flag_id+".json")
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None
def write_store(flag_id,payload): STORE_DIR.mkdir(parents=True,exist_ok=True); (STORE_DIR/(flag_id+".json")).write_text(json.dumps(payload),encoding="utf-8")
def png_bytes(text): return b"\x89PNG\r\n\x1a\nADSTEG"+text.encode("utf-8")
def hex_colors(text): return "\n".join(f".c{i:02d}{{color:#{ord(ch):02x}0000}}" for i,ch in enumerate(text))
def qr_svg(text):
    bits=''.join(format(b,'08b') for b in text.encode()); cells=[]
    for i,bit in enumerate(bits):
        x=16+(i%32)*8; y=64+(i//32)*8; color='#010101' if bit=='0' else '#020202'; cells.append(f'<rect class="shadow" x="{x}" y="{y}" width="8" height="8" fill="{color}"/>')
    return '<svg xmlns="http://www.w3.org/2000/svg" width="360" height="260" viewBox="0 0 360 260"><rect width="360" height="260" fill="#fff"/><text x="20" y="42" font-size="24">Badge QR</text>'+''.join(cells)+'</svg>'
def audio_text(flag):
    bits=''.join(format(b,'08b') for b in flag.encode()); return 'spectrogram tones hz per bit: '+','.join('2400' if bit=='1' else '1200' for bit in bits)
def make_payload(flag_id,flag):
    if CHALLENGE=="metadata":
        key=hashlib.sha256(flag_id.encode()).digest()[0]; enc=base64.b64encode(bytes([b^key for b in flag.encode()])).decode(); return {"flag_id":flag_id,"flag":flag,"key":key,"encoded":enc}
    if CHALLENGE=="qr": return {"flag_id":flag_id,"flag":flag,"svg":qr_svg(flag)}
    if CHALLENGE=="css": return {"flag_id":flag_id,"flag":flag,"css":hex_colors(flag)}
    if CHALLENGE=="trimodal":
        third=max(1,len(flag)//3); return {"flag_id":flag_id,"flag":flag,"exif":flag[:third],"mask":flag[third:2*third],"audio":flag[2*third:],"tones":audio_text(flag[2*third:])}
    if CHALLENGE=="badge": return {"flag_id":flag_id,"flag":flag,"svg":qr_svg(flag)}
    return {"flag_id":flag_id,"flag":flag}
def latest_payload():
    items=sorted(STORE_DIR.glob("*.json"),key=lambda p:p.stat().st_mtime,reverse=True)
    return json.loads(items[0].read_text(encoding="utf-8")) if items else make_payload("demo","blockChainPTIT{demo_dynamic_flag_not_for_scoring}")
def render(template_name,**ctx):
    text=(TEMPLATE_DIR/template_name).read_text(encoding="utf-8")
    for k,v in ctx.items(): text=text.replace("{{ "+k+" }}",str(v))
    return text
class Handler(BaseHTTPRequestHandler):
    server_version=NAME.replace(' ','')+"/1.0"
    def do_GET(self):
        parsed=urlparse(self.path); path=parsed.path; qs=parse_qs(parsed.query); payload=latest_payload()
        if path=="/": return self.send_text(render("index.html",name=html.escape(NAME),technique="API enum + LFI + split stego artifacts",probe="/api/manifest?case=latest"),"text/html; charset=utf-8")
        if path=="/static/style.css": return self.send_bytes((STATIC_DIR/"style.css").read_bytes(),"text/css; charset=utf-8")
        if path=="/healthz": return self.send_json({"ok":True,"challenge":CHALLENGE})
        if CHALLENGE=="metadata" and path=="/archive":
            self.send_response(200); self.send_header("Content-Type","text/html; charset=utf-8"); self.send_header("X-Archive-Key",str(payload["key"])); self.end_headers(); self.wfile.write(render("detail.html",name=NAME,body="<a href='/image/lake.png'>lake.png</a><p>CDN archived copy.</p>").encode()); return
        if CHALLENGE=="metadata" and path=="/image/lake.png": return self.send_bytes(png_bytes("tEXt:flag="+payload["encoded"]),"image/png")
        if CHALLENGE=="qr" and path=="/badge": return self.send_text(payload["svg"],"image/svg+xml")
        if CHALLENGE=="css" and path=="/debug/theme":
            name=qs.get("name",[""])[0]
            return self.send_text(payload["css"] if name=="internal" or ".." in name else "/* public theme */","text/css; charset=utf-8")
        if CHALLENGE=="trimodal" and path=="/api/manifest": return self.send_json({"case":"latest","photo":"/asset?name=../private/case-latest/photo.jpg","mask":"/asset?name=../private/case-latest/mask.png","signal":"/asset?name=../private/case-latest/signal.wav"})
        if CHALLENGE=="trimodal" and path=="/asset":
            name=qs.get("name",[""])[0]
            if "photo.jpg" in name: return self.send_bytes(png_bytes("EXIF:"+payload["exif"]),"image/jpeg")
            if "mask.png" in name: return self.send_bytes(png_bytes("LSB_BLUE:"+payload["mask"]),"image/png")
            if "signal.wav" in name: return self.send_bytes(("WAVTEXT:"+payload["tones"]+":"+payload["audio"]).encode(),"audio/wav")
            return self.send_bytes(b"not found\n","text/plain",HTTPStatus.NOT_FOUND)
        if CHALLENGE=="badge" and path=="/login": return self.send_text(render("login.html"),"text/html; charset=utf-8")
        if CHALLENGE=="badge" and path=="/badges": return self.send_text(render("detail.html",name=NAME,body="<a href='/badge?id=1'>Badge 1</a><a href='/badge?id=2'>Badge 2</a>"),"text/html; charset=utf-8")
        if CHALLENGE=="badge" and path=="/badge": return self.send_text(payload["svg"] if qs.get("id",[""])[0]=="17" else qr_svg("public badge"),"image/svg+xml")
        return self.send_bytes(b"not found\n","text/plain; charset=utf-8",HTTPStatus.NOT_FOUND)
    def do_POST(self):
        parsed=urlparse(self.path)
        if self.headers.get("X-Checker-Token")!=CHECKER_TOKEN: return self.send_bytes(b"forbidden\n","text/plain; charset=utf-8",HTTPStatus.FORBIDDEN)
        length=int(self.headers.get("Content-Length","0")); data=parse_qs(self.rfile.read(length).decode("utf-8",errors="replace"))
        if parsed.path=="/checker/put":
            flag_id=data.get("flag_id",[secrets.token_hex(6)])[0]; flag=data.get("flag",[""])[0]
            if not flag: return self.send_bytes(b"missing flag\n","text/plain; charset=utf-8",HTTPStatus.BAD_REQUEST)
            payload=make_payload(flag_id,flag); write_store(flag_id,payload); visible={k:v for k,v in payload.items() if k!="flag"}; return self.send_json(visible)
        if parsed.path=="/checker/get":
            flag_id=data.get("flag_id",[""])[0]; payload=read_store(flag_id)
            if not payload: return self.send_bytes(b"not found\n","text/plain; charset=utf-8",HTTPStatus.NOT_FOUND)
            return self.send_text(payload["flag"],"text/plain; charset=utf-8")
        return self.send_bytes(b"not found\n","text/plain; charset=utf-8",HTTPStatus.NOT_FOUND)
    def send_json(self,obj): self.send_text(json.dumps(obj),"application/json")
    def send_text(self,text,content_type,status=HTTPStatus.OK): self.send_bytes(text.encode("utf-8"),content_type,status)
    def send_bytes(self,data,content_type,status=HTTPStatus.OK): self.send_response(status); self.send_header("Content-Type",content_type); self.send_header("Content-Length",str(len(data))); self.end_headers(); self.wfile.write(data)
    def log_message(self,fmt,*args): print(f"{self.client_address[0]} - {fmt % args}")
if __name__=="__main__": ensure_state(); port=int(os.environ.get("PORT","8088")); print(f"Tri-Modal Stego AD listening on 0.0.0.0:{port}"); ThreadingHTTPServer(("0.0.0.0",port),Handler).serve_forever()

