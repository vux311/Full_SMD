import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

class SMDLoginTest(unittest.TestCase):
    def setUp(self):
        self.driver = webdriver.Chrome()
        self.driver.implicitly_wait(10)
        self.base_url = "http://localhost:3000"

    def test_login_admin(self):
        driver = self.driver
        driver.get(f"{self.base_url}/login")
        
        self.assertIn("Đăng nhập Hệ thống", driver.page_source)
        
        user_name_field = driver.find_element(By.XPATH, "//input[@placeholder='Ví dụ: gv1, hod1, sv1...']")
        user_name_field.clear()
        user_name_field.send_keys("admin")
        
        password_field = driver.find_element(By.XPATH, "//input[@type='password']")
        password_field.clear()
        password_field.send_keys("123456")
        
        login_button = driver.find_element(By.XPATH, "//button[@type='submit']")
        login_button.click()

        WebDriverWait(driver, 10).until(
            EC.url_contains("/dashboard")
        )
        
        self.assertIn("/dashboard", driver.current_url)
        print("Đăng nhập thành công và đã chuyển hướng đến Dashboard.")

    def tearDown(self):
        time.sleep(5)
        self.driver.quit()

if __name__ == "__main__":
    unittest.main()
