import html
import os
import random
import secrets
import shutil
import sqlite3
import string
import subprocess
import tempfile
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse


BASE_DIR = Path(__file__).resolve().parent
SERVICE_DIR = BASE_DIR.parent
FRONTEND_DIR = SERVICE_DIR / "frontend"
TEMPLATE_DIR = FRONTEND_DIR / "templates"
STATIC_DIR = FRONTEND_DIR / "static"
DATA_DIR = Path(os.environ.get("DATA_DIR", str(SERVICE_DIR / "data")))
MEDIA_DIR = DATA_DIR / "media"
DB_PATH = DATA_DIR / "gallery.db"
CHECKER_TOKEN = os.environ.get("CHECKER_TOKEN", "checker-secret")


def ensure_state():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    MEDIA_DIR.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(DB_PATH)
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS images (
          id INTEGER PRIMARY KEY,
          title TEXT,
          filename TEXT,
          is_public INTEGER,
          description TEXT,
          flag_id TEXT
        )
        """
    )
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS flags (
          flag_id TEXT PRIMARY KEY,
          filename TEXT,
          passphrase TEXT
        )
        """
    )
    count = db.execute("SELECT COUNT(*) FROM images WHERE is_public=1").fetchone()[0]
    if count == 0:
        public = [
            (1, "Morning Atrium", "atrium.jpg", 1, "public lobby capture", None),
            (2, "Server Corner", "server_corner.jpg", 1, "sanitized infrastructure photo", None),
            (3, "Badge Desk", "badge_desk.jpg", 1, "front desk record", None),
        ]
        db.executemany("INSERT INTO images VALUES(?, ?, ?, ?, ?, ?)", public)
        for _, title, filename, *_ in public:
            make_cover_jpeg(MEDIA_DIR / filename, title)
    db.commit()
    db.close()


def connect_db():
    return sqlite3.connect(DB_PATH)


def rand_text(n=8):
    alphabet = string.ascii_lowercase + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(n))


def make_ppm(path, seed_text):
    random.seed(seed_text)
    width, height = 960, 600
    rows = bytearray()
    tint = random.randint(0, 70)
    for y in range(height):
        for x in range(width):
            r = 35 + x * 45 // width + y * 18 // height + tint // 3
            g = 48 + y * 76 // height + tint // 4
            b = 62 + x * 68 // width + tint // 2
            if 365 < y < 475 and 110 < x < 850:
                r, g, b = 70 + (x % 35), 62 + (y % 25), 52
            if 250 < x < 590 and 210 < y < 360:
                r, g, b = 28, 32, 36
            if 285 < x < 555 and 238 < y < 330:
                r, g, b = 44, 82, 98
            for cx, cy in [(190, 405), (620, 392), (755, 335)]:
                if abs(x - cx) + abs(y - cy) < 42:
                    r, g, b = 226, 190, 53
                if cx - 10 <= x <= cx + 10 and cy - 20 <= y <= cy + 20:
                    r, g, b = 30, 28, 24
            n = (x * 17 + y * 31) & 7
            rows.extend((min(255, r + n), min(255, g + n), min(255, b + n)))
    path.write_bytes(f"P6\n{width} {height}\n255\n".encode() + rows)


def make_cover_jpeg(path, seed_text):
    with tempfile.TemporaryDirectory() as tmp:
        ppm = Path(tmp) / "cover.ppm"
        make_ppm(ppm, seed_text)
        with path.open("wb") as out:
            subprocess.run(["cjpeg", "-quality", "90", str(ppm)], check=True, stdout=out)


def make_stego_jpeg(path, flag, passphrase):
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        cover = tmp / "cover.jpg"
        flag_file = tmp / "flag.txt"
        flag_file.write_text(flag, encoding="ascii")
        make_cover_jpeg(cover, flag)
        shutil.copyfile(cover, path)
        env = os.environ.copy()
        env["MALLOC_CHECK_"] = "0"
        subprocess.run(
            ["steghide", "embed", "-cf", str(path), "-ef", str(flag_file), "-p", passphrase, "-f"],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            env=env,
        )


def extract_stego(path, passphrase):
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "flag.txt"
        env = os.environ.copy()
        env["MALLOC_CHECK_"] = "0"
        subprocess.run(
            ["steghide", "extract", "-sf", str(path), "-p", passphrase, "-xf", str(out), "-f"],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            env=env,
        )
        return out.read_text(encoding="ascii")


def render_template(name, **context):
    template = (TEMPLATE_DIR / name).read_text(encoding="utf-8")
    for key, value in context.items():
        template = template.replace("{{ " + key + " }}", str(value))
    return template


def index_page():
    db = connect_db()
    rows = db.execute("SELECT id,title,filename,description FROM images WHERE is_public=1 ORDER BY id").fetchall()
    db.close()
    cards = []
    for image_id, title, filename, description in rows:
        cards.append(
            f"""<a class="card" href="/image?id={image_id}">
              <img src="/download?file={html.escape(filename)}" alt="{html.escape(title)}">
              <h2>{html.escape(title)}</h2>
              <p>{html.escape(description)}</p>
            </a>"""
        )
    return render_template("index.html", cards="".join(cards))


