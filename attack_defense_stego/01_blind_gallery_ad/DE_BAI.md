# Đề Bài Attack/Defense CTF: Blind Gallery AD

## Thông Tin Chung

- Tên bài: Blind Gallery AD
- Chủ đề: SQL Injection, JPEG steganography, steghide
- Hình thức: Attack/Defense
- Độ khó đề xuất: Trung bình
- Flag format: `blockChainPTIT{}`

## Mô Tả

Blind Gallery là một web service gallery ảnh nội bộ. Người dùng bình thường chỉ thấy các ảnh public, còn checker có thể tạo các ảnh archive private cho từng round.

Mỗi flag động được checker nhúng vào một ảnh JPEG bằng `steghide`. Thông tin cần để tìm và giải ảnh gồm `filename` và `passphrase`, được lưu trong database của service.

## Root Bug

Endpoint xem ảnh:

```text
/image?id=<id>
```

dùng SQL query nối chuỗi trực tiếp với tham số `id`. Đội tấn công có thể dùng `UNION SELECT` để đọc các record `is_public=0`, từ đó lấy `filename` và `passphrase`.

Sau đó tải ảnh qua:

```text
/download?file=<filename>
```

và extract flag bằng:

```bash
steghide extract -sf <filename> -p <passphrase>
```

## Nhiệm Vụ Đội Chơi

### Attack

- Recon gallery public.
- Phát hiện SQL Injection ở `/image?id=`.
- Dùng `UNION SELECT` dump bảng `images`.
- Tìm record private do checker đặt.
- Tải ảnh archive.
- Dùng `steghide` với passphrase leak được để extract flag.

### Defense

- Vá SQL Injection bằng parameterized query.
- Không phá chức năng gallery public.
- Không phá checker endpoints `/checker/put` và `/checker/get`.
- Không xóa dữ liệu flag hợp lệ đã được checker đặt.

## Ghi Chú Cho Ban Tổ Chức

Checker dùng header `X-Checker-Token` để đặt và kiểm tra flag động. Token mặc định khi test local là:

```text
checker-secret
```

Khi deploy thật nên đổi token này thành chuỗi bí mật mạnh và cấu hình giống nhau cho service và checker.
