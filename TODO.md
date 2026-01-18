# TODO LIST - SDM Project (Syllabus Design & Management)

## 1. Hệ thống lõi (Core System)
- [x] Đảm bảo tính nhất quán dữ liệu Assessment Scheme (Tổng trọng số 100%).
- [x] Sửa lỗi kiểu dữ liệu BigInteger cho Foreign Keys trên SQL Server.
- [x] Cập nhật script seeding hỗ trợ đầy đủ các thực thể mới (Snapshots, Workflow logs, Assessments).
- [x] Khắc phục lỗi lưu trữ lồng nhau cho PLO Mapping và CLO References.

## 2. Thông báo & Tương tác (Notifications & Interaction)
- [x] Tích hợp Flask-Mail gửi thông báo qua Email khi có sự kiện quan trọng.
- [x] Tích hợp real-time notifications qua WebSockets (Flask-SocketIO).
- [x] Xây dựng hệ thống Template thông báo linh hoạt (Notification Templates).

## 3. Quản lý phiên bản & Audit Trail (Version Control & Audit)
- [x] Triển khai Syllabus Snapshots (lưu trữ bản ghi bất biến sau khi phê duyệt).
- [x] Ghi chép lịch sử Workflow chi tiết (Workflow Logs).
- [x] Xây dựng API So sánh phiên bản (Version Comparison/Diff API).
- [x] Giao diện Front-end: Xem lại các phiên bản lịch sử (History View).
- [x] Giao diện Front-end: So sánh hai phiên bản đề cương (Diff View - AI Powered).

## 4. Trí tuệ nhân tạo (AI Integration)
- [x] Phân tích sự phù hợp CLO - PLO bằng Gemini AI.
- [x] Gợi ý ma trận đánh giá (Assessment Schemes) từ CLO.
- [x] Cập nhật AI Service hỗ trợ SDK mới nhất và Model Gemini 3 Flash.
- [x] Triển khai xử lý hậu trường (Background Tasks) bằng Celery cho các tác vụ AI nặng.
- [ ] Tối ưu hóa mô hình nhúng (Embedding) để tìm kiếm đề cương tương tự.

## 5. Quy trình & Phê duyệt (Workflow & Approval)
- [x] Hoàn thiện Logic chuyển trạng thái Workflow (Draft -> Pending -> Approved/Returned).
- [x] Quản lý thời hạn phê duyệt (Review Deadlines) và Banner cảnh báo.
- [x] Tự động hóa kiểm tra deadline hàng ngày (Script check_deadlines.py).
- [x] Nhắc nhở qua Email cho các task sắp đến hạn.

## 6. Front-end (UI/UX)
- [x] Hiển thị Banner trạng thái và Deadline trên giao diện chi tiết.
- [x] Dashboard cho Admin: Tích hợp KPIs (Thời gian duyệt TB, tỷ lệ hoàn thành).
- [x] Cây quan hệ học phần trực quan (Subject Relationship Tree).
- [x] Form nhập liệu động cho Assessment Components.

## 8. Dữ liệu & Tìm kiếm (Data & Search)
- [x] Báo cáo Phân tích Tác động (Impact Analysis) cho Hiệu trưởng.
- [x] Tích hợp Elasticsearch cho tìm kiếm đề cương (Subject Code/Name).
- [x] Xây dựng Module OCR để số hóa dữ liệu từ PDF/Word cũ.

## 7. Khác (Others)
- [ ] Triển khai Unit Tests cho Service layer.
- [x] Xây dựng tài liệu API (Swagger/OpenAPI) cơ bản cho các endpoint chính.
- [x] Dockerize toàn bộ hệ thống (Web + API + DB + Redis + Celery).
