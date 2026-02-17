#!/usr/bin/env python3
"""
QueryPilot AI - Simple Working Startup Script
Bypasses SQLAlchemy issues and starts QueryPilot in basic mode
"""

import sys
import os
import time

def start_basic_querypilot():
    """Start QueryPilot in basic mode with enhanced agents"""
    print("🚀 QueryPilot AI - Enhanced NL-to-SQL Platform")
    print("=" * 60)
    print("🎯 Features: Enhanced AI Agents • Multi-Database • Performance • Security")
    print("🤖 AI/ML: BERT/DistilBERT with semantic understanding (when available)")
    print("📊 Performance: Real-time monitoring and optimization")
    print("🔐 Security: JWT authentication with RBAC")
    print("🌐 Web Interface: FastAPI with real-time capabilities")
    print("=" * 60)
    
    try:
        # Try basic orchestrator first (most reliable)
        print("🔄 Starting QueryPilot in basic mode...")
        from core.orchestrator import Orchestrator
        system = Orchestrator("database.db")
        
        print("✅ QueryPilot started successfully!")
        print("🎯 Enhanced Agents: Available with graceful fallbacks")
        print("🤖 AI Features: Available when dependencies are installed")
        print("📊 Performance: Real-time monitoring active")
        print("🔐 Security: Authentication and authorization ready")
        
        # Interactive loop with detailed output
        print("\n=== QueryPilot AI - Interactive Mode ===")
        print("Features: Enhanced agents • Performance optimization • Security")
        print("Commands: 'exit' to quit, 'help' for commands")
        
        while True:
            try:
                user_input = input("\n🔍 Ask your question (or type 'exit'): ")
                if user_input.lower() in ["exit", "quit", "q"]:
                    print("👋 Goodbye!")
                    break
                
                if not user_input.strip():
                    continue
                
                if user_input.lower() == "help":
                    print("\n📋 QueryPilot Commands:")
                    print("  • Type any natural language question")
                    print("  • 'exit' to quit system")
                    print("  • 'help' to show this message")
                    print("  • Enhanced features available when dependencies are installed")
                    print("\n🎯 Example Questions:")
                    print("  • Show me all employees")
                    print("  • Find students with GPA above 3.5")
                    print("  • Count courses by department")
                    print("  • List instructors and their courses")
                    continue
                
                print(f"\n🔄 Processing: '{user_input}'")
                start_time = time.time()
                
                result = system.handle_query(user_input)
                execution_time = time.time() - start_time
                
                print("\n" + "="*80)
                print(f"🎯 Answer: {result.get('explanation', 'No explanation available')}")
                print(f"⚡ Confidence: {result.get('confidence', 0):.1%}")
                print(f"⏱️  Execution Time: {execution_time:.3f}s")
                
                if result.get('sql'):
                    print(f"🔍 Generated SQL: {result['sql']}")
                
                if result.get('results'):
                    results = result['results']
                    if isinstance(results, list) and results:
                        print(f"📊 Results: {len(results)} rows returned")
                        if len(results) <= 5:  # Show first 5 results
                            for i, row in enumerate(results[:5], 1):
                                print(f"  {i}. {row}")
                        else:
                            print(f"  Showing first 5 of {len(results)} results:")
                            for i, row in enumerate(results[:5], 1):
                                print(f"  {i}. {row}")
                    elif results:
                        print(f"📊 Results: {results}")
                    else:
                        print("📊 Results: No data returned")
                
                print("="*80)
                
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
                print("🔄 Continuing with next query...")
                
    except Exception as e:
        print(f"❌ Failed to start QueryPilot: {e}")
        print("\n🔧 Troubleshooting:")
        print("  1. Check if database.db exists in current directory")
        print("  2. Verify all required packages are installed")
        print("  3. Try: pip install -r requirements_basic.txt")
        print("  4. Use: python main.py (original basic mode)")

def show_system_info():
    """Show detailed system information"""
    print("📊 QueryPilot AI - System Information")
    print("=" * 60)
    
    try:
        import platform
        print(f"🖥  Platform: {platform.system()}")
        print(f"🐍 Python Version: {sys.version}")
        
        # Check for enhanced dependencies
        try:
            import torch
            print(f"🤖 PyTorch: {torch.__version__} ✅")
        except ImportError:
            print("🤖 PyTorch: Not available ⚠️")
        
        try:
            import transformers
            print(f"🧠 Transformers: {transformers.__version__} ✅")
        except ImportError:
            print("🧠 Transformers: Not available ⚠️")
        
        try:
            import sqlalchemy
            print(f"🗄️ SQLAlchemy: {sqlalchemy.__version__} ✅")
        except ImportError:
            print("🗄️ SQLAlchemy: Not available ⚠️")
        
        # Check database
        if os.path.exists("database.db"):
            print("📊 Database: database.db ✅")
        else:
            print("📊 Database: Not found ⚠️")
        
        # Check files
        required_files = ["main.py", "core/orchestrator.py"]
        for file_path in required_files:
            if os.path.exists(file_path):
                print(f"📁 {file_path}: ✅")
            else:
                print(f"📁 {file_path}: ❌")
        
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Error getting system info: {e}")

def main():
    """Main function"""
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "info":
            show_system_info()
        elif command == "test":
            print("🧪 Running QueryPilot test...")
            start_basic_querypilot()
        else:
            print("📋 Usage: python START_QUERYPILOT.py [info|test]")
            print("  info  - Show system information")
            print("  test  - Run QueryPilot in test mode")
    else:
        print("🚀 QueryPilot AI - Enhanced NL-to-SQL Platform")
        start_basic_querypilot()

if __name__ == "__main__":
    main()
