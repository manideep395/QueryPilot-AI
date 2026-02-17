"""
Integration Tests for Web API and Security Features
Tests the complete system integration and security workflows
"""

import pytest
import requests
import json
import time
import threading
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, List, Any
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from web.api import app
from fastapi.testclient import TestClient
from core.security_manager import security_manager, UserRole, Permission
from core.enhanced_orchestrator import EnhancedOrchestrator

class TestWebAPIIntegration:
    """Integration tests for Web API"""
    
    def setup_method(self):
        self.client = TestClient(app)
        self.base_url = "http://testserver"
        self.admin_token = None
        self.user_token = None
        
        # Create test users
        security_manager.create_user("testadmin", "admin@test.com", "AdminPass123!", UserRole.ADMIN)
        security_manager.create_user("testuser", "user@test.com", "UserPass123!", UserRole.ANALYST)
        
        # Get tokens
        admin_login = {"username": "testadmin", "password": "AdminPass123!"}
        user_login = {"username": "testuser", "password": "UserPass123!"}
        
        admin_response = self.client.post("/api/auth/login", json=admin_login)
        user_response = self.client.post("/api/auth/login", json=user_login)
        
        if admin_response.status_code == 200:
            self.admin_token = admin_response.json()["access_token"]
        if user_response.status_code == 200:
            self.user_token = user_response.json()["access_token"]
    
    def test_complete_workflow(self):
        """Test complete user workflow from login to query execution"""
        # 1. User login
        login_data = {"username": "testuser", "password": "UserPass123!"}
        response = self.client.post("/api/auth/login", json=login_data)
        
        assert response.status_code == 200
        token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # 2. Get user info
        response = self.client.get("/api/auth/me", headers=headers)
        assert response.status_code == 200
        user_data = response.json()
        assert user_data["username"] == "testuser"
        assert user_data["role"] == "analyst"
        
        # 3. Get system status
        response = self.client.get("/api/system/status", headers=headers)
        assert response.status_code == 200
        status = response.json()
        assert "ai_integration" in status
        assert "security" in status
        
        # 4. Execute query
        query_data = {"question": "Show me all students"}
        response = self.client.post("/api/query", json=query_data, headers=headers)
        assert response.status_code == 200
        result = response.json()
        assert "sql" in result
        assert "explanation" in result
        assert "confidence" in result
        assert "ai_enhancements" in result
        assert "performance_metrics" in result
        
        # 5. Get performance report
        response = self.client.get("/api/performance/report", headers=headers)
        assert response.status_code == 200
        report = response.json()
        assert isinstance(report, dict)
        
        print("✅ Complete workflow test passed")
    
    def test_role_based_access_control(self):
        """Test role-based access control"""
        # Test admin access
        admin_headers = {"Authorization": f"Bearer {self.admin_token}"}
        response = self.client.get("/api/security/audit", headers=admin_headers)
        assert response.status_code == 200
        
        # Test user access (should fail for admin endpoint)
        user_headers = {"Authorization": f"Bearer {self.user_token}"}
        response = self.client.get("/api/security/audit", headers=user_headers)
        assert response.status_code == 403  # Forbidden
        
        # Test user access to regular endpoints
        response = self.client.get("/api/performance/report", headers=user_headers)
        assert response.status_code == 200
        
        print("✅ Role-based access control test passed")
    
    def test_concurrent_api_requests(self):
        """Test concurrent API requests"""
        def make_request():
            headers = {"Authorization": f"Bearer {self.user_token}"}
            query_data = {"question": "Count students"}
            response = self.client.post("/api/query", json=query_data, headers=headers)
            return response.status_code == 200
        
        # Make 10 concurrent requests
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_request) for _ in range(10)]
            results = [future.result() for future in futures]
        
        # All requests should succeed
        assert all(results)
        assert sum(results) == 10
        
        print("✅ Concurrent API requests test passed")
    
    def test_error_handling(self):
        """Test API error handling"""
        headers = {"Authorization": f"Bearer {self.user_token}"}
        
        # Test invalid query
        invalid_query = {"question": "INVALID SQL INJECTION; DROP TABLE students;"}
        response = self.client.post("/api/query", json=invalid_query, headers=headers)
        assert response.status_code in [400, 403]  # Bad request or forbidden
        
        # Test invalid token
        invalid_headers = {"Authorization": "Bearer invalid_token"}
        response = self.client.get("/api/auth/me", headers=invalid_headers)
        assert response.status_code == 401
        
        # Test missing authentication
        response = self.client.get("/api/auth/me")
        assert response.status_code == 401
        
        print("✅ Error handling test passed")
    
    def test_api_response_format(self):
        """Test API response format consistency"""
        headers = {"Authorization": f"Bearer {self.user_token}"}
        
        # Test query response format
        query_data = {"question": "Show students with marks > 80"}
        response = self.client.post("/api/query", json=query_data, headers=headers)
        assert response.status_code == 200
        
        result = response.json()
        required_fields = ["sql", "result", "explanation", "confidence", "execution_time", 
                         "timestamp", "performance_metrics", "ai_enhancements", "security_info"]
        
        for field in required_fields:
            assert field in result, f"Missing field: {field}"
        
        # Test performance metrics format
        perf_metrics = result["performance_metrics"]
        perf_fields = ["query_execution_time", "rows_returned", "performance_score"]
        
        for field in perf_fields:
            assert field in perf_metrics, f"Missing performance field: {field}"
        
        # Test AI enhancements format
        ai_enhancements = result["ai_enhancements"]
        ai_fields = ["nlu_method", "semantic_score"]
        
        for field in ai_fields:
            assert field in ai_enhancements, f"Missing AI field: {field}"
        
        print("✅ API response format test passed")

