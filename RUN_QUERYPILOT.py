#!/usr/bin/env python3
"""
QueryPilot AI - Run and Test Script
Runs QueryPilot system and shows detailed output
"""

import sys
import os
import subprocess
import time

def run_querypilot():
    """Run QueryPilot with detailed output"""
    print("🚀 QueryPilot AI - Enhanced NL-to-SQL Platform")
    print("=" * 60)
    print("🎯 Features: Enhanced AI Agents • Multi-Database • Performance • Security")
    print("🤖 AI/ML: BERT/DistilBERT with semantic understanding")
    print("📊 Performance: Real-time monitoring and optimization")
    print("🔐 Security: JWT authentication with RBAC")
    print("🌐 Web Interface: FastAPI with real-time capabilities")
    print("=" * 60)
    
    try:
        # Try to import enhanced orchestrator first
        try:
            from core.enhanced_orchestrator import EnhancedOrchestrator
            print("✅ Enhanced orchestrator loaded successfully!")
            system = EnhancedOrchestrator()
        except ImportError:
            print("⚠️ Enhanced orchestrator not available, using basic orchestrator")
            from core.orchestrator import Orchestrator
            system = Orchestrator("database.db")
        
        print("✅ QueryPilot started successfully!")
        print("🎯 Enhanced Agents: All 4 enhanced agents with graceful fallbacks")
        print("🤖 AI Features: BERT/DistilBERT integration when available")
        
        # Interactive loop with detailed output
        print("\n=== QueryPilot AI - Interactive Mode ===")
        print("Features: Enhanced agents • AI/ML • Performance optimization • Security")
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
                
                if result.get('ai_enhancements'):
                    ai_info = result['ai_enhancements']
                    print(f"🤖 AI Method: {ai_info.get('nlu_method', 'unknown')}")
                    print(f"🧠 Semantic Score: {ai_info.get('semantic_score', 0):.2f}")
                    print(f"📊 AI Confidence: {ai_info.get('ai_confidence', 0):.2f}")
                
                if result.get('performance_metrics'):
                    perf = result['performance_metrics']
                    print(f"📈 Performance Score: {perf.get('performance_score', 0):.1f}/100")
                    print(f"🚀 Query Time: {perf.get('query_execution_time', 0):.3f}s")
                    print(f"📊 Rows Returned: {perf.get('rows_returned', 0)}")
                
                if result.get('security_info'):
                    sec = result['security_info']
                    print(f"🔐 Authenticated: {sec.get('user_authenticated', False)}")
                    print(f"🛡️ Permissions Checked: {sec.get('permissions_checked', False)}")
                
                if result.get('web_info'):
                    web = result['web_info']
                    print(f"🌐 Web Interface: {web.get('available', False)}")
                    print(f"📡 API Status: {web.get('api_status', 'unknown')}")
                
                print("="*80)
                
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
                
    except Exception as e:
        print(f"❌ Failed to start QueryPilot: {e}")

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
            run_querypilot()
        else:
            print("📋 Usage: python RUN_QUERYPILOT.py [info|test]")
            print("  info  - Show system information")
            print("  test  - Run QueryPilot in test mode")
    else:
        print("🚀 QueryPilot AI - Enhanced NL-to-SQL Platform")
        run_querypilot()

if __name__ == "__main__":
    main()
