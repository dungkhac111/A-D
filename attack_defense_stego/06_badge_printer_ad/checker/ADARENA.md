# T?ch H?p ADArena / Hackerdom

Port service: `8089`.

```yaml
max_round: 20
round_time: 300
flag_lifetime: 5
service_port: 8089
flag_prefix: blockChainPTIT
```

```bash
python checker.py check 127.0.0.1 8089
python checker.py put 127.0.0.1 8089 flag_seed "blockChainPTIT{example}" 1
python checker.py get 127.0.0.1 8089 flag_seed "blockChainPTIT{example}" 1
```
