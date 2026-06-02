# Hướng Phòng Thủ

## Lỗi Gốc

Root bug là SQL Injection trong endpoint:

```text
/image?id=
```

Service nối trực tiếp tham số `id` vào câu SQL, khiến attacker có thể dùng `UNION SELECT` để đọc record private.

## Cách Vá Đúng

- Không nối chuỗi SQL với dữ liệu người dùng nhập.
- Ép `id` thành số nguyên nếu logic chỉ cần ID dạng số.
- Dùng parameterized query.
- Không thay đổi hoặc xóa endpoint checker `/checker/put` và `/checker/get`.
- Không xóa bảng `flags` hoặc file media mà checker đã tạo.

Ví dụ hướng vá:

```python
image_id = int(image_id)
rows = db.execute(
    "SELECT title, filename, description FROM images WHERE id=? AND is_public=1",
    (image_id,),
).fetchall()
```

## Sau Khi Vá Cần Giữ Hoạt Động

Các chức năng sau vẫn phải chạy:

```text
GET /
GET /image?id=1
GET /download?file=<public-image>
POST /checker/put
POST /checker/get
```

Nếu vá làm checker không đặt hoặc đọc được flag thì service sẽ bị tính lỗi.
