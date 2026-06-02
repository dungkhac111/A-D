#!/usr/bin/env python3
import os
import sys
import time
import urllib.parse
import urllib.request


TOKEN = os.environ.get("CHECKER_TOKEN", "checker-secret")


def post(base, path, data):
    body = urllib.parse.urlencode(data).encode()
    req = urllib.request.Request(
        base.rstrip("/") + path,
        data=body,
        headers={"X-Checker-Token": TOKEN, "Content-Type": "application/x-www-form-urlencoded"},
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        return resp.read().decode()


def get(base, path):
    with urllib.request.urlopen(base.rstrip("/") + path, timeout=15) as resp:
        return resp.read().decode(errors="replace")


def check(base):
    page = get(base, "/")
    assert "Blind Gallery AD" in page
    assert "Morning Atrium" in page
    print("OK")


def put(base, flag):
    flag_id = str(int(time.time())) + "_" + os.urandom(3).hex()
    result = post(base, "/checker/put", {"flag_id": flag_id, "flag": flag})
    print(flag_id)
    print(result.strip())


def get_flag(base, flag_id, expected=None):
    result = post(base, "/checker/get", {"flag_id": flag_id}).strip()
    if expected is not None and result != expected:
        raise SystemExit(f"flag mismatch: {result!r}")
    print(result)


def main():
    if len(sys.argv) < 3:
        raise SystemExit("usage: checker.py check|put|get BASE_URL [flag_or_flag_id] [expected]")
    action = sys.argv[1]
    base = sys.argv[2]
    if action == "check":
        check(base)
    elif action == "put":
        put(base, sys.argv[3])
    elif action == "get":
        get_flag(base, sys.argv[3], sys.argv[4] if len(sys.argv) > 4 else None)
    else:
        raise SystemExit("unknown action")


if __name__ == "__main__":
    main()
