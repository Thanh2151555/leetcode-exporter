# LeetCode Exporter

Một công cụ tự động mạnh mẽ giúp bạn tải toàn bộ các bài tập đã giải (Accepted) trên LeetCode và tự động đẩy (push) lên một kho lưu trữ (repository) trên GitHub của bạn.

## Tính năng nổi bật
- Tự động đăng nhập LeetCode thông qua file cấu hình.
- Sử dụng API GraphQL của LeetCode để lấy dữ liệu nhanh và chính xác 100%, không lo giao diện web bị thay đổi.
- Tự động phát hiện và lấy code thật sự của bạn (bất kể ngôn ngữ nào như C++, Java, Python, v.v.).
- Tổ chức thư mục lưu trữ mã nguồn gọn gàng.
- Tự động tạo file `README.md` tổng hợp danh sách các bài bạn đã giải.
- Tự động commit và push toàn bộ lên GitHub.

## Yêu cầu hệ thống
- Python 3.9 trở lên.
- Trình duyệt Google Chrome đã cài đặt trên máy.

## Cài đặt

1. Mở Terminal (Command Prompt / PowerShell) và sao chép mã nguồn về máy:
   ```bash
   git clone <ĐƯỜNG_DẪN_REPO_CỦA_BẠN>
   cd leetcode-exporter
   ```

2. Tạo môi trường ảo (khuyến nghị) và cài đặt thư viện:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
   ```

## Cấu hình (config.yaml)

Bạn cần chỉnh sửa file `config.yaml` ở thư mục gốc của dự án với thông tin tài khoản LeetCode của mình:

```yaml
leetcode:
  username: "email_cua_ban@gmail.com"
  password: "mat_khau_leetcode"

output_path: ./exported_solutions
repo_path: .
log_level: INFO
headless: false
```
*Lưu ý: Nếu bật `headless: true`, chương trình sẽ chạy ngầm không hiện cửa sổ Chrome.*
================================================================
## Cách sử dụng
Chỉ cần chạy các lệnh này trong Terminal:
1. cd.... (VD: D:\Destop\ProjectUploadGit\leetcode-exporter)
2. .venv\Scripts\activate
3. python main.py
================================================================
**Quá trình chương trình hoạt động:**
1. Khởi động Chrome và tự động đăng nhập (nếu gặp xác thực Capcha hoặc Cloudflare, bạn có thể tự tay bấm xác thực trong cửa sổ Chrome).
2. Quét toàn bộ danh sách bài bạn đã giải (Accept).
3. Lần lượt tải mã nguồn từng bài về thư mục `exported_solutions`.
4. Viết lại một file `README.md` thống kê các bài tập.
5. Cuối cùng, chương trình sẽ tự động `git add .`, `git commit` và `git push` code của bạn lên GitHub.

## Xử lý sự cố
- **Bị đứng ở lúc đăng nhập:** Hãy tắt chương trình (`Ctrl + C`) và chạy lại `python main.py`. Đôi khi do mạng chậm hoặc LeetCode hỏi Captcha.
- **Lỗi không lấy được code:** Chương trình lấy bài qua giao thức API ngầm, bảo đảm không bao giờ thiếu code. Tuy nhiên nếu mạng chập chờn, chương trình sẽ báo lỗi tại bài đó và tự tải lại ở những lần chạy sau.