class TestSecurityIntegration:
    """Integration tests for security features"""
    
    def setup_method(self):
        self.security = security_manager
        self.orchestrator = EnhancedOrchestrator()
        
        # Create test users
        self.security.create_user("secadmin", "secadmin@test.com", "SecAdmin123!", UserRole.ADMIN)
        self.security.create_user("secuser", "secuser@test.com", "SecUser123!", UserRole.VIEWER)
        
        # Get user IDs (simplified for testing)
        self.admin_id = "secadmin"
        self.user_id = "secuser"
    
    def test_authentication_workflow(self):
        """Test complete authentication workflow"""
        # 1. User registration
        success, message = self.security.create_user(
            "newuser", "newuser@test.com", "NewUser123!", UserRole.ANALYST
        )
        assert success is True
        
        # 2. User login
        token, login_message = self.security.authenticate_user("newuser", "NewUser123!")
        assert token is not None
        assert "success" in login_message.lower()
        
        # 3. Token validation
        payload = self.security.verify_jwt_token(token)
        assert payload is not None
        assert payload["username"] == "newuser"
        
        # 4. Permission check
        has_permission = self.security.check_permission(payload["user_id"], Permission.EXECUTE_QUERY)
        assert has_permission is True
        
        print("✅ Authentication workflow test passed")
    
    def test_query_security_validation(self):
        """Test query security validation"""
        dangerous_queries = [
            "SELECT * FROM students; DROP TABLE students; --",
            "SELECT * FROM students WHERE name = 'admin' OR '1'='1'",
            "SELECT * FROM students UNION SELECT * FROM users",
            "'; EXEC xp_cmdshell('dir'); --",
            "SELECT * FROM information_schema.tables --"
        ]
        
        for query in dangerous_queries:
            has_permission, message = self.security.check_query_permission(
                self.user_id, query, "default"
            )
            assert has_permission is False
            assert "blocked" in message.lower() or "invalid" in message.lower()
        
        print("✅ Query security validation test passed")
    
    def test_account_lockout_mechanism(self):
        """Test account lockout after failed attempts"""
        username = "lockoutuser"
        self.security.create_user(username, "lockout@test.com", "Lockout123!", UserRole.VIEWER)
        
        # Make multiple failed login attempts
        for i in range(6):  # More than max failed attempts
            token, message = self.security.authenticate_user(username, "wrongpassword")
            assert token is None
        
        # Check if account is locked
        user = self.security.get_user_by_username(username)
        assert user.locked_until is not None
        
        # Try login with correct password (should still fail)
        token, message = self.security.authenticate_user(username, "Lockout123!")
        assert token is None
        assert "locked" in message.lower()
        
        print("✅ Account lockout mechanism test passed")
    
    def test_audit_trail_completeness(self):
        """Test audit trail completeness"""
        initial_count = len(self.security.audit_logs)
        
        # Perform various actions
        self.security._log_audit(self.admin_id, "test_action_1", "test_resource", "127.0.0.1", "test_agent", True)
        self.security._log_audit(self.user_id, "test_action_2", "test_resource", "127.0.0.1", "test_agent", False)
        
        # Check audit logs
        final_count = len(self.security.audit_logs)
        assert final_count == initial_count + 2
        
        # Check log details
        recent_logs = self.security.audit_logs[-2:]
        assert recent_logs[0].action == "test_action_1"
        assert recent_logs[0].success is True
        assert recent_logs[1].action == "test_action_2"
        assert recent_logs[1].success is False
        
        print("✅ Audit trail completeness test passed")
    
    def test_permission_hierarchy(self):
        """Test role-based permission hierarchy"""
        # Admin should have all permissions
        admin_user = self.security.get_user_by_username("secadmin")
        admin_permissions = admin_user.permissions
        
        for permission in Permission:
            assert permission in admin_permissions
        
        # Viewer should have limited permissions
        viewer_user = self.security.get_user_by_username("secuser")
        viewer_permissions = viewer_user.permissions
        
        assert Permission.READ_DATA in viewer_permissions
        assert Permission.VIEW_SCHEMA in viewer_permissions
        assert Permission.MANAGE_USERS not in viewer_permissions
        assert Permission.DELETE_DATA not in viewer_permissions
        
        print("✅ Permission hierarchy test passed")

