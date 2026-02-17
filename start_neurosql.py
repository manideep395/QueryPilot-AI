#!/usr/bin/env python3
"""
NeuroSQL Enhanced Startup Script
Handles missing dependencies gracefully and provides fallback options
"""

import sys
import os
import subprocess

def check_dependencies():
    """Check which dependencies are available"""
    print("🔍 Checking dependencies...")
    
    # Check for torch/transformers
    try:
        import torch
        import transformers
        print("✅ PyTorch and Transformers available")
        return "full"
    except ImportError:
        print("⚠️  PyTorch/Transformers not found")
        return "basic"

def install_basic_dependencies():
    """Install basic dependencies"""
    print("📦 Installing basic dependencies...")
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", "requirements_basic.txt"
        ])
        print("✅ Basic dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def install_full_dependencies():
    """Install full dependencies including ML"""
    print("🤖 Installing full dependencies (including ML)...")
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ])
        print("✅ Full dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def start_basic_mode():
    """Start NeuroSQL in basic mode (without ML features)"""
    print("🚀 Starting NeuroSQL in basic mode...")
    os.system("python main.py")

def start_enhanced_mode():
    """Start NeuroSQL in enhanced mode (with ML features)"""
    print("🧠 Starting NeuroSQL Enhanced mode...")
    os.system("python enhanced_main.py")

def main():
    """Main startup logic"""
    print("🚀 NeuroSQL Enhanced v2.0 Startup")
    print("=" * 50)
    
    # Check dependencies
    mode = check_dependencies()
    
    if mode == "full":
        print("\n✨ All dependencies available - starting enhanced mode")
        start_enhanced_mode()
    elif mode == "basic":
        print("\n⚙️  Basic mode - starting without ML features")
        start_basic_mode()
    else:
        print("\n📦 Missing dependencies detected!")
        print("Choose an option:")
        print("1. Install basic dependencies (faster, no ML features)")
        print("2. Install full dependencies (slower, includes ML features)")
        print("3. Start in basic mode (without ML)")
        print("4. Exit")
        
        try:
            choice = input("\nEnter your choice (1-4): ").strip()
            
            if choice == "1":
                if install_basic_dependencies():
                    start_enhanced_mode()  # Try enhanced mode after installing basic
                else:
                    start_basic_mode()
            elif choice == "2":
                if install_full_dependencies():
                    start_enhanced_mode()
                else:
                    print("❌ Failed to install dependencies")
            elif choice == "3":
                start_basic_mode()
            elif choice == "4":
                print("👋 Goodbye!")
                sys.exit(0)
            else:
                print("❌ Invalid choice")
                sys.exit(1)
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            sys.exit(0)

if __name__ == "__main__":
    main()
