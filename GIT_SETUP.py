#!/usr/bin/env python3
"""
QueryPilot AI - Git Setup Script
Helps set up git repository and push to GitHub
"""

import os
import sys
import subprocess

def run_command(command, description=""):
    """Run a git command with error handling"""
    print(f"🔄 {description}")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} - Success")
            if result.stdout.strip():
                print(f"   Output: {result.stdout.strip()}")
            return True
        else:
            print(f"❌ {description} - Failed")
            if result.stderr.strip():
                print(f"   Error: {result.stderr.strip()}")
            return False
    except Exception as e:
        print(f"❌ {description} - Exception: {e}")
        return False

def setup_git_repository():
    """Set up git repository and push to GitHub"""
    print("🚀 QueryPilot AI - Git Setup Script")
    print("=" * 60)
    
    # Check if we're in a git repository
    if not os.path.exists(".git"):
        print("📁 Initializing git repository...")
        if not run_command("git init", "Initialize git repository"):
            return False
    
    # Check current status
    print("\n📊 Checking git status...")
    run_command("git status", "Check git status")
    
    # Add all files
    print("\n📦 Adding all files...")
    if not run_command("git add .", "Add all files"):
        return False
    
    # Create initial commit
    print("\n💾 Creating initial commit...")
    commit_message = """Initial commit: QueryPilot AI - Enhanced NL-to-SQL Platform

Features:
- Enhanced AI Agents with BERT/DistilBERT integration
- Multi-database support (SQLite, PostgreSQL, MySQL)
- Performance optimization with real-time monitoring
- Security framework with JWT authentication and RBAC
- Web interface with FastAPI and real-time capabilities
- Comprehensive testing suite with performance benchmarks
- Professional documentation and setup guides

Technical Details:
- Enhanced NLU Agent with transformer-based semantic understanding
- Enhanced Execution Agent with multi-database performance monitoring
- Enhanced Reflex Agent with multi-strategy error correction
- Enhanced Explanation Agent with AI-powered insights
- Enhanced Orchestrator coordinating all components
- Complete web interface with real-time capabilities
- Comprehensive test coverage and evaluation suite
- Professional README with complete documentation"""
    
    if not run_command(f'git commit -m "{commit_message}"', "Create initial commit"):
        return False
    
    # Check current branch
    print("\n🌿 Checking current branch...")
    run_command("git branch", "Check current branch")
    
    # Create and switch to main branch
    print("\n🌿 Creating main branch...")
    if not run_command("git checkout -b main", "Create main branch"):
        return False
    
    # Add remote origin
    print("\n🔗 Adding remote origin...")
    if not run_command("git remote add origin https://github.com/manideep395/QueryPilot-AI.git", "Add remote origin"):
        return False
    
    # Push to GitHub
    print("\n🚀 Pushing to GitHub...")
    if not run_command("git push -u origin main", "Push to GitHub"):
        return False
    
    print("\n" + "=" * 60)
    print("✅ Git setup completed successfully!")
    print("🚀 QueryPilot AI is now on GitHub!")
    print("📊 Repository: https://github.com/manideep395/QueryPilot-AI")
    print("=" * 60)
    
    return True

def show_git_info():
    """Show git repository information"""
    print("📊 QueryPilot AI - Git Information")
    print("=" * 60)
    
    # Show current directory
    current_dir = os.getcwd()
    print(f"📂 Current Directory: {current_dir}")
    
    # Check if git repository
    if os.path.exists(".git"):
        print("✅ Git repository initialized")
        
        # Show git status
        print("\n📊 Git Status:")
        run_command("git status", "Check git status")
        
        # Show git log
        print("\n📋 Git Log:")
        run_command("git log --oneline -5", "Show recent commits")
        
        # Show git remote
        print("\n🔗 Git Remotes:")
        run_command("git remote -v", "Show git remotes")
        
        # Show git branch
        print("\n🌿 Git Branches:")
        run_command("git branch -a", "Show git branches")
    else:
        print("❌ Git repository not initialized")
    
    print("=" * 60)

def main():
    """Main function"""
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "setup":
            setup_git_repository()
        elif command == "info":
            show_git_info()
        elif command == "status":
            run_command("git status", "Check git status")
        elif command == "push":
            run_command("git push origin main", "Push to GitHub")
        else:
            print("📋 Usage: python GIT_SETUP.py [setup|info|status|push]")
            print("  setup  - Set up git repository and push to GitHub")
            print("  info   - Show git repository information")
            print("  status - Check git status")
            print("  push   - Push to GitHub")
    else:
        print("🚀 QueryPilot AI - Git Setup Script")
        print("=" * 60)
        print("📋 Usage: python GIT_SETUP.py [setup|info|status|push]")
        print("  setup  - Set up git repository and push to GitHub")
        print("  info   - Show git repository information")
        print("  status - Check git status")
        print("  push   - Push to GitHub")
        print("\n🚀 Recommended: python GIT_SETUP.py setup")

if __name__ == "__main__":
    main()
