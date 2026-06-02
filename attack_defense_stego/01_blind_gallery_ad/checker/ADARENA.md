# Tích Hợp ADArena / Hackerdom

## Tổng Quan

`checker/checker.py` dùng Python standard library để kiểm tra SLA, đặt flag động và đọc lại flag động cho service Blind Gallery AD.

Checker không chứa logic khai thác. Logic tấn công mẫu nằm trong:

```text
solution/exploit.py
```

## Cấu Hình Đề Xuất

```yaml
max_round: 20
round_time: 300
flag_lifetime: 5
service_port: 8084
flag_prefix: blockChainPTIT
```

Với `round_time: 300` và `flag_lifetime: 5`, mỗi flag nên còn hợp lệ khoảng 25 phút.

## Exit Code

| Exit code | Ý nghĩa |
|---|---|
| 101 | OK |
| 102 | CORRUPT |
| 103 | MUMBLE |
| 104 | DOWN |
| 110 | CHECK FAILED |

## Kiểu Gọi Được Hỗ Trợ

Checker hỗ trợ kiểu gọi phổ biến của Hackerdom/ForcAD:

```bash
python checker.py check 10.10.0.5
python checker.py 10.10.0.5 check
```

Khi test local có port cụ thể:

```bash
python checker.py check 127.0.0.1 8084
python checker.py 127.0.0.1 8084 check
```

Có thể truyền URL trực tiếp:

```bash
python checker.py check http://127.0.0.1:8084
```

Nếu không truyền port, checker dùng `SERVICE_PORT`, mặc định là `8084`.

## Mode check

```bash
python checker.py check 10.10.0.5
```

Checker kiểm tra:

- `/healthz` trả JSON hợp lệ với `ok: true`.
- `/` render được gallery public.
- `/image?id=1` render được chi tiết ảnh public.
- `/download?file=atrium.jpg` trả về JPEG hợp lệ.
- `/checker/get` từ chối request thiếu checker token bằng HTTP 403.

## Mode put

Kiểu Hackerdom:

```bash
python checker.py put 10.10.0.5 flag_seed_123 "blockChainPTIT{example_flag}" 1
```

Kiểu test local:

```bash
python checker.py put 127.0.0.1 8084 "blockChainPTIT{example_flag}"
```

Checker gửi flag vào `/checker/put` và chỉ in `flag_id` ra stdout. Checker không in passphrase hoặc dữ liệu placement.

## Mode get

Kiểu Hackerdom:

```bash
python checker.py get 10.10.0.5 flag_seed_123 "blockChainPTIT{example_flag}" 1
```

Kiểu test local:

```bash
python checker.py get 127.0.0.1 8084 flag_seed_123 "blockChainPTIT{example_flag}"
```

Checker gọi `/checker/get`, nhận flag service extract ra và so sánh với flag expected.

## Biến Môi Trường

Service và checker phải dùng cùng `CHECKER_TOKEN`.

```bash
CHECKER_TOKEN=checker-secret
SERVICE_PORT=8084
CHECKER_TIMEOUT=15
FLAG_PREFIX=blockChainPTIT{
```

Khi deploy thật, nên đổi `CHECKER_TOKEN` thành chuỗi bí mật mạnh.
