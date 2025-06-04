<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Ứng dụng nhắn tin an toàn với mã hóa AES</title>
    <style>
        body { font-family: sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 900px; margin: 20px auto; padding: 20px; border: 1px solid #ddd; border-radius: 8px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }
        h1, h2 { color: #0056b3; }
        ul { list-style-type: disc; margin-left: 20px; }
        code { background-color: #f4f4f4; padding: 2px 4px; border-radius: 4px; }
        .note { background-color: #e6f7ff; border-left: 5px solid #007bff; padding: 10px; margin-top: 15px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Xây dựng ứng dụng nhắn tin an toàn trên Web sử dụng thuật toán mã hóa AES</h1>

        <p>Dự án này tập trung vào việc phát triển một ứng dụng nhắn tin an toàn, có thể truy cập qua giao diện web, tích hợp thuật toán mã hóa Advanced Encryption Standard (AES) để đảm bảo tính bảo mật và toàn vẹn của tin nhắn.</p>

        <h2>Mô tả bài toán / Yêu cầu:</h2>
        <ul>
            <li><strong>Sử dụng Socket:</strong> Ứng dụng phải sử dụng công nghệ Socket để giao tiếp theo thời gian thực, cho phép trao đổi tin nhắn tức thì giữa các người dùng.</li>
            <li><strong>Hoạt động trên Web, giao diện thân thiện:</strong> Ứng dụng phải hoạt động hoàn toàn trong trình duyệt web và có giao diện người dùng trực quan, dễ sử dụng và bắt mắt.</li>
            <li><strong>Có ô nhập mã khóa (độ dài tự do):</strong> Người dùng có khả năng nhập mã khóa mã hóa với độ dài tùy ý, mang lại sự linh hoạt trong cấu hình bảo mật.</li>
            <li><strong>Độ dài tin nhắn tự do:</strong> Ứng dụng phải hỗ trợ tin nhắn có độ dài tùy ý, cho phép người dùng gửi nhiều loại nội dung mà không bị hạn chế.</li>
        </ul>

        <h2>Công nghệ & Khái niệm (Dự kiến):</h2>
        <ul>
            <li><strong>Frontend:</strong> HTML, CSS, JavaScript (để xây dựng giao diện web tương tác)</li>
            <li><strong>Backend:</strong> Một ngôn ngữ phía máy chủ (ví dụ: Node.js, Python với Flask/Django, PHP, Java) để xử lý các kết nối socket và logic máy chủ.</li>
            <li><strong>Mạng:</strong> WebSockets (xây dựng trên TCP sockets) cho giao tiếp song công, liên tục.</li>
            <li><strong>Mật mã học:</strong> Triển khai hoặc sử dụng thuật toán mã hóa AES để truyền dữ liệu an toàn.</li>
        </ul>

    </div>
</body>
</html>
