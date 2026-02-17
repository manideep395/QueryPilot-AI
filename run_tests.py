"""
Comprehensive Test Runner for NeuroSQL Enhanced
Runs all test suites and generates combined reports
"""

import sys
import os
import subprocess
import time
import json
from datetime import datetime
from typing import Dict, List, Any

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def run_command(command: str, description: str) -> Dict:
    """Run a command and return results"""
    print(f"\n🔄 {description}")
    print("-" * 50)
    
    start_time = time.time()
    
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        
        end_time = time.time()
        duration = end_time - start_time
        
        success = result.returncode == 0
        
        status = "✅" if success else "❌"
        print(f"{status} {description} completed in {duration:.2f}s")
        
        if not success:
            print(f"Error output: {result.stderr}")
        
        return {
            "command": command,
            "description": description,
            "success": success,
            "duration": duration,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode
        }
        
    except subprocess.TimeoutExpired:
        print(f"⏰ {description} timed out after 5 minutes")
        return {
            "command": command,
            "description": description,
            "success": False,
            "duration": 300,
            "stdout": "",
            "stderr": "Test timed out",
            "returncode": -1
        }
    except Exception as e:
        print(f"❌ Error running {description}: {e}")
        return {
            "command": command,
            "description": description,
            "success": False,
            "duration": 0,
            "stdout": "",
            "stderr": str(e),
            "returncode": -2
        }

def run_all_tests():
    """Run all test suites"""
    print("🚀 NeuroSQL Enhanced - Comprehensive Test Suite")
    print("=" * 80)
    
    test_results = {}
    
    # 1. Unit Tests
    test_results["unit_tests"] = run_command(
        "python -m pytest tests/test_enhanced_features.py -v",
        "Unit Tests (Enhanced Features)"
    )
    
    # 2. Integration Tests
    test_results["integration_tests"] = run_command(
        "python tests/integration_tests.py",
        "Integration Tests (Web API & Security)"
    )
    
    # 3. Performance Benchmarks
    test_results["performance_benchmarks"] = run_command(
        "python tests/performance_benchmarks.py",
        "Performance Benchmarks & Stress Tests"
    )
    
    # 4. Enhanced Evaluation
    test_results["enhanced_evaluation"] = run_command(
        "python evaluation/enhanced_evaluator.py",
        "Enhanced Evaluation Suite (AI/ML, Performance, Security)"
    )
    
    # 5. Sample Data Generation
    test_results["sample_data"] = run_command(
        "python data/enhanced_sample_data.py",
        "Sample Data Generation & Validation"
    )
    
    # Generate combined report
    generate_combined_report(test_results)
    
    return test_results

def generate_combined_report(test_results: Dict):
    """Generate combined test report"""
    print("\n" + "=" * 80)
    print("📊 COMPREHENSIVE TEST REPORT")
    print("=" * 80)
    
    # Calculate overall statistics
    total_tests = len(test_results)
    passed_tests = sum(1 for result in test_results.values() if result["success"])
    total_duration = sum(result["duration"] for result in test_results.values())
    
    print(f"\n📈 OVERALL SUMMARY:")
    print(f"  Total Test Suites: {total_tests}")
    print(f"  Passed: {passed_tests}")
    print(f"  Failed: {total_tests - passed_tests}")
    print(f"  Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    print(f"  Total Duration: {total_duration:.2f}s")
    
    # Detailed results
    print(f"\n📋 DETAILED RESULTS:")
    
    for test_name, result in test_results.items():
        status = "✅ PASSED" if result["success"] else "❌ FAILED"
        duration = result["duration"]
        
        print(f"\n  {test_name.replace('_', ' ').title()}:")
        print(f"    Status: {status}")
        print(f"    Duration: {duration:.2f}s")
        
        if not result["success"]:
            print(f"    Error: {result['stderr'][:200]}...")
    
    # Recommendations
    print(f"\n💡 RECOMMENDATIONS:")
    
    failed_tests = [name for name, result in test_results.items() if not result["success"]]
    
    if not failed_tests:
        print("  🎉 All tests passed! System is ready for production.")
    else:
        for failed_test in failed_tests:
            if "unit" in failed_test:
                print(f"  🔧 Fix unit test failures in {failed_test}")
            elif "integration" in failed_test:
                print(f"  🔗 Resolve integration issues between components")
            elif "performance" in failed_test:
                print(f"  ⚡ Optimize performance bottlenecks")
            elif "evaluation" in failed_test:
                print(f"  📊 Address evaluation suite issues")
            elif "sample" in failed_test:
                print(f"  📝 Fix sample data generation problems")
    
    # Save report
    save_test_report(test_results, passed_tests, total_tests, total_duration)

def save_test_report(test_results: Dict, passed: int, total: int, duration: float):
    """Save test report to file"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"test_report_{timestamp}.json"
    
    report_data = {
        "timestamp": datetime.now().isoformat(),
        "summary": {
            "total_test_suites": total,
            "passed_suites": passed,
            "failed_suites": total - passed,
            "success_rate": (passed/total) * 100 if total > 0 else 0,
            "total_duration": duration
        },
        "detailed_results": test_results,
        "recommendations": generate_recommendations(test_results)
    }
    
    try:
        with open(filename, 'w') as f:
            json.dump(report_data, f, indent=2)
        print(f"\n💾 Test report saved to: {filename}")
    except Exception as e:
        print(f"\n❌ Failed to save test report: {e}")

def generate_recommendations(test_results: Dict) -> List[str]:
    """Generate recommendations based on test results"""
    recommendations = []
    
    # Analyze patterns in failures
    failed_tests = [name for name, result in test_results.items() if not result["success"]]
    
    if not failed_tests:
        recommendations.append("All tests passed! System is performing excellently.")
        return recommendations
    
    # Performance-related recommendations
    if any("performance" in test or "benchmark" in test for test in failed_tests):
        recommendations.append("Consider optimizing query performance and caching mechanisms")
        recommendations.append("Review database indexes and query execution plans")
    
    # Security-related recommendations
    if any("security" in test or "integration" in test for test in failed_tests):
        recommendations.append("Review and strengthen security configurations")
        recommendations.append("Ensure proper authentication and authorization flows")
    
    # AI/ML-related recommendations
    if any("evaluation" in test or "enhanced" in test for test in failed_tests):
        recommendations.append("Check AI/ML model configurations and dependencies")
        recommendations.append("Verify transformer model installation and compatibility")
    
    # General recommendations
    if len(failed_tests) > 2:
        recommendations.append("Multiple test suites failed - review system configuration")
        recommendations.append("Check dependencies and environment setup")
    
    return recommendations

def main():
    """Main test runner function"""
    print("NeuroSQL Enhanced Test Runner")
    print("This script will run all test suites and generate a comprehensive report")
    print()
    
    # Check if required directories exist
    required_dirs = ["tests", "evaluation", "data"]
    for dir_name in required_dirs:
        if not os.path.exists(dir_name):
            print(f"❌ Required directory '{dir_name}' not found")
            return
    
    # Run tests
    results = run_all_tests()
    
    # Exit with appropriate code
    all_passed = all(result["success"] for result in results.values())
    sys.exit(0 if all_passed else 1)

if __name__ == "__main__":
    main()
