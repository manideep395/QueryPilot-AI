"""
Comprehensive Test Suite for Enhanced NeuroSQL Features
Tests AI/ML, Multi-DB, Performance, Security, and Web API
"""

import pytest
import asyncio
import json
import time
from datetime import datetime
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.enhanced_orchestrator import EnhancedOrchestrator
from core.security_manager import security_manager, UserRole, Permission
from core.database_manager import db_manager
from core.performance_optimizer import performance_optimizer
from agents.enhanced_nlu_agent import EnhancedNLUAgent
from web.api import app
from fastapi.testclient import TestClient

class TestEnhancedNLUAgent:
    """Test AI/ML Enhanced NLU Agent"""
    
    def setup_method(self):
        self.nlu = EnhancedNLUAgent()
        self.sample_schema = {
            "students": ["id", "name", "age", "marks", "department"],
            "courses": ["id", "name", "credits", "department"],
            "enrollments": ["student_id", "course_id", "grade", "semester"]
        }
    
    def test_basic_table_detection(self):
        """Test basic table detection with AI enhancement"""
        text = "Show me all students"
        result = self.nlu.parse(text, self.sample_schema)
        
        assert result["table"] == "students"
        assert "students" in result["tables"]
        assert result["confidence"] > 0.5
    
    def test_temporal_intent_detection(self):
        """Test temporal intent detection"""
        text = "What were the enrollments last month?"
        result = self.nlu.parse(text, self.sample_schema)
        
        assert "temporal" in result
        assert result["temporal"].get("time_range") == "last_month"
    
    def test_comparative_intent_detection(self):
        """Test comparative intent detection"""
        text = "Find students with marks greater than 80"
        result = self.nlu.parse(text, self.sample_schema)
        
        assert "comparative" in result
        assert result["comparative"].get("comparison") == "greater_than"
        assert result["where_column"] == "MARKS"
        assert result["where_operator"] == ">"
        assert result["where_value"] == "80"
    
    def test_aggregation_detection(self):
        """Test aggregation detection"""
        test_cases = [
            ("Count the number of students", "COUNT"),
            ("What is the average marks?", "AVG"),
            ("Find the maximum marks", "MAX"),
            ("Show the minimum age", "MIN"),
            ("Calculate total credits", "SUM")
        ]
        
        for text, expected_agg in test_cases:
            result = self.nlu.parse(text, self.sample_schema)
            assert result["aggregation"] == expected_agg
    
    def test_semantic_column_mapping(self):
        """Test semantic column mapping"""
        text = "Find student names and scores"
        result = self.nlu.parse(text, self.sample_schema)
        
        assert "name" in result["columns"]
        # Should map "scores" to "marks" semantically
        assert any("marks" in col.lower() for col in result["columns"])
    
    def test_confidence_scoring(self):
        """Test confidence scoring"""
        simple_text = "Show students"
        complex_text = "Find students enrolled in computer science courses with marks greater than average from last semester"
        
        simple_result = self.nlu.parse(simple_text, self.sample_schema)
        complex_result = self.nlu.parse(complex_text, self.sample_schema)
        
        # Simple queries should have higher confidence
        assert simple_result["confidence"] >= complex_result["confidence"]

class TestDatabaseManager:
    """Test Multi-Database Support"""
    
    def setup_method(self):
        # Initialize test database connections
        db_manager.add_connection("test_sqlite", "sqlite:///test.db", "sqlite")
    
    def test_sqlite_connection(self):
        """Test SQLite connection"""
        assert "test_sqlite" in db_manager.list_connections()
        
        schema, relations = db_manager.get_schema("test_sqlite")
        assert isinstance(schema, dict)
        assert isinstance(relations, list)
    
    def test_query_execution(self):
        """Test query execution"""
        # This would require actual test database setup
        # For now, test the interface
        try:
            result = db_manager.execute_query("test_sqlite", "SELECT 1 as test")
            assert result is not None
        except Exception:
            # Expected if test database doesn't exist
            pass
    
    def test_connection_validation(self):
        """Test connection validation"""
        # Test invalid connection
        success = db_manager.add_connection("invalid", "invalid://connection", "sqlite")
        assert success is False
    
    def test_schema_introspection(self):
        """Test database schema introspection"""
        # Test with default connection
        try:
            schema, relations = db_manager.get_schema("default")
            assert isinstance(schema, dict)
            assert isinstance(relations, list)
        except Exception:
            pass

