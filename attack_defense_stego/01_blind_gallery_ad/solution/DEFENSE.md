# Defense

Root bug là SQL Injection trong `/image?id=`.

Vá đúng:

- Không nối chuỗi SQL với `id`.
- Ép `id` thành số nguyên.
- Dùng parameterized query.
- Không thay đổi `/checker/put` và `/checker/get`.
- Không xóa bảng `flags` hoặc file media checker đã tạo.

Sau khi vá, các chức năng sau vẫn phải chạy:

```text
GET /
GET /image?id=1
GET /download?file=<public-image>
POST /checker/put
POST /checker/get
```
