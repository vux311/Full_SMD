# Danh sách các tính năng cần kiểm tra (Test Todo List)

Dựa trên yêu cầu dự án SMD (Syllabus Management and Digitalization System) và cấu trúc mã nguồn hiện tại, dưới đây là danh sách các kịch bản kiểm thử cần thực hiện bằng Selenium (tương tự như `login_test.py`).

## 1. Xác thực và Phân quyền (Authentication & RBAC)
- [x] **Đăng nhập (Admin):** Kiểm tra đăng nhập thành công.
- [x] **Đăng xuất:** Kiểm tra xóa session và quay về trang login.
- [ ] **Đăng nhập (Giảng viên/Lecturer):** Kiểm tra quyền hạn của giảng viên.
- [ ] **Đăng nhập (Hỗ trợ đào tạo/AA):** Kiểm tra quyền duyệt cấp 2.
- [ ] **Đăng nhập (Sinh viên):** Kiểm tra giao diện xem công khai.
- [ ] **Quên mật khẩu:** Kiểm tra luồng gửi mail khôi phục (nếu có).

## 2. Quản lý Đề cương (Syllabus Management - Dành cho Giảng viên)
- [x] **Tạo mới Đề cương (Dạng nháp):** Điền thông tin, lưu nháp thành công (Đã sửa lỗi không lưu được).
- [ ] **Chỉnh sửa Đề cương:** Thay đổi nội dung, chuẩn đầu ra (CLO), học liệu.
- [ ] **Gửi duyệt (Submit):** Chuyển trạng thái từ Nháp sang Chờ Duyệt.
- [ ] **Lịch sử phiên bản:** Kiểm tra xem danh sách các phiên bản cũ có hiển thị không.
- [ ] **So sánh phiên bản:** Kiểm tra công cụ AI Change Detection (so sánh 2 bản).

## 3. Quy trình Duyệt (Approval Workflow - Dành cho Trưởng bộ môn/AA)
- [ ] **Danh sách đề cương chờ duyệt:** Hiển thị đúng danh sách cần xử lý.
- [ ] **Duyệt đề cương (Approve):** Phê duyệt và chuyển trạng thái tiếp theo.
- [ ] **Từ chối đề cương (Reject):** Yêu cầu chỉnh sửa kèm theo lý do bắt buộc.
- [ ] **Thảo luận cộng tác (Collaborative Review):** Thêm bình luận/feedback vào đề cương.

## 4. Các tính năng nâng cao (AI & Visualization)
- [ ] **Bản đồ chuẩn đầu ra (CLO-PLO Mapping):** Kiểm tra bảng ánh xạ hiển thị đúng.
- [ ] **Cây phả hệ môn học (Subject Tree):** Kiểm tra hiển thị mối quan hệ tiên quyết/song hành.
- [ ] **Tóm tắt AI (AI Summary):** Kiểm tra nút bấm gọi AI và hiển thị kết quả tóm tắt.

## 5. Quản trị hệ thống (Admin)
- [ ] **Quản lý người dùng (User Management):** Tạo mới, khóa/mở khóa tài khoản.
- [ ] **Cấu hình hệ thống:** Thay đổi các tham số hệ thống.

## 6. Giao diện Sinh viên
- [ ] **Tìm kiếm đề cương:** Theo mã môn, tên môn, chuyên ngành.
- [ ] **Theo dõi (Follow):** Kiểm tra tính năng nhận thông báo khi đề cương thay đổi.
- [ ] **Báo lỗi (Feedback):** Gửi phản hồi về nội dung đề cương.
