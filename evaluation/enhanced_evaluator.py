"""
Enhanced Evaluation Suite for NeuroSQL v2.0
Tests AI/ML capabilities, performance, security, and multi-database features
"""

import sys
import os
import time
import json
import statistics
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple
import matplotlib.pyplot as plt
import pandas as pd

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.enhanced_orchestrator import EnhancedOrchestrator
from core.security_manager import security_manager, UserRole
from core.performance_optimizer import performance_optimizer
from core.database_manager import db_manager

class EnhancedEvaluator:
    """Comprehensive evaluation system for enhanced NeuroSQL"""
    
    def __init__(self):
        self.orchestrator = EnhancedOrchestrator()
        self.results = {
            "ai_ml_tests": {},
            "performance_tests": {},
            "security_tests": {},
            "multi_db_tests": {},
            "integration_tests": {}
        }
        
    def run_comprehensive_evaluation(self):
        """Run all evaluation tests"""
        print("🚀 Starting Enhanced NeuroSQL Evaluation Suite")
        print("=" * 60)
        
        # AI/ML Evaluation
        print("\n🤖 Evaluating AI/ML Capabilities...")
        self.results["ai_ml_tests"] = self.evaluate_ai_ml_capabilities()
        
        # Performance Evaluation
        print("\n⚡ Evaluating Performance Optimization...")
        self.results["performance_tests"] = self.evaluate_performance_features()
        
        # Security Evaluation
        print("\n🔐 Evaluating Security Framework...")
        self.results["security_tests"] = self.evaluate_security_features()
        
        # Multi-Database Evaluation
        print("\n🗄️ Evaluating Multi-Database Support...")
        self.results["multi_db_tests"] = self.evaluate_multi_database_features()
        
        # Integration Evaluation
        print("\n🔗 Evaluating System Integration...")
        self.results["integration_tests"] = self.evaluate_integration_features()
        
        # Generate comprehensive report
        self.generate_evaluation_report()
        
        return self.results
    
    def evaluate_ai_ml_capabilities(self) -> Dict:
        """Evaluate AI/ML enhanced features"""
        ai_results = {
            "nlu_accuracy": 0,
            "temporal_understanding": 0,
            "comparative_reasoning": 0,
            "semantic_mapping": 0,
            "confidence_scoring": 0,
            "fallback_mechanism": 0
        }
        
        # Test cases for AI/ML features
        test_cases = [
            # Basic queries
            {"question": "Show me all students", "expected_table": "students", "type": "basic"},
            {"question": "List all courses", "expected_table": "courses", "type": "basic"},
            
            # Aggregation queries
            {"question": "Count the number of students", "expected_agg": "COUNT", "type": "aggregation"},
            {"question": "What is the average marks?", "expected_agg": "AVG", "type": "aggregation"},
            {"question": "Find the maximum marks", "expected_agg": "MAX", "type": "aggregation"},
            
            # Temporal queries
            {"question": "Show enrollments from last month", "temporal": "last_month", "type": "temporal"},
            {"question": "Students enrolled this year", "temporal": "this_year", "type": "temporal"},
            
            # Comparative queries
            {"question": "Students with marks greater than 80", "comparison": "greater_than", "type": "comparative"},
            {"question": "Find courses with credits between 3 and 4", "comparison": "between", "type": "comparative"},
            
            # Complex queries
            {"question": "Count students in computer science department with marks above average", 
             "complexity": "high", "type": "complex"},
            {"question": "Show top 5 performing students by department", 
             "complexity": "high", "type": "complex"}
        ]
        
        correct_predictions = 0
        total_tests = len(test_cases)
        
        for test_case in test_cases:
            try:
                result = self.orchestrator.handle_query(test_case["question"])
                
                # Check table detection
                if "expected_table" in test_case:
                    if result.get("ai_enhancements", {}).get("nlu_method") == "transformer":
                        ai_results["nlu_accuracy"] += 1
                
                # Check aggregation detection
                if "expected_agg" in test_case:
                    sql = result.get("sql", "")
                    if test_case["expected_agg"] in sql.upper():
                        correct_predictions += 1
                
                # Check temporal understanding
                if "temporal" in test_case:
                    temporal_info = result.get("ai_enhancements", {}).get("temporal_intent", {})
                    if temporal_info.get("time_range") == test_case["temporal"]:
                        ai_results["temporal_understanding"] += 1
                
                # Check comparative reasoning
                if "comparison" in test_case:
                    comparative_info = result.get("ai_enhancements", {}).get("comparative_intent", {})
                    if comparative_info.get("comparison") == test_case["comparison"]:
                        ai_results["comparative_reasoning"] += 1
                
                # Check confidence scoring
                confidence = result.get("confidence", 0)
                if confidence > 0.5:
                    ai_results["confidence_scoring"] += 1
                
                print(f"  ✅ {test_case['question'][:50]}... - Confidence: {confidence:.2f}")
                
            except Exception as e:
                print(f"  ❌ {test_case['question'][:50]}... - Error: {e}")
        
        # Calculate percentages
        for key in ai_results:
            if total_tests > 0:
                ai_results[key] = (ai_results[key] / total_tests) * 100
        
        return ai_results
    
    def evaluate_performance_features(self) -> Dict:
        """Evaluate performance optimization features"""
        perf_results = {
            "query_optimization": 0,
            "caching_effectiveness": 0,
            "performance_monitoring": 0,
            "resource_usage": 0,
            "optimization_suggestions": 0
        }
        
        # Test query optimization
        test_queries = [
            "SELECT * FROM students",
            "SELECT name, marks FROM students WHERE marks > 80",
            "SELECT department, COUNT(*) FROM students GROUP BY department",
            "SELECT s.name, c.name FROM students s JOIN courses c ON s.department = c.department"
        ]
        
        optimization_count = 0
        total_time = 0
        
        for query in test_queries:
            try:
                start_time = time.time()
                optimized_query, optimizations = performance_optimizer.optimize_query_execution(query, "default")
                end_time = time.time()
                
                if optimizations:
                    optimization_count += 1
                    perf_results["query_optimization"] += 1
                
                total_time += (end_time - start_time)
                print(f"  ⚡ Query optimized in {(end_time - start_time)*1000:.2f}ms")
                
            except Exception as e:
                print(f"  ❌ Performance test failed: {e}")
        
        # Test performance monitoring
        try:
            report = performance_optimizer.get_performance_report(1)
            if report and "total_queries" in report:
                perf_results["performance_monitoring"] = 100
                print(f"  📊 Performance report generated: {report['total_queries']} queries")
        except Exception as e:
            print(f"  ❌ Performance monitoring failed: {e}")
        
        # Test optimization suggestions
        try:
            suggestions = performance_optimizer.get_optimization_recommendations()
            if suggestions:
                perf_results["optimization_suggestions"] = 100
                print(f"  💡 Generated {len(suggestions)} optimization suggestions")
        except Exception as e:
            print(f"  ❌ Optimization suggestions failed: {e}")
        
        # Calculate percentages
        total_perf_tests = len(test_queries)
        if total_perf_tests > 0:
            perf_results["query_optimization"] = (optimization_count / total_perf_tests) * 100
        
        return perf_results
    
    def evaluate_security_features(self) -> Dict:
        """Evaluate security framework features"""
        security_results = {
            "authentication": 0,
            "authorization": 0,
            "sql_injection_protection": 0,
            "audit_logging": 0,
            "user_management": 0
        }
        
        # Test user creation and authentication
        try:
            # Create test user
            success, message = security_manager.create_user(
                "eval_user", "eval@example.com", "EvalPass123!", UserRole.ANALYST
            )
            if success:
                security_results["user_management"] = 100
                print(f"  👤 User creation successful")
            
            # Test authentication
            token, auth_message = security_manager.authenticate_user("eval_user", "EvalPass123!")
            if token:
                security_results["authentication"] = 100
                print(f"  🔐 Authentication successful")
            
        except Exception as e:
            print(f"  ❌ Security test failed: {e}")
        
        # Test SQL injection protection
        dangerous_queries = [
            "SELECT * FROM students; DROP TABLE students; --",
            "SELECT * FROM students WHERE name = 'admin' OR '1'='1'",
            "SELECT * FROM students UNION SELECT * FROM users",
            "'; EXEC xp_cmdshell('dir'); --"
        ]
        
        blocked_count = 0
        for query in dangerous_queries:
            try:
                has_permission, message = security_manager.check_query_permission("eval_user", query, "default")
                if not has_permission:
                    blocked_count += 1
                    print(f"  🛡️  Dangerous query blocked: {query[:50]}...")
            except Exception as e:
                print(f"  ❌ Security check failed: {e}")
        
        if len(dangerous_queries) > 0:
            security_results["sql_injection_protection"] = (blocked_count / len(dangerous_queries)) * 100
        
        # Test audit logging
        try:
            initial_count = len(security_manager.audit_logs)
            security_manager._log_audit(
                user_id="eval_user",
                action="test_action",
                resource="test_resource",
                ip_address="127.0.0.1",
                user_agent="test_agent",
                success=True
            )
            final_count = len(security_manager.audit_logs)
            if final_count > initial_count:
                security_results["audit_logging"] = 100
                print(f"  📝 Audit logging successful")
        except Exception as e:
            print(f"  ❌ Audit logging failed: {e}")
        
        return security_results
    
    def evaluate_multi_database_features(self) -> Dict:
        """Evaluate multi-database support"""
        db_results = {
            "connection_management": 0,
            "schema_introspection": 0,
            "query_execution": 0,
            "database_switching": 0
        }
        
        # Test connection management
        try:
            connections = db_manager.list_connections()
            if connections and len(connections) > 0:
                db_results["connection_management"] = 100
                print(f"  🔗 Found {len(connections)} database connections")
        except Exception as e:
            print(f"  ❌ Connection management failed: {e}")
        
        # Test schema introspection
        try:
            for conn_name in db_manager.list_connections()[:1]:  # Test first connection
                schema, relations = db_manager.get_schema(conn_name)
                if schema and isinstance(schema, dict):
                    db_results["schema_introspection"] = 100
                    print(f"  📋 Schema introspection successful for {conn_name}")
                    break
        except Exception as e:
            print(f"  ❌ Schema introspection failed: {e}")
        
        # Test database switching
        try:
            result = self.orchestrator.handle_query("load default", user_id="admin")
            if result.get("database") == "default":
                db_results["database_switching"] = 100
                print(f"  🔄 Database switching successful")
        except Exception as e:
            print(f"  ❌ Database switching failed: {e}")
        
        return db_results
    
    def evaluate_integration_features(self) -> Dict:
        """Evaluate system integration"""
        integration_results = {
            "end_to_end_processing": 0,
            "error_handling": 0,
            "response_time": 0,
            "feature_coordination": 0
        }
        
        # Test end-to-end processing
        complex_queries = [
            "What is the average marks of students in computer science department?",
            "Count the number of courses offered by each department",
            "Find students with marks greater than 80 enrolled in database courses"
        ]
        
        successful_queries = 0
        response_times = []
        
        for query in complex_queries:
            try:
                start_time = time.time()
                result = self.orchestrator.handle_query(query, user_id="admin")
                end_time = time.time()
                
                response_time = end_time - start_time
                response_times.append(response_time)
                
                # Check if all components are present
                if (result.get("sql") and 
                    result.get("explanation") and 
                    result.get("confidence") > 0 and
                    "ai_enhancements" in result and
                    "performance_metrics" in result and
                    "security_info" in result):
                    
                    successful_queries += 1
                    print(f"  ✅ Complex query processed in {response_time:.3f}s")
                else:
                    print(f"  ⚠️  Partial success for: {query[:50]}...")
                    
            except Exception as e:
                print(f"  ❌ Integration test failed: {e}")
        
        # Calculate results
        if len(complex_queries) > 0:
            integration_results["end_to_end_processing"] = (successful_queries / len(complex_queries)) * 100
        
        if response_times:
            avg_response_time = statistics.mean(response_times)
            integration_results["response_time"] = 100 if avg_response_time < 2.0 else 50
            print(f"  ⏱️  Average response time: {avg_response_time:.3f}s")
        
        # Test feature coordination
        try:
            status = self.orchestrator.get_system_status()
            if (status.get("ai_integration") == "enabled" and
                status.get("multi_database", {}).get("supported") and
                status.get("performance_optimization", {}).get("enabled") and
                status.get("security", {}).get("enabled")):
                integration_results["feature_coordination"] = 100
                print(f"  🎯 All features properly coordinated")
        except Exception as e:
            print(f"  ❌ Feature coordination test failed: {e}")
        
        return integration_results
    
    def generate_evaluation_report(self):
        """Generate comprehensive evaluation report"""
        print("\n" + "=" * 80)
        print("📊 COMPREHENSIVE EVALUATION REPORT")
        print("=" * 80)
        
        # Calculate overall scores
        categories = ["ai_ml_tests", "performance_tests", "security_tests", "multi_db_tests", "integration_tests"]
        category_scores = {}
        
        for category in categories:
            if category in self.results and self.results[category]:
                scores = list(self.results[category].values())
                if scores:
                    category_scores[category] = statistics.mean(scores)
                else:
                    category_scores[category] = 0
            else:
                category_scores[category] = 0
        
        overall_score = statistics.mean(category_scores.values()) if category_scores else 0
        
        # Print detailed results
        print(f"\n🎯 OVERALL SCORE: {overall_score:.1f}/100")
        print("\n📈 CATEGORY BREAKDOWN:")
        
        category_names = {
            "ai_ml_tests": "🤖 AI/ML Capabilities",
            "performance_tests": "⚡ Performance Optimization",
            "security_tests": "🔐 Security Framework",
            "multi_db_tests": "🗄️ Multi-Database Support",
            "integration_tests": "🔗 System Integration"
        }
        
        for category, score in category_scores.items():
            status = "🟢" if score >= 80 else "🟡" if score >= 60 else "🔴"
            print(f"  {status} {category_names[category]}: {score:.1f}/100")
        
        # Detailed breakdowns
        print("\n📋 DETAILED BREAKDOWN:")
        
        for category in categories:
            if category in self.results and self.results[category]:
                print(f"\n{category_names[category]}:")
                for metric, value in self.results[category].items():
                    status = "✅" if value >= 80 else "⚠️" if value >= 60 else "❌"
                    print(f"  {status} {metric.replace('_', ' ').title()}: {value:.1f}%")
        
        # Recommendations
        print("\n💡 RECOMMENDATIONS:")
        recommendations = self._generate_recommendations(category_scores)
        for i, rec in enumerate(recommendations, 1):
            print(f"  {i}. {rec}")
        
        # Save results to file
        self._save_evaluation_results(overall_score, category_scores)
        
        # Generate visualization
        self._generate_visualization(category_scores)
    
    def _generate_recommendations(self, category_scores: Dict) -> List[str]:
        """Generate improvement recommendations based on scores"""
        recommendations = []
        
        if category_scores.get("ai_ml_tests", 0) < 80:
            recommendations.append("Improve AI/ML model training with more diverse datasets")
        
        if category_scores.get("performance_tests", 0) < 80:
            recommendations.append("Optimize query caching and implement better indexing strategies")
        
        if category_scores.get("security_tests", 0) < 80:
            recommendations.append("Enhance security policies and add more comprehensive audit logging")
        
        if category_scores.get("multi_db_tests", 0) < 80:
            recommendations.append("Expand multi-database support and improve connection management")
        
        if category_scores.get("integration_tests", 0) < 80:
            recommendations.append("Improve error handling and feature coordination")
        
        if not recommendations:
            recommendations.append("System is performing excellently! Consider advanced optimizations")
        
        return recommendations
    
    def _save_evaluation_results(self, overall_score: float, category_scores: Dict):
        """Save evaluation results to JSON file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"evaluation_results_{timestamp}.json"
        
        results_data = {
            "timestamp": datetime.now().isoformat(),
            "overall_score": overall_score,
            "category_scores": category_scores,
            "detailed_results": self.results
        }
        
        try:
            with open(filename, 'w') as f:
                json.dump(results_data, f, indent=2)
            print(f"\n💾 Results saved to: {filename}")
        except Exception as e:
            print(f"\n❌ Failed to save results: {e}")
    
    def _generate_visualization(self, category_scores: Dict):
        """Generate evaluation visualization"""
        try:
            categories = list(category_scores.keys())
            scores = list(category_scores.values())
            
            category_labels = [
                "AI/ML", "Performance", "Security", "Multi-DB", "Integration"
            ]
            
            plt.figure(figsize=(12, 6))
            bars = plt.bar(category_labels, scores, color=['#4CAF50', '#2196F3', '#FF9800', '#9C27B0', '#F44336'])
            
            plt.title('NeuroSQL Enhanced Evaluation Results', fontsize=16, fontweight='bold')
            plt.ylabel('Score (%)', fontsize=12)
            plt.ylim(0, 100)
            
            # Add value labels on bars
            for bar, score in zip(bars, scores):
                plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1, 
                        f'{score:.1f}%', ha='center', va='bottom', fontweight='bold')
            
            # Add horizontal lines for benchmarks
            plt.axhline(y=80, color='green', linestyle='--', alpha=0.7, label='Excellent (80%)')
            plt.axhline(y=60, color='orange', linestyle='--', alpha=0.7, label='Good (60%)')
            
            plt.legend()
            plt.tight_layout()
            
            # Save plot
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"evaluation_chart_{timestamp}.png"
            plt.savefig(filename, dpi=300, bbox_inches='tight')
            print(f"📊 Chart saved to: {filename}")
            
        except Exception as e:
            print(f"❌ Failed to generate visualization: {e}")

def main():
    """Run enhanced evaluation"""
    evaluator = EnhancedEvaluator()
    results = evaluator.run_comprehensive_evaluation()
    return results

if __name__ == "__main__":
    main()
