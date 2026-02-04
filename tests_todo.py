import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

class SMDComprehensiveTest(unittest.TestCase):
    """
    File test tổng thể các tính năng của hệ thống SMD.
    Dựa trên cấu trúc của login_test.py, các hàm dưới đây là khung sườn (boilerplate)
    để phát triển các kịch bản kiểm thử tự động.
    """

    def setUp(self):
        # Cấu hình Chrome Driver (có thể thay đổi sang Headless nếu chạy trên server)
        self.driver = webdriver.Chrome()
        self.driver.implicitly_wait(10)
        self.base_url = "http://localhost:3000"

    def tearDown(self):
        # Chờ 3 giây để quan sát kết quả trước khi đóng (tùy chọn)
        time.sleep(3)
        self.driver.quit()

    # --- 1. AUTHENTICATION ---

    def test_01_login_admin(self):
        """Kiểm tra đăng nhập với quyền Admin"""
        driver = self.driver
        driver.get(f"{self.base_url}/login")
        
        driver.find_element(By.XPATH, "//input[@placeholder='Ví dụ: gv1, hod1, sv1...']").send_keys("admin")
        driver.find_element(By.XPATH, "//input[@type='password']").send_keys("123456")
        driver.find_element(By.XPATH, "//button[@type='submit']").click()

        WebDriverWait(driver, 10).until(EC.url_contains("/dashboard"))
        self.assertIn("/dashboard", driver.current_url)
        print("PASS: Đăng nhập Admin thành công.")

    def test_02_logout(self):
        """Kiểm tra đăng xuất"""
        driver = self.driver
        # 1. Login first
        driver.get(f"{self.base_url}/login")
        driver.find_element(By.XPATH, "//input[@placeholder='Ví dụ: gv1, hod1, sv1...']").send_keys("admin")
        driver.find_element(By.XPATH, "//input[@type='password']").send_keys("123456")
        driver.find_element(By.XPATH, "//button[@type='submit']").click()
        WebDriverWait(driver, 10).until(EC.url_contains("/dashboard"))

        # 2. Click Logout button in Header
        logout_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[@title='Logout']"))
        )
        logout_btn.click()

        # 3. Verify redirected to login
        WebDriverWait(driver, 10).until(EC.url_contains("/login"))
        self.assertIn("/login", driver.current_url)
        print("PASS: Đăng xuất thành công.")

    # --- 2. SYLLABUS MANAGEMENT (GIẢNG VIÊN) ---

    def test_03_create_syllabus_draft(self):
        """Kiểm tra tạo mới đề cương (Lưu nháp)"""
        driver = self.driver
        # 1. Đăng nhập với quyền GV (gv1)
        driver.get(f"{self.base_url}/login")
        driver.find_element(By.XPATH, "//input[@placeholder='Ví dụ: gv1, hod1, sv1...']").send_keys("gv1")
        driver.find_element(By.XPATH, "//input[@type='password']").send_keys("123456")
        driver.find_element(By.XPATH, "//button[@type='submit']").click()
        WebDriverWait(driver, 10).until(EC.url_contains("/dashboard"))

        # 2. Truy cập /syllabus/create
        driver.get(f"{self.base_url}/syllabus/create")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//h1[contains(., 'Biên soạn Đề cương')]|//div[contains(., 'Biên soạn Đề cương')]")))

        # 3. Điền thông tin cơ bản
        # Tìm dropdown Subject (môn học) - sử dụng SearchableSelect component
        subject_dropdown = driver.find_element(By.XPATH, "//button[contains(., 'Chọn môn học')]")
        subject_dropdown.click()
        time.sleep(1)
        first_option = driver.find_element(By.XPATH, "//div[contains(@class, 'cursor-default')]")
        first_option.click()

        # 4. Ấn nút 'Lưu nháp'
        save_btn = driver.find_element(By.XPATH, "//button[contains(., 'Lưu Nháp')]")
        save_btn.click()

        # 5. Kiểm tra thông báo (Alert)
        WebDriverWait(driver, 10).until(EC.alert_is_present())
        alert = driver.switch_to.alert
        self.assertIn("thành công", alert.text.lower())
        alert.accept()
        
        print("PASS: Tạo mới đề cương nháp thành công.")

    def test_04_edit_syllabus_content(self):
        """Kiểm tra chỉnh sửa nội dung đề cương"""
        driver = self.driver
        # 1. Login as Lecturer
        # 2. Go to /dashboard and find a Draft syllabus
        # 3. Click 'Sửa'
        # 4. Change some content (e.g., Description)
        # 5. Click 'Lưu Nháp'
        # 6. Verify success message
        print("TODO: Thực hiện logic chỉnh sửa đề cương")
        pass

    def test_05_submit_syllabus(self):
        """Kiểm tra gửi duyệt đề cương"""
        driver = self.driver
        # 1. Login as Lecturer
        # 2. Open a Draft syllabus
        # 3. Click 'Gửi duyệt'
        # 4. Verify message and status change to 'PENDING_REVIEW'
        print("TODO: Thực hiện logic gửi duyệt đề cương")
        pass

    # --- 3. REVIEW & APPROVAL (HOD / AA) ---

    def test_06_review_approve_syllabus(self):
        """Kiểm tra quy trình phê duyệt đề cương (Trưởng bộ môn)"""
        driver = self.driver
        # 1. Login with username 'hod1' (Head of Dept)
        # 2. Go to 'Yêu cầu phê duyệt' menu
        # 3. Locate a syllabus with 'Pending Review' status
        # 4. Click 'View/Approve'
        # 5. Click 'Phê duyệt'
        # 6. Verify status changes according to workflow
        print("TODO: Thực hiện logic phê duyệt (HOD)")
        pass

    def test_07_review_reject_syllabus(self):
        """Kiểm tra quy trình từ chối đề cương (AA)"""
        driver = self.driver
        # 1. Login with username 'aa1' (Academic Affairs)
        # 2. Find a syllabus in 'Pending Approval'
        # 3. Click 'Reject' or 'Yêu cầu chỉnh sửa'
        # 4. Must provide a mandatory reason
        # 5. Verify syllabus is returned to Lecturer
        print("TODO: Thực hiện logic từ chối (AA)")
        pass

    # --- 4. ADVANCED FEATURES (AI & VISUALIZATION) ---

    def test_08_view_subject_tree(self):
        """Kiểm tra hiển thị Cây phả hệ môn học"""
        driver = self.driver
        # 1. Open any public syllabus or view details
        # 2. Switch to 'Visual Subject Tree' tab
        # 3. Verify Canvas/SVG elements are rendered
        print("TODO: Kiểm tra Subject Tree")
        pass

    def test_09_ai_summary(self):
        """Kiểm tra tính năng tóm tắt bằng AI"""
        driver = self.driver
        # 1. Open a syllabus detail page
        # 2. Click 'Tóm tắt AI' button
        # 3. Wait for AI processing background task
        # 4. Verify summary text appears in the UI
        print("TODO: Kiểm tra AI Summary")
        pass

    def test_10_version_comparison(self):
        """Kiểm tra so sánh 2 phiên bản đề cương"""
        driver = self.driver
        # 1. Open a syllabus that has history
        # 2. Select two versions from the list
        # 3. Click 'So sánh'
        # 4. Verify highlighted differences are shown
        print("TODO: Kiểm tra so sánh phiên bản")
        pass

    # --- 5. STUDENT FEATURES ---

    def test_11_student_search_syllabus(self):
        """Kiểm tra sinh viên tìm kiếm đề cương"""
        driver = self.driver
        # 1. Go to /portal (public view)
        # 2. Type subject name/code in search bar
        # 3. Verify results filter automatically
        print("TODO: Kiểm tra tìm kiếm đề cương (Sinh viên)")
        pass

    def test_12_student_report_error(self):
        """Kiểm tra sinh viên gửi báo cáo lỗi nội dung"""
        driver = self.driver
        # 1. Open syllabus as 'sv1'
        # 2. Click 'Báo lỗi' button
        # 3. Fill details and submit
        # 4. Verify lecturer/admin receives notification
        print("TODO: Kiểm tra báo lỗi (Feedback)")
        pass

if __name__ == "__main__":
    unittest.main()