class TestEndToEndIntegration:
    """End-to-end integration tests"""
    
    def setup_method(self):
        self.orchestrator = EnhancedOrchestrator()
        self.security = security_manager
        
        # Create test user
        self.security.create_user("e2euser", "e2e@test.com", "E2EUser123!", UserRole.ANALYST)
        token, _ = self.security.authenticate_user("e2euser", "E2EUser123!")
        self.user_id = "e2euser"
    
    def test_complex_query_processing_pipeline(self):
        """Test complex query through entire processing pipeline"""
        complex_query = "What is the average GPA of students in Computer Science department with scholarships above $5000?"
        
        # Process query
        result = self.orchestrator.handle_query(complex_query, user_id=self.user_id)
        
        # Verify all pipeline components worked
        assert result["confidence"] > 0
        assert result["sql"] is not None
        assert "AVG" in result["sql"].upper()
        assert "execution_time" in result
        
        # Check AI enhancements
        ai_info = result["ai_enhancements"]
        assert "nlu_method" in ai_info
        assert "comparative_intent" in ai_info
        
        # Check performance metrics
        perf_info = result["performance_metrics"]
        assert "performance_score" in perf_info
        assert "query_execution_time" in perf_info
        
        # Check security info
        sec_info = result["security_info"]
        assert sec_info["user_authenticated"] is True
        assert sec_info["permissions_checked"] is True
        
        print("✅ Complex query processing pipeline test passed")
    
    def test_multi_feature_coordination(self):
        """Test coordination between multiple features"""
        queries = [
            "Show me students enrolled last month",
            "Find courses with enrollment rate above 80%",
            "Count instructors by department with salary above average"
        ]
        
        for query in queries:
            result = self.orchestrator.handle_query(query, user_id=self.user_id)
            
            # Verify temporal understanding
            if "last month" in query.lower():
                temporal_info = result["ai_enhancements"].get("temporal_intent", {})
                assert temporal_info.get("time_range") == "last_month"
            
            # Verify comparative reasoning
            if "above" in query.lower():
                comparative_info = result["ai_enhancements"].get("comparative_intent", {})
                assert comparative_info.get("comparison") in ["greater_than", "above"]
            
            # Verify performance monitoring
            assert result["performance_metrics"]["performance_score"] > 0
            
            # Verify security validation
            assert result["security_info"]["permissions_checked"] is True
        
        print("✅ Multi-feature coordination test passed")
    
    def test_error_recovery_and_fallback(self):
        """Test error recovery and fallback mechanisms"""
        # Test with potentially problematic query
        problematic_query = "Show me data from non_existent_table"
        
        result = self.orchestrator.handle_query(problematic_query, user_id=self.user_id)
        
        # Should handle error gracefully
        assert result["confidence"] == 0.0 or result.get("error") is not None
        assert "explanation" in result
        
        # Test with malformed query
        malformed_query = "Show me students with marks > abc"
        
        result = self.orchestrator.handle_query(malformed_query, user_id=self.user_id)
        
        # Should provide meaningful error message
        assert result["confidence"] < 0.5
        assert "explanation" in result
        
        print("✅ Error recovery and fallback test passed")
    
    def test_system_resilience(self):
        """Test system resilience under stress"""
        def process_query(query_text):
            try:
                result = self.orchestrator.handle_query(query_text, user_id=self.user_id)
                return result is not None and "error" not in result
            except Exception:
                return False
        
        # Process multiple queries concurrently
        queries = [f"Show students {i}" for i in range(20)]
        
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(process_query, q) for q in queries]
            results = [future.result() for future in futures]
        
        # Most queries should succeed
        success_rate = sum(results) / len(results)
        assert success_rate > 0.8  # At least 80% success rate
        
        print(f"✅ System resilience test passed ({success_rate:.1%} success rate)")

