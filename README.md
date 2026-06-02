# Web Steganography Attack/Defense CTF

Repo này là bản Attack/Defense tách riêng từ các bài Web Steganography Jeopardy.

Repo Jeopardy cũ được giữ nguyên. Các bài trong repo này dùng flag động do checker đặt vào service theo từng round.

## Cấu Trúc

```text
attack_defense_stego/
  <challenge>/
    service/        Source và Docker Compose để chạy service
      backend/      Backend Python xử lý gallery, database và checker API
      frontend/     Template HTML và CSS giao diện web
    checker/        Checker dùng cho hệ thống chấm Attack/Defense
    solution/       Writeup, exploit mẫu và hướng phòng thủ
    DE_BAI.md       Đề bài cho người chơi
    challenge.yml   Metadata của challenge
```

## Danh Sách Bài

| STT | Tên | Trạng thái |
|---|---|---|
| 01 | Blind Gallery AD | Hoàn chỉnh service, checker, attack và defense |

## Cách Chạy Nhanh

```bash
cd attack_defense_stego/01_blind_gallery_ad/service
docker compose up --build
```

Service mặc định chạy ở:

```text
http://127.0.0.1:8084
```

Test checker:

```bash
cd attack_defense_stego/01_blind_gallery_ad
python checker/checker.py check 127.0.0.1 8084
```

Nếu checker in `OK` và thoát với exit code `101` thì service đang hoạt động đúng.
