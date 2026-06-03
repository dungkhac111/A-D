#!/usr/bin/env python3
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request


OK = 101
CORRUPT = 102
MUMBLE = 103
DOWN = 104
CHECK_FAILED = 110

CHECKER_TOKEN = os.environ.get("CHECKER_TOKEN", "checker-secret")
FLAG_PREFIX = os.environ.get("FLAG_PREFIX", "blockChainPTIT{")

ACTIONS = {"check", "put", "get"}


def env_int(name, default):
    try:
        return int(os.environ.get(name, default))
    except ValueError:
        print(f"checker failed: invalid integer env {name}={os.environ.get(name)!r}")
        raise SystemExit(CHECK_FAILED)


SERVICE_PORT = env_int("SERVICE_PORT", "8084")
TIMEOUT = env_int("CHECKER_TIMEOUT", "15")


class CheckerError(Exception):
    code = CHECK_FAILED


class Down(CheckerError):
    code = DOWN


class Mumble(CheckerError):
    code = MUMBLE


class Corrupt(CheckerError):
    code = CORRUPT


def die(code, message):
    print(message)
    raise SystemExit(code)


def request(base, path, method="GET", data=None, token=True):
    url = base.rstrip("/") + path
    body = None
    headers = {}
    if data is not None:
        body = urllib.parse.urlencode(data).encode()
        headers["Content-Type"] = "application/x-www-form-urlencoded"
    if token:
        headers["X-Checker-Token"] = CHECKER_TOKEN
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            return resp.status, resp.headers, resp.read()
    except urllib.error.HTTPError as exc:
        return exc.code, exc.headers, exc.read()
    except (OSError, TimeoutError) as exc:
        raise Down(f"service is unavailable: {exc}") from exc


def text_response(base, path):
    status, _headers, body = request(base, path, token=False)
    if status >= 500:
        raise Down(f"{path} returned HTTP {status}")
    if status != 200:
        raise Mumble(f"{path} returned HTTP {status}")
    return body.decode("utf-8", errors="replace")


def bytes_response(base, path):
    status, headers, body = request(base, path, token=False)
    if status >= 500:
        raise Down(f"{path} returned HTTP {status}")
    if status != 200:
        raise Mumble(f"{path} returned HTTP {status}")
    return headers, body


def parse_args(argv):
    if not argv:
        raise Mumble("missing action")

    if argv[0] in ACTIONS:
        action = argv[0]
        rest = argv[1:]
    elif len(argv) >= 2 and argv[1] in ACTIONS:
        action = argv[1]
        rest = [argv[0]] + argv[2:]
    elif len(argv) >= 3 and argv[2] in ACTIONS and argv[1].isdigit():
        action = argv[2]
        rest = [argv[0], argv[1]] + argv[3:]
    else:
        raise Mumble("usage: checker.py check|put|get HOST [PORT] ...")

    if not rest:
        raise Mumble("missing host")

    host = rest[0]
    tail = rest[1:]
    if host.startswith("http://") or host.startswith("https://"):
        base = host
    else:
        port = SERVICE_PORT
        if tail and tail[0].isdigit():
            port = int(tail[0])
            tail = tail[1:]
        base = f"http://{host}:{port}"
    return action, base, tail


def check(base):
    status, _headers, body = request(base, "/healthz", token=False)
    if status != 200:
        raise Down(f"/healthz returned HTTP {status}")
    try:
        health = json.loads(body.decode())
    except json.JSONDecodeError as exc:
        raise Mumble("/healthz is not valid JSON") from exc
    if health.get("ok") is not True:
        raise Mumble("/healthz does not report ok=true")

    page = text_response(base, "/")
    for marker in ("Blind Gallery AD", "Morning Atrium", "Server Corner"):
        if marker not in page:
            raise Mumble(f"homepage is missing marker: {marker}")

    detail = text_response(base, "/image?id=1")
    if "atrium.jpg" not in detail or "Morning Atrium" not in detail:
        raise Mumble("public image detail is broken")

    headers, image = bytes_response(base, "/download?file=atrium.jpg")
    if "image/jpeg" not in headers.get("Content-Type", ""):
        raise Mumble("download endpoint does not return image/jpeg")
    if not image.startswith(b"\xff\xd8") or not image.endswith(b"\xff\xd9"):
        raise Mumble("downloaded public image is not a valid JPEG envelope")

    status, _headers, _body = request(base, "/checker/get", method="POST", data={"flag_id": "probe"}, token=False)
    if status != 403:
        raise Mumble("checker endpoint must reject missing token with HTTP 403")

    print("OK")
    return OK


def validate_flag(flag):
    if not flag.startswith(FLAG_PREFIX) or not flag.endswith("}"):
        raise Mumble("flag has invalid format")


def put(base, args):
    if not args:
        raise Mumble("missing flag")
    if len(args) >= 2 and args[1].startswith(FLAG_PREFIX):
        flag_id = args[0]
        flag = args[1]
    else:
        flag = args[0]
        flag_id = f"{int(time.time())}_{os.urandom(4).hex()}"
    validate_flag(flag)

    status, _headers, body = request(base, "/checker/put", method="POST", data={"flag_id": flag_id, "flag": flag})
    if status >= 500:
        raise Down(f"/checker/put returned HTTP {status}")
    if status != 200:
        raise Mumble(f"/checker/put returned HTTP {status}")

    try:
        payload = json.loads(body.decode())
    except json.JSONDecodeError as exc:
        raise Mumble("/checker/put returned invalid JSON") from exc
    if payload.get("flag_id") != flag_id or not payload.get("filename") or not payload.get("passphrase"):
        raise Mumble("/checker/put returned incomplete placement data")

    print(flag_id)
    return OK


def get_flag(base, args):
    if len(args) < 2:
        raise Mumble("missing flag_id or expected flag")
    flag_id, expected = args[0], args[1]
    validate_flag(expected)

    status, _headers, body = request(base, "/checker/get", method="POST", data={"flag_id": flag_id})
    if status == 404:
        raise Corrupt("flag_id was not found")
    if status >= 500:
        raise Down(f"/checker/get returned HTTP {status}")
    if status != 200:
        raise Mumble(f"/checker/get returned HTTP {status}")

    actual = body.decode("utf-8", errors="replace").strip()
    if actual != expected:
        raise Corrupt("stored flag does not match expected flag")

    print("OK")
    return OK


def main():
    try:
        action, base, args = parse_args(sys.argv[1:])
        if action == "check":
            code = check(base)
        elif action == "put":
            code = put(base, args)
        elif action == "get":
            code = get_flag(base, args)
        else:
            raise Mumble("unknown action")
        raise SystemExit(code)
    except CheckerError as exc:
        die(exc.code, str(exc))
    except Exception as exc:
        die(CHECK_FAILED, f"checker failed: {exc}")


if __name__ == "__main__":
    main()