class TestSecurityScenarios:
    """Test specific security scenarios"""
    
    def setup_method(self):
        self.security = security_manager
        self.orchestrator = EnhancedOrchestrator()
        
        # Create test users with different roles
        self.security.create_user("victim", "victim@test.com", "Victim123!", UserRole.VIEWER)
        self.security.create_user("attacker", "attacker@test.com", "Attack123!", UserRole.ANALYST)
    
    def test_sql_injection_attempts(self):
        """Test various SQL injection attempts"""
        injection_attempts = [
            "'; DROP TABLE students; --",
            "' OR '1'='1",
            "UNION SELECT * FROM users --",
            "'; EXEC xp_cmdshell('dir'); --",
            "1' AND (SELECT COUNT(*) FROM users) > 0 --",
            "'; INSERT INTO users VALUES('hacker', 'password'); --",
            "' OR 1=1 #",
            "'; SHUTDOWN; --",
            "' UNION SELECT @@version --",
            "'; ALTER TABLE students DROP COLUMN marks; --"
        ]
        
        for injection in injection_attempts:
            # Test through security manager
            has_permission, message = self.security.check_query_permission(
                "attacker", f"SELECT * FROM students WHERE name = '{injection}'", "default"
            )
            assert has_permission is False
            
            # Test through orchestrator
            result = self.orchestrator.handle_query(
                f"Show students with name {injection}", user_id="attacker"
            )
            assert result.get("confidence", 1.0) == 0.0 or result.get("error") is not None
        
        print("✅ SQL injection attempts test passed")
    
    def test_privilege_escalation_attempts(self):
        """Test privilege escalation attempts"""
        # Test viewer trying to access admin functions
        has_permission = self.security.check_permission("victim", Permission.MANAGE_USERS)
        assert has_permission is False
        
        # Test analyst trying to delete data
        has_permission = self.security.check_permission("attacker", Permission.DELETE_DATA)
        assert has_permission is False
        
        # Test through orchestrator
        result = self.orchestrator.handle_query("DELETE FROM students WHERE id = 1", user_id="victim")
        assert result.get("error") == "security_blocked" or result["confidence"] == 0.0
        
        print("✅ Privilege escalation attempts test passed")
    
    def test_session_management_security(self):
        """Test session management security"""
        # Get valid token
        token, _ = self.security.authenticate_user("attacker", "Attack123!")
        
        # Test token validation
        payload = self.security.verify_jwt_token(token)
        assert payload is not None
        
        # Test invalid token
        invalid_payload = self.security.verify_jwt_token("invalid_token")
        assert invalid_payload is None
        
        # Test expired token (simulate by checking token structure)
        assert "exp" in payload
        assert "user_id" in payload
        assert "username" in payload
        
        print("✅ Session management security test passed")

def run_integration_tests():
    """Run all integration tests"""
    print("🚀 Running Integration Tests")
    print("=" * 60)
    
    test_classes = [
        TestWebAPIIntegration,
        TestSecurityIntegration,
        TestEndToEndIntegration,
        TestSecurityScenarios
    ]
    
    total_tests = 0
    passed_tests = 0
    
    for test_class in test_classes:
        print(f"\n📋 Running {test_class.__name__}")
        
        # Get all test methods
        test_methods = [method for method in dir(test_class) if method.startswith('test_')]
        
        for test_method in test_methods:
            total_tests += 1
            try:
                # Create test instance
                test_instance = test_class()
                
                # Run setup if available
                if hasattr(test_instance, 'setup_method'):
                    test_instance.setup_method()
                
                # Run test
                getattr(test_instance, test_method)()
                passed_tests += 1
                print(f"  ✅ {test_method}")
                
            except Exception as e:
                print(f"  ❌ {test_method}: {e}")
    
    print(f"\n📊 Integration Test Results:")
    print(f"  Total Tests: {total_tests}")
    print(f"  Passed: {passed_tests}")
    print(f"  Failed: {total_tests - passed_tests}")
    print(f"  Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    
    return passed_tests, total_tests

if __name__ == "__main__":
    run_integration_tests()
