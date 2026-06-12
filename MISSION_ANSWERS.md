# Day 12 Lab - Mission Answers

## Part 1: Localhost vs Production

### Exercise 1.1: Anti-patterns found
1. Hardcode API Key trực tiếp trong mã nguồn.
2. Cấu hình Port cố định, không thể thay đổi thông qua biến môi trường.
3. Không có health check hoặc readiness endpoints.
4. Bật chế độ Debug mode (`DEBUG=True`) trên môi trường thực tế, tiềm ẩn rủi ro lộ mã nguồn.
5. Không có cơ chế Graceful Shutdown, khi tắt server các tiến trình đang chạy có thể bị dừng đột ngột gây mất mát dữ liệu.

### Exercise 1.3: Comparison table
| Feature | Develop | Production | Tại sao quan trọng? |
|---------|---------|------------|---------------------|
| Config  | Hardcode trong file | Biến môi trường (Env vars) | Đảm bảo an toàn bảo mật, linh hoạt khi đổi môi trường mà không cần sửa code. |
| Health check | Không có | Có endpoints `/health` và `/ready` | Giúp Load Balancer/Orchestrator biết tình trạng container để restart hoặc điều hướng traffic. |
| Logging | Sử dụng `print()` | Sử dụng JSON Structured Logging | Giúp dễ dàng tổng hợp, lọc và phân tích log trên các hệ thống giám sát. |
| Shutdown| Dừng đột ngột | Graceful Shutdown | Tránh lỗi ngắt kết nối giữa chừng, đảm bảo xử lý hết request đang dang dở. |

## Part 2: Docker

### Exercise 2.1: Dockerfile questions
1. **Base image:** Thường là `python:3.11-slim` để giảm dung lượng file.
2. **Working directory:** Thường là `/app`.
3. **Tại sao COPY requirements.txt trước:** Tận dụng Docker Cache. Vì file requirements ít thay đổi nên layer này sẽ được cache lại, không phải tốn thời gian tải lại pip install liên tục khi chỉ thay đổi mã nguồn.
4. **CMD vs ENTRYPOINT khác nhau thế nào:** `ENTRYPOINT` xác định lệnh chính để thực thi, khó bị ghi đè. `CMD` cung cấp đối số mặc định, rất dễ bị ghi đè khi chạy lệnh docker run.

### Exercise 2.3: Image size comparison
- Develop: ~1GB (nếu sử dụng base image full Python)
- Production: ~150-300MB (nếu sử dụng python-slim và multi-stage builds)
- Difference: Giảm đáng kể khoảng 70-80% dung lượng, giúp thời gian tải và deploy nhanh hơn.

## Part 3: Cloud Deployment

### Exercise 3.1: Railway deployment
- URL: (Vui lòng thay bằng URL của bạn sau khi deploy)
- Screenshot: `[Link to screenshot in repo]`

## Part 4: API Security

### Exercise 4.1-4.3: Test results
- Khi không truyền Header `X-API-Key`: Nhận HTTP 401 Unauthorized.
- Khi truyền đúng `X-API-Key`: Nhận kết quả HTTP 200 OK từ AI Agent.
- Khi test Rate Limiting gọi liên tục 15-20 lần: Trả về HTTP 429 Too Many Requests sau khi quá giới hạn cho phép trong khoảng thời gian cửa sổ.

### Exercise 4.4: Cost guard implementation
- **Cách tiếp cận:** Sử dụng Redis làm bộ nhớ in-memory phân tán. Mỗi người dùng có một Redis key riêng (ví dụ: `budget:user_id:2026-06`) lưu chi phí tổng cộng trong tháng.
- Trước khi gọi LLM, server kiểm tra giá trị hiện tại, nếu vượt ngưỡng ($10) thì trả về HTTP 402 Payment Required.
- Sau khi LLM phản hồi, tăng `incrbyfloat` lượng tiền token tiêu thụ vào khóa Redis và đặt TTL là hơn 1 tháng.

## Part 5: Scaling & Reliability

### Exercise 5.1-5.5: Implementation notes
- **Stateless:** Dữ liệu context hội thoại phải đưa toàn bộ vào Redis. Việc lưu state ở biến cục bộ Python sẽ dẫn đến lỗi khi load balancer điều hướng request kế tiếp tới một Container Agent khác.
- **Graceful Shutdown:** Bắt tín hiệu `SIGTERM` (do hệ điều hành hoặc Docker/K8s gửi), chặn các request mới, chờ các request đang chạy hiện tại phản hồi xong, rồi tắt các connection đến Redis một cách an toàn trước khi đóng hẳn application.
