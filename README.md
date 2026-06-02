# Web Steganography Attack/Defense CTF

Repo này là bản Attack/Defense tách riêng từ các bài Web Steganography Jeopardy.

Repo Jeopardy cũ được giữ nguyên. Các bài trong repo này dùng flag động do checker đặt vào service theo từng round.

## Cấu Trúc

```text
attack_defense_stego/
  <challenge>/
    service/        Source và Docker Compose để chạy service
      backend/      Backend Python xử lý web, dữ liệu và checker API
      frontend/     Template HTML và CSS giao diện web
    checker/        Checker dùng cho hệ thống chấm Attack/Defense
    solution/       Writeup, exploit mẫu và hướng phòng thủ
    DE_BAI.md       Đề bài cho người chơi
    challenge.yml   Metadata của challenge
```

## Danh Sách Bài

| STT | Tên | Kỹ thuật | Port | Trạng thái |
|---|---|---|---|---|
| 01 | Blind Gallery AD | SQL Injection + JPEG steghide | 8084 | Đã test check/put/get/exploit |
| 02 | Metadata Gallery AD | Header leak + PNG metadata | 8085 | Đã test check/put/get/exploit |
| 03 | QR Shadow Layer AD | QR SVG shadow layer | 8086 | Đã test check/put/get/exploit |
| 04 | CSS Color Encoding AD | Path traversal + CSS color encoding | 8087 | Đã test check/put/get/exploit |
| 05 | Tri-Modal Stego AD | API enum + LFI + split stego artifacts | 8088 | Đã test check/put/get/exploit |
| 06 | Badge Printer AD | JWT/IDOR theme + QR stego | 8089 | Đã test check/put/get/exploit |

## Chạy Local

Ví dụ chạy một bài:

```bash
cd attack_defense_stego/02_metadata_gallery_ad/service
docker compose up --build
```

Test checker:

```bash
cd attack_defense_stego/02_metadata_gallery_ad
python checker/checker.py check 127.0.0.1 8085
python checker/checker.py put 127.0.0.1 8085 flag_seed_demo "blockChainPTIT{demo_flag_1234567890abcdef}" 1
python checker/checker.py get 127.0.0.1 8085 flag_seed_demo "blockChainPTIT{demo_flag_1234567890abcdef}" 1
```

Checker chuẩn dùng exit code:

```text
101 OK
102 CORRUPT
103 MUMBLE
104 DOWN
110 CHECK FAILED
```

Khi đưa lên hệ thống thật, platform sẽ truyền IP service của từng team và flag random theo từng round. Không hard-code `127.0.0.1` trong checker.
