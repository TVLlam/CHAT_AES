# Xây dựng ứng dụng nhắn tin an toàn trên Web sử dụng thuật toán mã hóa AES

Dự án này tập trung vào việc phát triển một ứng dụng nhắn tin an toàn, có thể truy cập qua giao diện web, tích hợp thuật toán mã hóa Advanced Encryption Standard (AES) để đảm bảo tính bảo mật và toàn vẹn của tin nhắn.

## Mô tả bài toán / Yêu cầu:

Dựa trên các yêu cầu từ bài toán thực hành, ứng dụng cần đáp ứng các điểm sau:

* **Sử dụng Socket:** Ứng dụng phải sử dụng công nghệ Socket để giao tiếp theo thời gian thực, cho phép trao đổi tin nhắn tức thì giữa các người dùng.
* **Hoạt động trên Web, giao diện thân thiện:** Ứng dụng phải hoạt động hoàn toàn trong trình duyệt web và có giao diện người dùng trực quan, dễ sử dụng và bắt mắt.
* **Có ô nhập mã khóa (độ dài tự do):** Người dùng có khả năng nhập mã khóa mã hóa với độ dài tùy ý, mang lại sự linh hoạt trong cấu hình bảo mật.
* **Độ dài tin nhắn tự do:** Ứng dụng phải hỗ trợ tin nhắn có độ dài tùy ý, cho phép người dùng gửi nhiều loại nội dung mà không bị hạn chế.

## Công nghệ & Khái niệm (Dự kiến):

Để hoàn thành dự án này, các công nghệ và khái niệm sau đây có thể được áp dụng:

* **Frontend:** HTML, CSS, JavaScript (để xây dựng giao diện web tương tác).
* **Backend:** Một ngôn ngữ phía máy chủ (ví dụ: Node.js, Python với Flask/Django, PHP, Java) để xử lý các kết nối socket và logic máy chủ.
* **Mạng:** WebSockets (xây dựng trên TCP sockets) cho giao tiếp song công, liên tục.
* **Mật mã học:** Triển khai hoặc sử dụng thuật toán mã hóa AES để truyền dữ liệu an toàn.
