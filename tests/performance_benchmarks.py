"""
Performance Benchmarks and Stress Tests for NeuroSQL Enhanced
Tests system performance under various load conditions
"""

import asyncio
import time
import threading
import multiprocessing
import psutil
import gc
import statistics
import json
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.enhanced_orchestrator import EnhancedOrchestrator
from core.security_manager import security_manager, UserRole
from core.performance_optimizer import performance_optimizer

class PerformanceBenchmark:
    """Comprehensive performance testing suite"""
    
    def __init__(self):
        self.orchestrator = EnhancedOrchestrator()
        self.results = {}
        
    def run_all_benchmarks(self):
        """Run all performance benchmarks"""
        print("🚀 Starting Performance Benchmark Suite")
        print("=" * 60)
        
        # Single-threaded performance
        print("\n📊 Single-threaded Performance Tests...")
        self.results["single_threaded"] = self.benchmark_single_threaded()
        
        # Concurrent performance
        print("\n🔄 Concurrent Performance Tests...")
        self.results["concurrent"] = self.benchmark_concurrent()
        
        # Memory usage tests
        print("\n💾 Memory Usage Tests...")
        self.results["memory"] = self.benchmark_memory_usage()
        
        # Stress tests
        print("\n💪 Stress Tests...")
        self.results["stress"] = self.benchmark_stress_tests()
        
        # Scalability tests
        print("\n📈 Scalability Tests...")
        self.results["scalability"] = self.benchmark_scalability()
        
        # Generate report
        self.generate_benchmark_report()
        
        return self.results
    
    def benchmark_single_threaded(self) -> Dict:
        """Benchmark single-threaded performance"""
        results = {
            "simple_queries": [],
            "complex_queries": [],
            "ai_enhanced_queries": []
        }
        
        # Test queries of different complexity
        simple_queries = [
            "Show me all students",
            "List all courses", 
            "Count enrollments",
            "Show departments"
        ]
        
        complex_queries = [
            "Find students with marks greater than 80 in computer science department",
            "Count courses by department with average credits",
            "Show students and their enrolled courses",
            "Find top performing students in each department"
        ]
        
        ai_enhanced_queries = [
            "What were the enrollments last month?",
            "Find students with salary between 50000 and 80000",
            "Show sales trends from this year",
            "Compare performance across departments"
        ]
        
        # Benchmark simple queries
        print("  Testing simple queries...")
        for query in simple_queries:
            times = []
            for _ in range(10):  # Run each query 10 times
                start = time.time()
                try:
                    result = self.orchestrator.handle_query(query, user_id="admin")
                    end = time.time()
                    times.append((end - start) * 1000)  # Convert to ms
                except Exception as e:
                    print(f"    ❌ Query failed: {e}")
            
            if times:
                avg_time = statistics.mean(times)
                results["simple_queries"].append({
                    "query": query[:50] + "...",
                    "avg_time_ms": avg_time,
                    "min_time_ms": min(times),
                    "max_time_ms": max(times),
                    "std_dev": statistics.stdev(times) if len(times) > 1 else 0
                })
                print(f"    ✅ {query[:30]}... - {avg_time:.2f}ms avg")
        
        # Benchmark complex queries
        print("  Testing complex queries...")
        for query in complex_queries:
            times = []
            for _ in range(5):  # Run each query 5 times
                start = time.time()
                try:
                    result = self.orchestrator.handle_query(query, user_id="admin")
                    end = time.time()
                    times.append((end - start) * 1000)
                except Exception as e:
                    print(f"    ❌ Query failed: {e}")
            
            if times:
                avg_time = statistics.mean(times)
                results["complex_queries"].append({
                    "query": query[:50] + "...",
                    "avg_time_ms": avg_time,
                    "min_time_ms": min(times),
                    "max_time_ms": max(times),
                    "std_dev": statistics.stdev(times) if len(times) > 1 else 0
                })
                print(f"    ✅ {query[:30]}... - {avg_time:.2f}ms avg")
        
        # Benchmark AI-enhanced queries
        print("  Testing AI-enhanced queries...")
        for query in ai_enhanced_queries:
            times = []
            for _ in range(3):  # Run each query 3 times
                start = time.time()
                try:
                    result = self.orchestrator.handle_query(query, user_id="admin")
                    end = time.time()
                    times.append((end - start) * 1000)
                except Exception as e:
                    print(f"    ❌ Query failed: {e}")
            
            if times:
                avg_time = statistics.mean(times)
                results["ai_enhanced_queries"].append({
                    "query": query[:50] + "...",
                    "avg_time_ms": avg_time,
                    "min_time_ms": min(times),
                    "max_time_ms": max(times),
                    "std_dev": statistics.stdev(times) if len(times) > 1 else 0
                })
                print(f"    ✅ {query[:30]}... - {avg_time:.2f}ms avg")
        
        return results
    
    def benchmark_concurrent(self) -> Dict:
        """Benchmark concurrent query processing"""
        results = {
            "thread_pool": {},
            "async_processing": {},
            "resource_contention": {}
        }
        
        # Test with different numbers of concurrent threads
        thread_counts = [2, 5, 10, 20, 50]
        test_query = "Show me all students"
        
        print("  Testing thread pool performance...")
        for thread_count in thread_counts:
            times = []
            start_memory = psutil.Process().memory_info().rss
            
            def run_query():
                start = time.time()
                try:
                    # Create new orchestrator for each thread to avoid conflicts
                    orchestrator = EnhancedOrchestrator()
                    result = orchestrator.handle_query(test_query, user_id="admin")
                    end = time.time()
                    return end - start
                except Exception as e:
                    print(f"    ❌ Concurrent query failed: {e}")
                    return float('inf')
            
            # Run queries concurrently
            with ThreadPoolExecutor(max_workers=thread_count) as executor:
                futures = [executor.submit(run_query) for _ in range(thread_count)]
                query_times = [future.result() for future in as_completed(futures)]
                
                # Filter out failed queries
                valid_times = [t for t in query_times if t != float('inf')]
                if valid_times:
                    avg_time = statistics.mean(valid_times)
                    results["thread_pool"][thread_count] = {
                        "avg_time_ms": avg_time * 1000,
                        "throughput_qps": thread_count / avg_time,
                        "success_rate": len(valid_times) / len(query_times) * 100
                    }
                    
                    end_memory = psutil.Process().memory_info().rss
                    memory_increase = (end_memory - start_memory) / 1024 / 1024  # MB
                    
                    print(f"    ✅ {thread_count} threads - {avg_time*1000:.2f}ms avg, "
                          f"{thread_count/avg_time:.1f} QPS, {memory_increase:.1f}MB memory")
        
        return results
    
    def benchmark_memory_usage(self) -> Dict:
        """Benchmark memory usage patterns"""
        results = {
            "baseline_memory": 0,
            "query_memory": [],
            "memory_leaks": [],
            "garbage_collection": {}
        }
        
        # Measure baseline memory
        gc.collect()  # Force garbage collection
        baseline_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
        results["baseline_memory"] = baseline_memory
        print(f"  Baseline memory: {baseline_memory:.1f}MB")
        
        # Test memory usage during queries
        test_queries = [
            "Show me all students",
            "Count students by department",
            "Find students with marks > 80",
            "Complex join query with aggregations"
        ]
        
        memory_measurements = []
        
        for i, query in enumerate(test_queries):
            gc.collect()
            pre_memory = psutil.Process().memory_info().rss / 1024 / 1024
            
            # Run query multiple times
            for _ in range(10):
                try:
                    result = self.orchestrator.handle_query(query, user_id="admin")
                except Exception as e:
                    print(f"    ❌ Memory test query failed: {e}")
            
            post_memory = psutil.Process().memory_info().rss / 1024 / 1024
            memory_increase = post_memory - pre_memory
            
            memory_measurements.append({
                "query": query[:30] + "...",
                "memory_increase_mb": memory_increase,
                "pre_memory_mb": pre_memory,
                "post_memory_mb": post_memory
            })
            
            print(f"    Query {i+1}: +{memory_increase:.1f}MB")
        
        results["query_memory"] = memory_measurements
        
        # Test for memory leaks
        print("  Testing for memory leaks...")
        leak_measurements = []
        
        for iteration in range(5):
            gc.collect()
            start_memory = psutil.Process().memory_info().rss / 1024 / 1024
            
            # Run many queries
            for i in range(100):
                try:
                    self.orchestrator.handle_query(f"Show students {i}", user_id="admin")
                except:
                    pass
            
            gc.collect()
            end_memory = psutil.Process().memory_info().rss / 1024 / 1024
            leak_measurements.append(end_memory - start_memory)
            
            print(f"    Iteration {iteration+1}: +{end_memory - start_memory:.1f}MB")
        
        results["memory_leaks"] = leak_measurements
        
        return results
    
    def benchmark_stress_tests(self) -> Dict:
        """Stress test the system under high load"""
        results = {
            "high_concurrency": {},
            "sustained_load": {},
            "error_rates": {},
            "resource_exhaustion": {}
        }
        
        # High concurrency stress test
        print("  Running high concurrency stress test...")
        concurrent_users = [10, 25, 50, 100]
        
        for user_count in concurrent_users:
            errors = 0
            successes = 0
            start_time = time.time()
            
            def stress_query():
                nonlocal errors, successes
                try:
                    orchestrator = EnhancedOrchestrator()
                    result = orchestrator.handle_query("Show me all students", user_id="admin")
                    successes += 1
                except Exception as e:
                    errors += 1
            
            # Run concurrent queries
            threads = []
            for _ in range(user_count):
                thread = threading.Thread(target=stress_query)
                threads.append(thread)
                thread.start()
            
            # Wait for all threads to complete
            for thread in threads:
                thread.join()
            
            end_time = time.time()
            total_time = end_time - start_time
            
            results["high_concurrency"][user_count] = {
                "successes": successes,
                "errors": errors,
                "error_rate": errors / (successes + errors) * 100,
                "total_time": total_time,
                "throughput_qps": (successes + errors) / total_time
            }
            
            print(f"    {user_count} users: {successes} success, {errors} errors, "
                  f"{(successes+errors)/total_time:.1f} QPS")
        
        # Sustained load test
        print("  Running sustained load test...")
        duration_seconds = 60  # 1 minute test
        start_time = time.time()
        query_count = 0
        error_count = 0
        
        while time.time() - start_time < duration_seconds:
            try:
                self.orchestrator.handle_query(f"Show students {query_count}", user_id="admin")
                query_count += 1
            except Exception as e:
                error_count += 1
            
            time.sleep(0.01)  # Small delay to prevent overwhelming
        
        actual_duration = time.time() - start_time
        results["sustained_load"] = {
            "duration_seconds": actual_duration,
            "queries_processed": query_count,
            "errors": error_count,
            "error_rate": error_count / (query_count + error_count) * 100,
            "avg_qps": query_count / actual_duration
        }
        
        print(f"    Sustained load: {query_count} queries in {actual_duration:.1f}s, "
              f"{query_count/actual_duration:.1f} QPS")
        
        return results
    
    def benchmark_scalability(self) -> Dict:
        """Test system scalability with increasing complexity"""
        results = {
            "query_complexity": {},
            "data_volume": {},
            "feature_overhead": {}
        }
        
        # Test query complexity scalability
        complexity_queries = [
            ("Simple", "Show students"),
            ("Medium", "Show students with marks > 80"),
            ("Complex", "Show students with marks > 80 in CS department"),
            ("Very Complex", "Show students with marks > dept average, enrolled in >3 courses")
        ]
        
        print("  Testing query complexity scalability...")
        for complexity, query in complexity_queries:
            times = []
            for _ in range(5):
                start = time.time()
                try:
                    result = self.orchestrator.handle_query(query, user_id="admin")
                    end = time.time()
                    times.append((end - start) * 1000)
                except Exception as e:
                    print(f"    ❌ Scalability test failed: {e}")
            
            if times:
                avg_time = statistics.mean(times)
                results["query_complexity"][complexity] = {
                    "avg_time_ms": avg_time,
                    "complexity_factor": avg_time / times[0] if times else 1
                }
                print(f"    {complexity}: {avg_time:.2f}ms")
        
        # Test feature overhead
        features_test = [
            ("Basic", "Show students"),
            ("With Security", "Show students", {"with_security": True}),
            ("With Performance", "Show students", {"with_performance": True}),
            ("With AI", "Show students", {"with_ai": True}),
            ("All Features", "Show students", {"with_all": True})
        ]
        
        print("  Testing feature overhead...")
        for feature_name, query, options in features_test:
            times = []
            for _ in range(5):
                start = time.time()
                try:
                    result = self.orchestrator.handle_query(query, user_id="admin")
                    end = time.time()
                    times.append((end - start) * 1000)
                except Exception as e:
                    print(f"    ❌ Feature overhead test failed: {e}")
            
            if times:
                avg_time = statistics.mean(times)
                results["feature_overhead"][feature_name] = {
                    "avg_time_ms": avg_time
                }
                print(f"    {feature_name}: {avg_time:.2f}ms")
        
        return results
    
    def generate_benchmark_report(self):
        """Generate comprehensive benchmark report"""
        print("\n" + "=" * 80)
        print("📊 PERFORMANCE BENCHMARK REPORT")
        print("=" * 80)
        
        # Single-threaded performance summary
        if "single_threaded" in self.results:
            st_results = self.results["single_threaded"]
            print("\n🎯 SINGLE-THREADED PERFORMANCE:")
            
            for query_type in ["simple_queries", "complex_queries", "ai_enhanced_queries"]:
                if query_type in st_results and st_results[query_type]:
                    times = [q["avg_time_ms"] for q in st_results[query_type]]
                    avg_time = statistics.mean(times)
                    print(f"  {query_type.replace('_', ' ').title()}: {avg_time:.2f}ms avg")
        
        # Concurrent performance summary
        if "concurrent" in self.results:
            conc_results = self.results["concurrent"]
            if "thread_pool" in conc_results:
                print("\n🔄 CONCURRENT PERFORMANCE:")
                for thread_count, metrics in conc_results["thread_pool"].items():
                    print(f"  {thread_count} threads: {metrics['throughput_qps']:.1f} QPS, "
                          f"{metrics['success_rate']:.1f}% success rate")
        
        # Memory usage summary
        if "memory" in self.results:
            mem_results = self.results["memory"]
            print("\n💾 MEMORY USAGE:")
            print(f"  Baseline: {mem_results.get('baseline_memory', 0):.1f}MB")
            
            if "query_memory" in mem_results:
                avg_increase = statistics.mean([q["memory_increase_mb"] for q in mem_results["query_memory"]])
                print(f"  Average increase per query: {avg_increase:.1f}MB")
            
            if "memory_leaks" in mem_results:
                avg_leak = statistics.mean(mem_results["memory_leaks"])
                print(f"  Average memory leak per 100 queries: {avg_leak:.1f}MB")
        
        # Stress test summary
        if "stress" in self.results:
            stress_results = self.results["stress"]
            print("\n💪 STRESS TEST RESULTS:")
            
            if "high_concurrency" in stress_results:
                max_qps = 0
                best_config = None
                for users, metrics in stress_results["high_concurrency"].items():
                    if metrics["throughput_qps"] > max_qps:
                        max_qps = metrics["throughput_qps"]
                        best_config = users
                print(f"  Max throughput: {max_qps:.1f} QPS at {best_config} concurrent users")
            
            if "sustained_load" in stress_results:
                sustained = stress_results["sustained_load"]
                print(f"  Sustained load: {sustained['avg_qps']:.1f} QPS for {sustained['duration_seconds']:.1f}s")
        
        # Save results
        self._save_benchmark_results()
    
    def _save_benchmark_results(self):
        """Save benchmark results to file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"performance_benchmark_{timestamp}.json"
        
        try:
            with open(filename, 'w') as f:
                json.dump(self.results, f, indent=2, default=str)
            print(f"\n💾 Benchmark results saved to: {filename}")
        except Exception as e:
            print(f"\n❌ Failed to save benchmark results: {e}")

def main():
    """Run performance benchmarks"""
    benchmark = PerformanceBenchmark()
    results = benchmark.run_all_benchmarks()
    return results

if __name__ == "__main__":
    main()