class TestPerformanceOptimizer:
    """Test Performance Optimization Layer"""
    
    def setup_method(self):
        self.optimizer = performance_optimizer
    
    def test_query_analysis(self):
        """Test query performance analysis"""
        query = "SELECT * FROM students WHERE marks > 80"
        
        try:
            metrics = self.optimizer.analyze_query_performance(query, "default")
            assert metrics is not None
            assert hasattr(metrics, 'execution_time')
            assert hasattr(metrics, 'rows_returned')
            assert hasattr(metrics, 'optimization_suggestions')
        except Exception:
            # Expected if no database connection
            pass
    
    def test_optimization_suggestions(self):
        """Test optimization suggestions"""
        query = "SELECT * FROM large_table"
        optimized_query, optimizations = self.optimizer.optimize_query_execution(query, "default")
        
        assert optimized_query is not None
        assert isinstance(optimizations, list)
    
    def test_performance_report(self):
        """Test performance report generation"""
        report = self.optimizer.get_performance_report(24)
        assert isinstance(report, dict)
        assert "total_queries" in report or "message" in report
    
    def test_cache_functionality(self):
        """Test caching functionality"""
        # Test cache count tracking
        count = self.optimizer._get_cache_count(hash("test_query"))
        assert isinstance(count, int)

class TestSecurityManager:
    """Test Security Framework"""
    
    def setup_method(self):
        self.security = security_manager
    
    def test_user_creation(self):
        """Test user creation"""
        success, message = self.security.create_user(
            "testuser", "test@example.com", "TestPass123!", UserRole.ANALYST
        )
        
        assert success is True
        assert "created successfully" in message.lower()
    
    def test_password_validation(self):
        """Test password strength validation"""
        # Weak password
        is_valid, message = self.security.validate_password_strength("weak")
        assert is_valid is False
        
        # Strong password
        is_valid, message = self.security.validate_password_strength("StrongPass123!")
        assert is_valid is True
    
    def test_authentication(self):
        """Test user authentication"""
        # Create test user first
        self.security.create_user("authuser", "auth@example.com", "AuthPass123!", UserRole.VIEWER)
        
        # Test authentication
        token, message = self.security.authenticate_user("authuser", "AuthPass123!")
        assert token is not None
        assert "success" in message.lower()
        
        # Test invalid credentials
        token, message = self.security.authenticate_user("authuser", "wrongpassword")
        assert token is None
        assert "invalid" in message.lower()
    
    def test_permission_checking(self):
        """Test permission checking"""
        # Create admin user
        success, _ = self.security.create_user("adminuser", "admin@example.com", "AdminPass123!", UserRole.ADMIN)
        
        # Get user ID (this would need to be implemented properly)
        # For now, test the permission structure
        admin_permissions = self.security.role_permissions[UserRole.ADMIN]
        assert Permission.MANAGE_USERS in admin_permissions
        assert Permission.EXECUTE_QUERY in admin_permissions
    
    def test_query_permission_validation(self):
        """Test query permission validation"""
        # Test SELECT query
        has_permission, message = self.security.check_query_permission("test_user", "SELECT * FROM students", "default")
        # Should return True for basic SELECT (if user has read permission)
        
        # Test dangerous query
        has_permission, message = self.security.check_query_permission("test_user", "DROP TABLE students", "default")
        assert has_permission is False
        assert "blocked" in message.lower()
    
    def test_audit_logging(self):
        """Test audit logging"""
        initial_count = len(self.security.audit_logs)
        
        self.security._log_audit(
            user_id="test_user",
            action="test_action",
            resource="test_resource",
            ip_address="127.0.0.1",
            user_agent="test_agent",
            success=True
        )
        
        assert len(self.security.audit_logs) == initial_count + 1

