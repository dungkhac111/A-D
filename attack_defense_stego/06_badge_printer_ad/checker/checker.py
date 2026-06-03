#!/usr/bin/env python3
import json, os, sys, time, urllib.error, urllib.parse, urllib.request
OK=101; CORRUPT=102; MUMBLE=103; DOWN=104; CHECK_FAILED=110
CHECKER_TOKEN=os.environ.get("CHECKER_TOKEN","checker-secret"); FLAG_PREFIX=os.environ.get("FLAG_PREFIX","blockChainPTIT{"); ACTIONS={"check","put","get"}
def env_int(name,default):
    try: return int(os.environ.get(name,default))
    except ValueError: print(f"checker failed: invalid integer env {name}={os.environ.get(name)!r}"); raise SystemExit(CHECK_FAILED)
SERVICE_PORT=env_int("SERVICE_PORT","8089"); TIMEOUT=env_int("CHECKER_TIMEOUT","15")
class CheckerError(Exception): code=CHECK_FAILED
class Down(CheckerError): code=DOWN
class Mumble(CheckerError): code=MUMBLE
class Corrupt(CheckerError): code=CORRUPT
def die(code,msg): print(msg); raise SystemExit(code)
def request(base,path,method="GET",data=None,token=True):
    body=None; headers={}
    if data is not None: body=urllib.parse.urlencode(data).encode(); headers["Content-Type"]="application/x-www-form-urlencoded"
    if token: headers["X-Checker-Token"]=CHECKER_TOKEN
    req=urllib.request.Request(base.rstrip("/")+path,data=body,headers=headers,method=method)
    try:
        with urllib.request.urlopen(req,timeout=TIMEOUT) as resp: return resp.status,resp.headers,resp.read()
    except urllib.error.HTTPError as exc: return exc.code,exc.headers,exc.read()
    except (OSError,TimeoutError) as exc: raise Down(f"service is unavailable: {exc}") from exc
def parse_args(argv):
    if not argv: raise Mumble("missing action")
    if argv[0] in ACTIONS: action=argv[0]; rest=argv[1:]
    elif len(argv)>=2 and argv[1] in ACTIONS: action=argv[1]; rest=[argv[0]]+argv[2:]
    elif len(argv)>=3 and argv[2] in ACTIONS and argv[1].isdigit(): action=argv[2]; rest=[argv[0],argv[1]]+argv[3:]
    else: raise Mumble("usage: checker.py check|put|get HOST [PORT] ...")
    if not rest: raise Mumble("missing host")
    host=rest[0]; tail=rest[1:]
    if host.startswith("http://") or host.startswith("https://"): base=host
    else:
        port=SERVICE_PORT
        if tail and tail[0].isdigit(): port=int(tail[0]); tail=tail[1:]
        base=f"http://{host}:{port}"
    return action,base,tail
def check(base):
    status,_h,body=request(base,"/healthz",token=False)
    if status!=200: raise Down(f"/healthz returned HTTP {status}")
    try: health=json.loads(body.decode())
    except json.JSONDecodeError as exc: raise Mumble("/healthz is not valid JSON") from exc
    if health.get("ok") is not True or health.get("challenge")!="badge": raise Mumble("/healthz returned unexpected challenge data")
    status,_h,body=request(base,"/",token=False)
    if status!=200: raise Mumble(f"homepage returned HTTP {status}")
    if "Badge Printer AD" not in body.decode("utf-8",errors="replace"): raise Mumble("homepage marker is missing")
    status,_h,_b=request(base,"/login",token=False)
    if status not in (200,302): raise Mumble(f"public probe returned HTTP {status}")
    status,_h,_b=request(base,"/checker/get",method="POST",data={"flag_id":"probe"},token=False)
    if status!=403: raise Mumble("checker endpoint must reject missing token with HTTP 403")
    print("OK"); return OK
def validate_flag(flag):
    if not flag.startswith(FLAG_PREFIX) or not flag.endswith("}"): raise Mumble("flag has invalid format")
def put(base,args):
    if not args: raise Mumble("missing flag")
    if len(args)>=2 and args[1].startswith(FLAG_PREFIX): flag_id,args_flag=args[0],args[1]
    else: args_flag=args[0]; flag_id=f"{int(time.time())}_{os.urandom(4).hex()}"
    validate_flag(args_flag)
    status,_h,body=request(base,"/checker/put",method="POST",data={"flag_id":flag_id,"flag":args_flag})
    if status>=500: raise Down(f"/checker/put returned HTTP {status}")
    if status!=200: raise Mumble(f"/checker/put returned HTTP {status}")
    try: payload=json.loads(body.decode())
    except json.JSONDecodeError as exc: raise Mumble("/checker/put returned invalid JSON") from exc
    if payload.get("flag_id")!=flag_id: raise Mumble("/checker/put returned wrong flag_id")
    print(flag_id); return OK
def get_flag(base,args):
    if len(args)<2: raise Mumble("missing flag_id or expected flag")
    flag_id,expected=args[0],args[1]; validate_flag(expected)
    status,_h,body=request(base,"/checker/get",method="POST",data={"flag_id":flag_id})
    if status==404: raise Corrupt("flag_id was not found")
    if status>=500: raise Down(f"/checker/get returned HTTP {status}")
    if status!=200: raise Mumble(f"/checker/get returned HTTP {status}")
    actual=body.decode("utf-8",errors="replace").strip()
    if actual!=expected: raise Corrupt("stored flag does not match expected flag")
    print("OK"); return OK
def main():
    try:
        action,base,args=parse_args(sys.argv[1:])
        code=check(base) if action=="check" else put(base,args) if action=="put" else get_flag(base,args) if action=="get" else (_ for _ in ()).throw(Mumble("unknown action"))
        raise SystemExit(code)
    except CheckerError as exc: die(exc.code,str(exc))
    except Exception as exc: die(CHECK_FAILED,f"checker failed: {exc}")
if __name__=="__main__": main()
