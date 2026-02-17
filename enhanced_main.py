#!/usr/bin/env python3
"""
Enhanced NeuroSQL Main Application
Features: AI/ML Integration, Multi-DB Support, Performance Optimization, Security
"""

import sys
import argparse
from core.enhanced_orchestrator import EnhancedOrchestrator
from core.security_manager import security_manager, UserRole
from web.api import app
import uvicorn

def main():
    parser = argparse.ArgumentParser(description="Enhanced NeuroSQL - AI-powered Natural Language to SQL")
    parser.add_argument("--database", "-d", default="database.db", help="Default database path")
    parser.add_argument("--web", "-w", action="store_true", help="Start web server")
    parser.add_argument("--port", "-p", type=int, default=8000, help="Web server port")
    parser.add_argument("--host", default="0.0.0.0", help="Web server host")
    parser.add_argument("--create-user", action="store_true", help="Create a new user")
    parser.add_argument("--username", help="Username for new user")
    parser.add_argument("--email", help="Email for new user")
    parser.add_argument("--password", help="Password for new user")
    parser.add_argument("--role", choices=["admin", "analyst", "viewer", "guest"], default="analyst", help="Role for new user")
    
    args = parser.parse_args()
    
    # Create user if requested
    if args.create_user:
        if not all([args.username, args.email, args.password]):
            print("❌ Error: --username, --email, and --password required when creating user")
            sys.exit(1)
        
        role_map = {
            "admin": UserRole.ADMIN,
            "analyst": UserRole.ANALYST,
            "viewer": UserRole.VIEWER,
            "guest": UserRole.GUEST
        }
        
        success, message = security_manager.create_user(
            args.username, args.email, args.password, role_map[args.role]
        )
        
        if success:
            print(f"✅ User created successfully: {args.username}")
            print(f"📧 Email: {args.email}")
            print(f"🔑 Role: {args.role}")
        else:
            print(f"❌ Failed to create user: {message}")
        return
    
    # Start web server if requested
    if args.web:
        print("🚀 Starting Enhanced NeuroSQL Web Server")
        print(f"🌐 Server: http://{args.host}:{args.port}")
        print("📊 Dashboard: Available at root URL")
        print("🔐 API Documentation: http://{args.host}:{args.port}/docs")
        
        # Initialize orchestrator
        orchestrator = EnhancedOrchestrator(args.database)
        
        # Store orchestrator in app state for API access
        app.state.orchestrator = orchestrator
        
        uvicorn.run(app, host=args.host, port=args.port)
        return
    
    # Interactive CLI mode
    print("=== Enhanced NeuroSQL - AI-powered NL-to-SQL ===")
    print("Features: AI/ML • Multi-DB • Performance • Security")
    print()
    
    # Initialize enhanced orchestrator
    system = EnhancedOrchestrator(args.database)
    
    # Show system status
    status = system.get_system_status()
    print("🔧 System Status:")
    for key, value in status.items():
        if isinstance(value, dict):
            print(f"  {key.replace('_', ' ').title()}:")
            for sub_key, sub_value in value.items():
                print(f"    {sub_key}: {sub_value}")
        elif isinstance(value, list):
            print(f"  {key.replace('_', ' ').title()}: {', '.join(value)}")
        else:
            print(f"  {key.replace('_', ' ').title()}: {value}")
    print()
    
    # Demo authentication (in production, use proper login)
    print("🔐 Authentication Demo:")
    print("Default admin user: admin / admin123")
    print("Creating a demo session...")
    
    # Authenticate as admin for demo
    token, auth_message = security_manager.authenticate_user("admin", "admin123")
    if token:
        print(f"✅ {auth_message}")
        current_user_id = "admin"
    else:
        print(f"❌ {auth_message}")
        current_user_id = None
    
    print()
    print("💡 Available Commands:")
    print("  • Natural language queries (e.g., 'Show me all students')")
    print("  • 'show tables' - List all tables")
    print("  • 'describe [table]' - Show table structure")
    print("  • 'load [database]' - Switch database")
    print("  • 'performance report' - Show performance metrics")
    print("  • 'optimization suggestions' - Get optimization tips")
    print("  • 'exit' - Quit application")
    print()
    
    # Main interaction loop
    while True:
        try:
            user_input = input("🧠 NeuroSQL> ").strip()
            
            if user_input.lower() in ["exit", "quit", "q"]:
                print("👋 Goodbye!")
                break
            
            if not user_input:
                continue
            
            # Process query with enhanced features
            result = system.handle_query(user_input, user_id=current_user_id)
            
            # Display results
            print("\n" + "="*60)
            
            if result.get("error"):
                print(f"❌ Error: {result['explanation']}")
            else:
                print(f"🎯 Explanation: {result['explanation']}")
                print(f"🔢 Confidence: {result['confidence']:.1%}")
                print(f"⏱️  Execution Time: {result['execution_time']:.3f}s")
                
                if result.get("sql"):
                    print(f"🔍 SQL: {result['sql']}")
                
                # Show AI enhancements
                if "ai_enhancements" in result:
                    ai_info = result["ai_enhancements"]
                    print(f"🤖 AI Method: {ai_info['nlu_method']}")
                    if ai_info.get("temporal"):
                        print(f"⏰ Temporal Intent: {ai_info['temporal']}")
                    if ai_info.get("comparative"):
                        print(f"📊 Comparative Intent: {ai_info['comparative']}")
                
                # Show performance metrics
                if "performance_metrics" in result:
                    perf = result["performance_metrics"]
                    print(f"📈 Performance Score: {perf['performance_score']:.1f}/100")
                    if perf.get("optimizations_applied"):
                        print(f"⚡ Optimizations: {', '.join(perf['optimizations_applied'])}")
                
                # Show results
                if result.get("result"):
                    print(f"📋 Results ({len(result['result'])} rows):")
                    if isinstance(result['result'], list) and result['result']:
                        # Show first few rows as preview
                        for i, row in enumerate(result['result'][:5]):
                            print(f"  {i+1}: {row}")
                        if len(result['result']) > 5:
                            print(f"  ... and {len(result['result']) - 5} more rows")
                    else:
                        print(f"  {result['result']}")
                elif result.get("result") is None:
                    print("📊 No data returned")
            
            print("="*60 + "\n")
            
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            continue

if __name__ == "__main__":
    main()
