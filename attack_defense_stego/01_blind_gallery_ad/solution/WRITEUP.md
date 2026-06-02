# Writeup Blind Gallery AD

Blind Gallery AD là một bài Attack/Defense kết hợp lỗ hổng web và steganography.

Checker đặt flag động vào service bằng cách tạo một ảnh JPEG private, nhúng flag vào ảnh bằng `steghide`, rồi lưu thông tin ảnh trong database.

## Ý Tưởng Khai Thác

Endpoint `/image?id=` bị SQL Injection. Attacker dùng `UNION SELECT` để đọc bảng `images`, từ đó lấy được:

```text
filename
passphrase
```

Sau đó attacker tải ảnh qua `/download?file=<filename>` và dùng `steghide extract` để lấy flag.

## Các Bước Tóm Tắt

1. Mở gallery public.
2. Kiểm tra `/image?id=1`.
3. Thử payload SQL Injection.
4. Xác định số cột bằng `UNION SELECT`.
5. Dump record `is_public=0`.
6. Lấy `filename` và `passphrase`.
7. Tải ảnh archive.
8. Dùng `steghide` extract flag.

## Phòng Thủ

Cách phòng thủ đúng là vá SQL Injection bằng parameterized query, đồng thời giữ nguyên cơ chế checker `put/get`.

Không nên xóa dữ liệu checker đã đặt, vì như vậy service có thể bị tính `CORRUPT`.
