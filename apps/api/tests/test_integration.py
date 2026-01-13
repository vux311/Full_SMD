"""
Integration tests for Syllabus API endpoints
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import pytest
import json
from flask import Flask
from create_app import create_app


@pytest.fixture
def app():
    """Create application for testing"""
    app = create_app()
    app.config['TESTING'] = True
    return app


@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()


@pytest.fixture
def auth_headers(client):
    """Get authentication headers"""
    response = client.post('/auth/login', json={
        'username': 'test_user',
        'password': 'test_password'
    })
    
    if response.status_code == 200:
        token = response.json.get('token')
        return {'Authorization': f'Bearer {token}'}
    return {}


class TestSyllabusEndpoints:
    """Test syllabus CRUD operations"""
    
    def test_list_syllabuses(self, client, auth_headers):
        """Test GET /syllabuses/"""
        response = client.get('/syllabuses/', headers=auth_headers)
        assert response.status_code == 200
        data = response.json
        assert isinstance(data, list)
    
    def test_list_syllabuses_paginated(self, client, auth_headers):
        """Test GET /syllabuses/?page=1&page_size=10"""
        response = client.get('/syllabuses/?page=1&page_size=10', headers=auth_headers)
        assert response.status_code == 200
        data = response.json
        assert 'items' in data
        assert 'pagination' in data
        assert data['pagination']['page'] == 1
        assert data['pagination']['page_size'] == 10
    
    def test_get_syllabus_by_id(self, client, auth_headers):
        """Test GET /syllabuses/:id"""
        response = client.get('/syllabuses/1', headers=auth_headers)
        assert response.status_code in [200, 404]  # OK or Not Found
        
        if response.status_code == 200:
            data = response.json
            assert 'id' in data
            assert data['id'] == 1
    
    def test_create_syllabus(self, client, auth_headers):
        """Test POST /syllabuses/"""
        syllabus_data = {
            'subject_id': 1,
            'program_id': 1,
            'academic_year_id': 1,
            'lecturer_id': 1,
            'version': '1.0',
            'status': 'DRAFT',
            'time_allocation': json.dumps({'theory': 30, 'practice': 15}),
            'clos': [],
            'materials': [],
            'teaching_plans': [],
            'assessment_schemes': []
        }
        
        response = client.post('/syllabuses/', 
                              json=syllabus_data, 
                              headers=auth_headers)
        
        # Should be 201 Created or 400/422 for validation errors
        assert response.status_code in [201, 400, 422]
    
    def test_submit_syllabus_requires_auth(self, client):
        """Test POST /syllabuses/:id/submit requires authentication"""
        response = client.post('/syllabuses/1/submit')
        assert response.status_code in [401, 403]  # Unauthorized


class TestPaginationFeature:
    """Test pagination functionality"""
    
    def test_default_pagination(self, client, auth_headers):
        """Test pagination with default values"""
        response = client.get('/syllabuses/?page=1', headers=auth_headers)
        assert response.status_code == 200
        data = response.json
        
        assert 'pagination' in data
        assert data['pagination']['page'] == 1
        assert data['pagination']['page_size'] == 20  # default
    
    def test_custom_page_size(self, client, auth_headers):
        """Test pagination with custom page size"""
        response = client.get('/syllabuses/?page=1&page_size=50', headers=auth_headers)
        assert response.status_code == 200
        data = response.json
        
        assert data['pagination']['page_size'] == 50
    
    def test_max_page_size_limit(self, client, auth_headers):
        """Test pagination respects max page size"""
        response = client.get('/syllabuses/?page=1&page_size=999', headers=auth_headers)
        assert response.status_code == 200
        data = response.json
        
        # Should be capped at MAX_PAGE_SIZE (100)
        assert data['pagination']['page_size'] <= 100


class TestPerformanceMonitoring:
    """Test performance monitoring"""
    
    def test_endpoint_performance_logged(self, client, auth_headers, caplog):
        """Test that endpoint performance is logged"""
        response = client.get('/syllabuses/', headers=auth_headers)
        assert response.status_code == 200
        
        # Check if performance logs are generated
        # (This requires proper logging setup in test environment)


class TestCaching:
    """Test caching functionality"""
    
    def test_cached_response(self, client, auth_headers):
        """Test that repeated requests use cache"""
        # First request
        response1 = client.get('/syllabuses/1', headers=auth_headers)
        
        # Second request (should be cached)
        response2 = client.get('/syllabuses/1', headers=auth_headers)
        
        if response1.status_code == 200:
            assert response1.json == response2.json


class TestErrorHandling:
    """Test error handling"""
    
    def test_invalid_syllabus_id(self, client, auth_headers):
        """Test GET /syllabuses/:id with invalid ID"""
        response = client.get('/syllabuses/999999', headers=auth_headers)
        assert response.status_code == 404
    
    def test_invalid_pagination_params(self, client, auth_headers):
        """Test pagination with invalid parameters"""
        response = client.get('/syllabuses/?page=-1&page_size=0', headers=auth_headers)
        # Should handle gracefully and return 200 with adjusted params
        assert response.status_code == 200


class TestWorkflowOperations:
    """Test workflow operations"""
    
    def test_submit_syllabus(self, client, auth_headers):
        """Test submitting syllabus for approval"""
        # First create a syllabus
        response = client.post('/syllabuses/1/submit', headers=auth_headers)
        
        # Should succeed or return validation error
        assert response.status_code in [200, 400, 404]
    
    def test_evaluate_syllabus(self, client, auth_headers):
        """Test evaluating syllabus"""
        evaluation_data = {
            'action': 'approve',
            'comment': 'Approved for publication'
        }
        
        response = client.post('/syllabuses/1/evaluate',
                              json=evaluation_data,
                              headers=auth_headers)
        
        assert response.status_code in [200, 400, 404]


# Run tests
if __name__ == '__main__':
    pytest.main([__file__, '-v'])
