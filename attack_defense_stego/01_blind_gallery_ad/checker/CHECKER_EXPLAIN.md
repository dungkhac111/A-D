# Checker Explain

Checker has three modes:

```bash
python checker.py check 127.0.0.1 8084
python checker.py put 127.0.0.1 8084 'blockChainPTIT{flag}'
python checker.py get 127.0.0.1 8084 '<flag_id>' 'blockChainPTIT{flag}'
```

It also supports direct URL mode:

```bash
python checker.py check http://127.0.0.1:8084
```

## Role Separation

- `checker/checker.py`: used by organizers/checksystem only. It checks SLA, puts dynamic flags, and gets dynamic flags.
- `solution/exploit.py`: used for writeup/attack demonstration. It contains exploit logic.

The checker does not leak filename/passphrase placement data to stdout during `put`; it prints only `flag_id`.

## Exit Codes

```text
101 OK
102 CORRUPT
103 MUMBLE
104 DOWN
110 CHECK FAILED
```

## check

The checker verifies:

- `/healthz` returns JSON with `ok: true`.
- `/` renders the public gallery.
- `/image?id=1` renders a public image detail.
- `/download?file=atrium.jpg` returns a JPEG envelope.
- `/checker/get` rejects requests without `X-Checker-Token`.

## put

The checker calls `/checker/put` with `X-Checker-Token`.

The service then:

- Generates an archive filename.
- Generates a passphrase.
- Creates a JPEG cover.
- Embeds the flag into the JPEG using `steghide`.
- Stores a private row in the `images` table.

## get

The checker calls `/checker/get` with `flag_id`, receives the extracted flag, and compares it with the expected flag.

If the value differs, checker returns `CORRUPT`.
