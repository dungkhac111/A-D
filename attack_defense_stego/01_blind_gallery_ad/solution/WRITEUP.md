# Writeup

Blind Gallery AD giấu flag động trong JPEG bằng `steghide`. Flag được checker đặt vào record private.

Attacker khai thác SQL Injection ở `/image?id=` để đọc bảng `images`, lấy `filename` và `passphrase`, tải ảnh qua `/download`, rồi dùng `steghide extract`.

Defense đúng là vá SQL Injection bằng parameterized query nhưng giữ nguyên cơ chế checker put/get.
