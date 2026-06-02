# Đề bài Attack/Defense CTF: Blind Gallery AD

## Thông tin chung

- Tên bài: Blind Gallery AD
- Chủ đề: SQL Injection, JPEG steganography, steghide
- Hình thức: Attack/Defense
- Độ khó đề xuất: Trung bình
- Flag format: `blockChainPTIT{}`

## Mô tả

Blind Gallery là một web service gallery ảnh nội bộ. Người dùng bình thường chỉ thấy ảnh public, trong khi checker có thể tạo các ảnh archive private cho từng round.

Mỗi flag động được checker nhúng vào một ảnh JPEG bằng `steghide`. Metadata cần để tìm ảnh gồm `filename` và `passphrase` được lưu trong bảng `images`.

## Root bug

Endpoint xem ảnh:

```text
/image?id=<id>
```

dùng SQL query nối chuỗi trực tiếp với tham số `id`. Attacker có thể dùng `UNION SELECT` để đọc các record `is_public=0`, từ đó lấy `filename` và `passphrase`.

Sau đó attacker tải ảnh qua:

```text
/download?file=<filename>
```

và extract flag bằng:

```bash
steghide extract -sf <filename> -p <passphrase>
```

## Nhiệm vụ đội chơi

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

## Ghi chú

Checker dùng header `X-Checker-Token` để đặt và kiểm tra flag động. Token mặc định trong môi trường local là `checker-secret`.
