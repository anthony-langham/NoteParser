#!/usr/bin/env python3
"""
Local development server runner for Heidi MCP Server.

This script provides an easy way to run the MCP server locally for development and testing.
"""

import sys
import os
import logging
from pathlib import Path

# Add the backend directory to the path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

def check_environment():
    """Check if the development environment is properly set up."""
    print("🔍 Checking local development environment...")
    
    # Check data files
    data_dir = backend_dir / "mcp_server" / "data"
    conditions_file = data_dir / "conditions.json"
    guidelines_file = data_dir / "guidelines.json"
    
    print(f"📁 Data directory: {data_dir}")
    print(f"  ✅ Conditions file: {conditions_file} (exists: {conditions_file.exists()})")
    print(f"  ✅ Guidelines file: {guidelines_file} (exists: {guidelines_file.exists()})")
    
    if not conditions_file.exists() or not guidelines_file.exists():
        print("❌ Error: Required data files are missing!")
        return False
    
    # Check environment file
    env_file = backend_dir / ".env"
    print(f"🔧 Environment file: {env_file} (exists: {env_file.exists()})")
    
    # Check Python dependencies
    try:
        import mcp
        import pydantic
        import pytest
        print("✅ Python dependencies are installed")
    except ImportError as e:
        print(f"❌ Error: Missing Python dependency: {e}")
        print("💡 Run: pip3 install -r requirements.txt")
        return False
    
    print("✅ Local development environment is ready!")
    return True

def run_tests():
    """Run the test suite to verify functionality."""
    print("\n🧪 Running tests...")
    
    try:
        from test_runner import main as test_main
        import asyncio
        
        print("Running end-to-end workflow test...")
        asyncio.run(test_main())
        print("✅ All tests passed!")
        return True
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def run_server():
    """Run the MCP server."""
    print("\n🚀 Starting Heidi Clinical Decision Support MCP Server...")
    print("📝 Server will handle clinical note parsing, condition identification,")
    print("   dose calculation, and treatment plan generation.")
    print("\n🔗 Server is running in MCP mode - connect via MCP client")
    print("⏹️  Press Ctrl+C to stop the server")
    print("-" * 60)
    
    try:
        from mcp_server.server import main
        main()
    except KeyboardInterrupt:
        print("\n\n⏹️  Server stopped by user")
    except Exception as e:
        print(f"\n❌ Server error: {e}")
        return False
    
    return True

def main():
    """Main function for local development."""
    print("=" * 60)
    print("🏥 Heidi Clinical Decision Support - Local Development")
    print("=" * 60)
    
    # Check environment
    if not check_environment():
        print("\n❌ Environment check failed. Please fix the issues above.")
        sys.exit(1)
    
    # Ask user what they want to do
    print("\n🎯 What would you like to do?")
    print("1. Run tests only")
    print("2. Run MCP server")
    print("3. Run tests then server")
    
    try:
        choice = input("\nEnter your choice (1-3): ").strip()
        
        if choice == "1":
            if not run_tests():
                sys.exit(1)
        elif choice == "2":
            run_server()
        elif choice == "3":
            if run_tests():
                input("\n✅ Tests passed! Press Enter to start the server...")
                run_server()
            else:
                sys.exit(1)
        else:
            print("Invalid choice. Running tests by default...")
            run_tests()
            
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
        sys.exit(0)

if __name__ == "__main__":
    main()