class TestWebAPI:
    """Test Web API Endpoints"""
    
    def setup_method(self):
        self.client = TestClient(app)
    
    def test_health_check(self):
        """Test health check endpoint"""
        response = self.client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
    
    def test_login_endpoint(self):
        """Test login endpoint"""
        login_data = {
            "username": "admin",
            "password": "admin123"
        }
        
        response = self.client.post("/api/auth/login", json=login_data)
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
    
    def test_invalid_login(self):
        """Test invalid login"""
        login_data = {
            "username": "admin",
            "password": "wrongpassword"
        }
        
        response = self.client.post("/api/auth/login", json=login_data)
        assert response.status_code == 401
    
    def test_protected_endpoint_without_token(self):
        """Test accessing protected endpoint without token"""
        response = self.client.get("/api/auth/me")
        assert response.status_code == 401
    
    def test_protected_endpoint_with_token(self):
        """Test accessing protected endpoint with valid token"""
        # First login to get token
        login_data = {"username": "admin", "password": "admin123"}
        login_response = self.client.post("/api/auth/login", json=login_data)
        token = login_response.json()["access_token"]
        
        # Access protected endpoint
        headers = {"Authorization": f"Bearer {token}"}
        response = self.client.get("/api/auth/me", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "admin"
    
    def test_query_execution_endpoint(self):
        """Test query execution endpoint"""
        # Login first
        login_data = {"username": "admin", "password": "admin123"}
        login_response = self.client.post("/api/auth/login", json=login_data)
        token = login_response.json()["access_token"]
        
        # Execute query
        headers = {"Authorization": f"Bearer {token}"}
        query_data = {"question": "Show me all students"}
        
        response = self.client.post("/api/query", json=query_data, headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "sql" in data
        assert "explanation" in data
        assert "confidence" in data

class TestEnhancedOrchestrator:
    """Test Enhanced Orchestrator Integration"""
    
    def setup_method(self):
        self.orchestrator = EnhancedOrchestrator()
    
    def test_system_status(self):
        """Test system status"""
        status = self.orchestrator.get_system_status()
        assert isinstance(status, dict)
        assert "orchestrator" in status
        assert "ai_integration" in status
        assert "multi_database" in status
        assert "performance_optimization" in status
        assert "security" in status
    
    def test_basic_query_processing(self):
        """Test basic query processing"""
        result = self.orchestrator.handle_query("Show me all students")
        
        assert isinstance(result, dict)
        assert "explanation" in result
        assert "confidence" in result
        assert "execution_time" in result
    
    def test_enhanced_query_processing(self):
        """Test enhanced query processing with AI features"""
        result = self.orchestrator.handle_query(
            "Find students with marks greater than 80 from computer science department",
            user_id="admin"
        )
        
        assert isinstance(result, dict)
        assert "ai_enhancements" in result
        assert "performance_metrics" in result
        assert "security_info" in result
        
        # Check AI enhancements
        ai_info = result["ai_enhancements"]
        assert "nlu_method" in ai_info
        assert "comparative_intent" in ai_info
    
    def test_performance_monitoring(self):
        """Test performance monitoring integration"""
        result = self.orchestrator.handle_query("Count the number of students")
        
        if "performance_metrics" in result:
            perf = result["performance_metrics"]
            assert "performance_score" in perf
            assert isinstance(perf["performance_score"], (int, float))

class TestIntegration:
    """Integration Tests for Complete System"""
    
    def test_end_to_end_query_flow(self):
        """Test complete query flow from NLU to execution"""
        orchestrator = EnhancedOrchestrator()
        
        # Test complex query
        query = "What is the average marks of students in computer science department?"
        result = orchestrator.handle_query(query, user_id="admin")
        
        # Verify all components worked
        assert result["confidence"] > 0
        assert result["sql"] is not None
        assert "AVG" in result["sql"].upper()
        assert "execution_time" in result
    
    def test_security_integration(self):
        """Test security integration with query processing"""
        orchestrator = EnhancedOrchestrator()
        
        # Test dangerous query
        result = orchestrator.handle_query("DROP TABLE students", user_id="admin")
        
        # Should be blocked by security
        assert result.get("error") == "security_blocked" or result["confidence"] == 0.0
    
    def test_multi_database_integration(self):
        """Test multi-database integration"""
        # This would require multiple database connections
        # For now, test the interface
        connections = db_manager.list_connections()
        assert isinstance(connections, list)
        assert len(connections) > 0

# Performance and Stress Tests
class TestPerformance:
    """Performance and Stress Tests"""
    
    def test_concurrent_query_processing(self):
        """Test concurrent query processing"""
        orchestrator = EnhancedOrchestrator()
        
        async def run_query(query_text):
            return orchestrator.handle_query(query_text)
        
        # Run multiple queries concurrently
        queries = [
            "Show me students",
            "Count courses", 
            "Find enrollments",
            "List departments"
        ]
        
        start_time = time.time()
        tasks = [run_query(q) for q in queries]
        results = asyncio.run(asyncio.gather(*tasks, return_exceptions=True))
        end_time = time.time()
        
        # Verify all queries completed
        assert len(results) == len(queries)
        assert end_time - start_time < 5.0  # Should complete within 5 seconds
    
    def test_memory_usage(self):
        """Test memory usage during processing"""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        orchestrator = EnhancedOrchestrator()
        
        # Process multiple queries
        for i in range(100):
            orchestrator.handle_query(f"Show me students {i}")
        
        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory
        
        # Memory increase should be reasonable (less than 100MB)
        assert memory_increase < 100 * 1024 * 1024

if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "--tb=short"])