def image_page(image_id):
    db = connect_db()
    query = "SELECT title, filename, description FROM images WHERE id = '%s' AND is_public = 1" % image_id
    try:
        rows = db.execute(query).fetchall()
    except sqlite3.Error as exc:
        rows = [("SQL error", "", str(exc))]
    db.close()
    cards = []
    for title, filename, description in rows:
        img = f'<img src="/download?file={html.escape(str(filename))}" alt="{html.escape(str(title))}">' if filename else ""
        cards.append(
            f"""<article class="detail">
              {img}
              <h1>{html.escape(str(title))}</h1>
              <p>{html.escape(str(description))}</p>
              <code>{html.escape(str(filename))}</code>
            </article>"""
        )
    if not cards:
        cards.append("<article class='detail'><h1>No image</h1><p>No public image matched this id.</p></article>")
    return render_template("image.html", records="".join(cards))


class Handler(BaseHTTPRequestHandler):
    server_version = "BlindGalleryAD/1.0"

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        if path == "/":
            return self.send_text(index_page(), "text/html; charset=utf-8")
        if path == "/image":
            image_id = parse_qs(parsed.query).get("id", ["1"])[0]
            return self.send_text(image_page(image_id), "text/html; charset=utf-8")
        if path == "/download":
            filename = Path(parse_qs(parsed.query).get("file", [""])[0]).name
            target = MEDIA_DIR / filename
            if not target.is_file():
                return self.send_bytes(b"file not found\n", "text/plain; charset=utf-8", HTTPStatus.NOT_FOUND)
            return self.send_bytes(target.read_bytes(), "image/jpeg")
        if path == "/static/style.css":
            target = STATIC_DIR / "style.css"
            return self.send_bytes(target.read_bytes(), "text/css; charset=utf-8")
        if path == "/healthz":
            return self.send_bytes(b'{"ok": true}\n', "application/json")
        return self.send_bytes(b"not found\n", "text/plain; charset=utf-8", HTTPStatus.NOT_FOUND)

    def do_POST(self):
        parsed = urlparse(self.path)
        if self.headers.get("X-Checker-Token") != CHECKER_TOKEN:
            return self.send_bytes(b"forbidden\n", "text/plain; charset=utf-8", HTTPStatus.FORBIDDEN)
        length = int(self.headers.get("Content-Length", "0"))
        data = parse_qs(self.rfile.read(length).decode("utf-8", errors="replace"))
        if parsed.path == "/checker/put":
            flag_id = data.get("flag_id", [rand_text(12)])[0]
            flag = data.get("flag", [""])[0]
            if not flag:
                return self.send_bytes(b"missing flag\n", "text/plain; charset=utf-8", HTTPStatus.BAD_REQUEST)
            passphrase = "ad-" + rand_text(12)
            filename = f"archive_{flag_id}_{rand_text(6)}.jpg"
            path = MEDIA_DIR / filename
            make_stego_jpeg(path, flag, passphrase)
            db = connect_db()
            image_id = random.randint(1000, 999999)
            db.execute(
                "INSERT INTO images(id,title,filename,is_public,description,flag_id) VALUES(?,?,?,?,?,?)",
                (image_id, "Archive Evidence", filename, 0, f"passphrase: {passphrase}", flag_id),
            )
            db.execute("INSERT OR REPLACE INTO flags(flag_id,filename,passphrase) VALUES(?,?,?)", (flag_id, filename, passphrase))
            db.commit()
            db.close()
            body = f'{{"flag_id":"{flag_id}","image_id":{image_id},"filename":"{filename}","passphrase":"{passphrase}"}}\n'
            return self.send_text(body, "application/json")
        if parsed.path == "/checker/get":
            flag_id = data.get("flag_id", [""])[0]
            db = connect_db()
            row = db.execute("SELECT filename,passphrase FROM flags WHERE flag_id=?", (flag_id,)).fetchone()
            db.close()
            if not row:
                return self.send_bytes(b"not found\n", "text/plain; charset=utf-8", HTTPStatus.NOT_FOUND)
            flag = extract_stego(MEDIA_DIR / row[0], row[1])
            return self.send_text(flag, "text/plain; charset=utf-8")
        return self.send_bytes(b"not found\n", "text/plain; charset=utf-8", HTTPStatus.NOT_FOUND)

    def send_text(self, text, content_type, status=HTTPStatus.OK):
        self.send_bytes(text.encode(), content_type, status)

    def send_bytes(self, data, content_type, status=HTTPStatus.OK):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, fmt, *args):
        print(f"{self.client_address[0]} - {fmt % args}")


if __name__ == "__main__":
    ensure_state()
    port = int(os.environ.get("PORT", "8084"))
    server = ThreadingHTTPServer(("0.0.0.0", port), Handler)
    print(f"Blind Gallery AD listening on 0.0.0.0:{port}")
    server.serve_forever()
