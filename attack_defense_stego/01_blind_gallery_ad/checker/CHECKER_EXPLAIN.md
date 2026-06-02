# Giải Trình Hoạt Động Checker

Checker nằm tại:

```text
checker/checker.py
```

Checker chỉ dùng Python standard library, không cần cài thêm package ngoài. File này dùng để chấm trạng thái service theo hướng Attack/Defense: checker chỉ kiểm tra SLA, đặt flag và đọc lại flag, không chứa logic khai thác.

Logic khai thác nằm riêng trong:

```text
solution/exploit.py
```

Việc tách này quan trọng vì checker không nên tiết lộ cách khai thác cho đội phòng thủ hoặc bị bundle nhầm vào môi trường chấm.

## Mã Trạng Thái

Checker trả exit code theo kiểu Hackerdom/ForcAD:

| Exit code | Ý nghĩa |
|---|---|
| 101 | OK - service hoạt động đúng |
| 102 | CORRUPT - flag đã đặt nhưng đọc lại sai hoặc bị mất |
| 103 | MUMBLE - service trả dữ liệu sai định dạng hoặc sai logic |
| 104 | DOWN - service không truy cập được hoặc lỗi hệ thống |
| 110 | CHECK FAILED - bản thân checker gặp lỗi ngoài dự kiến |

## Các Mode

Checker hỗ trợ cả hai kiểu truyền tham số:

```bash
python checker.py check 10.10.0.5
python checker.py 10.10.0.5 check
```

Khi test local có thể truyền thêm port:

```bash
python checker.py check 127.0.0.1 8084
python checker.py 127.0.0.1 8084 check
```

Checker cũng hỗ trợ truyền URL trực tiếp:

```bash
python checker.py check http://127.0.0.1:8084
```

Nếu hệ thống không truyền port, checker dùng biến môi trường `SERVICE_PORT`, mặc định là `8084`.

## check

Ví dụ:

```bash
python checker.py check 10.10.0.5
```

Checker kiểm tra:

- `/healthz` trả JSON hợp lệ và có `ok: true`.
- `/` render được gallery public.
- `/image?id=1` render được chi tiết ảnh public.
- `/download?file=atrium.jpg` trả về JPEG hợp lệ.
- `/checker/get` phải từ chối request thiếu `X-Checker-Token` bằng HTTP 403.

Checker không khai thác SQL Injection và không extract stego trong mode `check`.

## put

Kiểu hệ thống AD:

```bash
python checker.py put 10.10.0.5 flag_seed_123 "blockChainPTIT{example_flag}" 1
```

Kiểu test local:

```bash
python checker.py put 127.0.0.1 8084 "blockChainPTIT{example_flag}"
```

Checker gửi flag vào `/checker/put`. Service sẽ tạo ảnh JPEG, nhúng flag bằng `steghide`, rồi lưu record private vào database.

Khi chạy thành công, checker chỉ in ra một dòng `flag_id`, ví dụ:

```text
flag_seed_123
```

Checker không in `filename` hoặc `passphrase` ra stdout/stderr.

## get

Kiểu hệ thống AD:

```bash
python checker.py get 10.10.0.5 flag_seed_123 "blockChainPTIT{example_flag}" 1
```

Kiểu test local:

```bash
python checker.py get 127.0.0.1 8084 flag_seed_123 "blockChainPTIT{example_flag}"
```

Checker gửi `flag_id` vào `/checker/get`, nhận lại flag được service extract từ ảnh JPEG, rồi so sánh với flag gốc.

Nếu flag khác expected, checker trả `CORRUPT`.

## Biến Môi Trường

```text
CHECKER_TOKEN=checker-secret
SERVICE_PORT=8084
CHECKER_TIMEOUT=15
FLAG_PREFIX=blockChainPTIT{
```

Service và checker phải dùng cùng `CHECKER_TOKEN`.
