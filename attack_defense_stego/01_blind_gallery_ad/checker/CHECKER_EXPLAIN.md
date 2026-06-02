# Checker Explain

Checker có ba mode:

```bash
python3 checker.py check http://host:8084
python3 checker.py put http://host:8084 'blockChainPTIT{flag}'
python3 checker.py get http://host:8084 '<flag_id>' 'blockChainPTIT{flag}'
```

## check

Kiểm tra service sống và trang public gallery render được.

## put

Gọi `/checker/put` với header `X-Checker-Token`.

Service sẽ:

- Sinh filename archive.
- Sinh passphrase.
- Tạo JPEG cover.
- Nhúng flag vào JPEG bằng `steghide`.
- Lưu record private trong bảng `images`.

## get

Gọi `/checker/get` để service extract lại flag từ JPEG theo `flag_id`.

Nếu flag khác expected, checker fail.
