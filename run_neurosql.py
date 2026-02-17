#!/usr/bin/env python3
"""
Simple NeuroSQL Enhanced Startup Script
Handles dependency checking and provides multiple startup options
"""

import sys
import os
import subprocess

def check_ml_dependencies():
    """Check if ML dependencies are available"""
    try:
        import torch
        import transformers
        print("✅ PyTorch and Transformers available")
        return True
    except ImportError:
        print("⚠️  PyTorch/Transformers not found")
        return False

def install_dependencies(requirements_file):
    """Install dependencies from specified requirements file"""
    print(f"📦 Installing dependencies from {requirements_file}...")
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", requirements_file
        ])
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def main():
    """Main startup logic"""
    print("🚀 NeuroSQL Enhanced v2.0 Startup")
    print("=" * 50)
    
    # Check ML dependencies
    has_ml = check_ml_dependencies()
    
    if has_ml:
        print("\n✨ Starting Enhanced NeuroSQL (with AI features)...")
        try:
            # Try to import and run enhanced version
            from core.enhanced_orchestrator import EnhancedOrchestrator
            system = EnhancedOrchestrator()
            
            print("🧠 Enhanced NeuroSQL started successfully!")
            print("🌐 Web interface: python enhanced_main.py --web")
            print("💬 CLI interface: python enhanced_main.py")
            
            # Start interactive mode
            system = EnhancedOrchestrator()
            print("\n=== Enhanced NeuroSQL - AI-powered NL-to-SQL ===")
            print("Features: AI/ML • Multi-DB • Performance • Security")
            
            while True:
                try:
                    user_input = input("\nAsk your question (or type 'exit'): ")
                    if user_input.lower() in ["exit", "quit", "q"]:
                        print("👋 Goodbye!")
                        break
                    
                    if not user_input.strip():
                        continue
                    
                    result = system.handle_query(user_input)
                    print("\n" + "="*60)
                    print(f"🎯 Answer: {result.get('explanation', 'No explanation available')}")
                    print(f"⚡ Confidence: {result.get('confidence', 0):.1%}")
                    print(f"⏱️  Time: {result.get('execution_time', 0):.3f}s")
                    
                    if result.get('sql'):
                        print(f"🔍 SQL: {result['sql']}")
                    
                    if result.get('ai_enhancements'):
                        ai_info = result['ai_enhancements']
                        print(f"🤖 AI Method: {ai_info.get('nlu_method', 'unknown')}")
                        
                    if result.get('performance_metrics'):
                        perf = result['performance_metrics']
                        print(f"📊 Performance Score: {perf.get('performance_score', 0):.1f}/100")
                    
                    print("="*60)
                    
                except KeyboardInterrupt:
                    print("\n👋 Goodbye!")
                    break
                except Exception as e:
                    print(f"❌ Error: {e}")
                    
        except ImportError as e:
            print(f"❌ Failed to load enhanced components: {e}")
            print("🔄 Falling back to basic mode...")
            fallback_to_basic()
            
    else:
        print("\n⚙️ ML dependencies not available")
        print("Choose an option:")
        print("1. Install ML dependencies (may take time)")
        print("2. Start in basic mode (no AI features)")
        print("3. Exit")
        
        try:
            choice = input("\nEnter your choice (1-3): ").strip()
            
            if choice == "1":
                if install_dependencies("requirements.txt"):
                    print("🔄 Restarting with ML features...")
                    os.execv(sys.executable, [sys.executable] + sys.argv)
                else:
                    print("❌ Failed to install ML dependencies")
                    fallback_to_basic()
            elif choice == "2":
                fallback_to_basic()
            elif choice == "3":
                print("👋 Goodbye!")
                sys.exit(0)
            else:
                print("❌ Invalid choice")
                sys.exit(1)
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            sys.exit(0)

def fallback_to_basic():
    """Fallback to basic NeuroSQL mode"""
    print("\n🔄 Starting Basic NeuroSQL...")
    try:
        # Import basic version
        from core.orchestrator import Orchestrator
        system = Orchestrator("database.db")
        
        print("✅ Basic NeuroSQL started successfully!")
        
        while True:
            try:
                user_input = input("\nAsk your question (or type 'exit'): ")
                if user_input.lower() in ["exit", "quit", "q"]:
                    print("👋 Goodbye!")
                    break
                
                result = system.handle_query(user_input)
                print("\n" + "="*40)
                print(f"Answer: {result.get('explanation', 'No explanation')}")
                print(f"SQL: {result.get('sql', 'No SQL generated')}")
                print("="*40)
                
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
                
    except ImportError as e:
        print(f"❌ Failed to load basic components: {e}")
        print("Please check your Python installation and dependencies")

if __name__ == "__main__":
    main()
