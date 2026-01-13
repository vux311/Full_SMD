"""
Load testing script using Locust
Install: pip install locust
Run: locust -f load_test.py --host=http://localhost:5000
"""
from locust import HttpUser, task, between
import random
import json


class SyllabusManagementUser(HttpUser):
    """
    Simulates user behavior for Syllabus Management System
    """
    wait_time = between(1, 3)  # Wait 1-3 seconds between tasks
    
    def on_start(self):
        """Called when a user starts - perform login"""
        # Login to get token
        response = self.client.post("/auth/login", json={
            "username": "test_user",
            "password": "test_password"
        })
        
        if response.status_code == 200:
            data = response.json()
            self.token = data.get('token')
            self.headers = {"Authorization": f"Bearer {self.token}"}
        else:
            self.token = None
            self.headers = {}
    
    @task(3)
    def list_syllabuses(self):
        """List syllabuses - most common operation (weight=3)"""
        page = random.randint(1, 5)
        self.client.get(
            f"/syllabuses/?page={page}&page_size=20",
            headers=self.headers,
            name="/syllabuses/ (paginated)"
        )
    
    @task(2)
    def get_syllabus_detail(self):
        """Get syllabus details (weight=2)"""
        syllabus_id = random.randint(1, 100)
        self.client.get(
            f"/syllabuses/{syllabus_id}",
            headers=self.headers,
            name="/syllabuses/:id"
        )
    
    @task(1)
    def list_subjects(self):
        """List subjects (weight=1)"""
        self.client.get(
            "/subjects/",
            headers=self.headers,
            name="/subjects/"
        )
    
    @task(1)
    def list_programs(self):
        """List programs (weight=1)"""
        self.client.get(
            "/programs/",
            headers=self.headers,
            name="/programs/"
        )
    
    @task(1)
    def get_system_settings(self):
        """Get system settings (weight=1)"""
        self.client.get(
            "/system-settings/",
            headers=self.headers,
            name="/system-settings/"
        )
    
    @task(1)
    def search_syllabuses(self):
        """Search syllabuses by subject (weight=1)"""
        subject_id = random.randint(1, 20)
        self.client.get(
            f"/syllabuses/?subject_id={subject_id}",
            headers=self.headers,
            name="/syllabuses/ (search)"
        )


class AdminUser(HttpUser):
    """
    Simulates admin user behavior with write operations
    """
    wait_time = between(2, 5)
    
    def on_start(self):
        """Login as admin"""
        response = self.client.post("/auth/login", json={
            "username": "admin",
            "password": "admin_password"
        })
        
        if response.status_code == 200:
            data = response.json()
            self.token = data.get('token')
            self.headers = {"Authorization": f"Bearer {self.token}"}
        else:
            self.token = None
            self.headers = {}
    
    @task(2)
    def list_syllabuses(self):
        """Admin lists syllabuses"""
        self.client.get(
            "/syllabuses/?page=1&page_size=50",
            headers=self.headers,
            name="[Admin] /syllabuses/"
        )
    
    @task(1)
    def create_syllabus(self):
        """Admin creates syllabus"""
        syllabus_data = {
            "subject_id": random.randint(1, 20),
            "program_id": random.randint(1, 10),
            "academic_year_id": random.randint(1, 5),
            "lecturer_id": random.randint(1, 50),
            "version": "1.0",
            "status": "DRAFT",
            "time_allocation": json.dumps({
                "theory": 30,
                "practice": 15
            }),
            "clos": [],
            "materials": [],
            "teaching_plans": [],
            "assessment_schemes": []
        }
        
        self.client.post(
            "/syllabuses/",
            json=syllabus_data,
            headers=self.headers,
            name="[Admin] /syllabuses/ (create)"
        )
    
    @task(1)
    def submit_syllabus(self):
        """Admin submits syllabus for approval"""
        syllabus_id = random.randint(1, 100)
        self.client.post(
            f"/syllabuses/{syllabus_id}/submit",
            headers=self.headers,
            name="[Admin] /syllabuses/:id/submit"
        )


# Test scenarios
class QuickLoadTest(HttpUser):
    """Quick load test with mixed operations"""
    tasks = [SyllabusManagementUser]
    weight = 80  # 80% regular users


class HeavyLoadTest(HttpUser):
    """Heavy load test including admin operations"""
    tasks = [SyllabusManagementUser, AdminUser]
    weight = 20  # 20% admin users
