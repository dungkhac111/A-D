# ADArena / Hackerdom Integration

## Summary

`checker/checker.py` uses only Python standard library. It checks SLA and handles dynamic flag placement/retrieval for the Blind Gallery AD service.

The checker does not contain exploit logic. Attack logic is kept in `solution/exploit.py`.

## Suggested Platform Settings

```yaml
max_round: 20
round_time: 300
flag_lifetime: 5
service_port: 8084
flag_prefix: blockChainPTIT
```

With `round_time: 300` and `flag_lifetime: 5`, a flag should remain valid for about 25 minutes.

## Exit Codes

| Exit code | Meaning |
|---|---|
| 101 | OK |
| 102 | CORRUPT |
| 103 | MUMBLE |
| 104 | DOWN |
| 110 | CHECK FAILED |

## Supported Calling Styles

The checker supports both common Hackerdom/ForcAD styles:

```bash
python checker.py check 10.10.0.5
python checker.py 10.10.0.5 check
```

With explicit local port:

```bash
python checker.py check 127.0.0.1 8084
python checker.py 127.0.0.1 8084 check
```

Direct URL is also supported:

```bash
python checker.py check http://127.0.0.1:8084
```

If no port is provided, the checker uses `SERVICE_PORT`, default `8084`.

## check

```bash
python checker.py check 10.10.0.5
```

The checker verifies:

- `/healthz` returns valid JSON with `ok: true`.
- `/` renders the public gallery.
- `/image?id=1` renders a public image detail.
- `/download?file=atrium.jpg` returns a JPEG envelope.
- `/checker/get` rejects requests without checker token using HTTP 403.

## put

Hackerdom-style:

```bash
python checker.py put 10.10.0.5 flag_seed_123 'blockChainPTIT{example_flag}' 1
```

Local simplified style:

```bash
python checker.py put 127.0.0.1 8084 'blockChainPTIT{example_flag}'
```

The checker sends the flag to `/checker/put` and prints only `flag_id` to stdout. It does not print the passphrase or placement JSON.

## get

Hackerdom-style:

```bash
python checker.py get 10.10.0.5 flag_seed_123 'blockChainPTIT{example_flag}' 1
```

Local:

```bash
python checker.py get 127.0.0.1 8084 flag_seed_123 'blockChainPTIT{example_flag}'
```

The checker asks `/checker/get` for the flag and compares the returned value with the expected flag.

## Environment

Both service and checker use the same `CHECKER_TOKEN`.

```bash
CHECKER_TOKEN=checker-secret
SERVICE_PORT=8084
CHECKER_TIMEOUT=15
FLAG_PREFIX=blockChainPTIT{
```

For production AD, set a strong random `CHECKER_TOKEN` in the checksystem and service environment.
