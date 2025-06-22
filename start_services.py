#!/usr/bin/env python3
"""
Startup script for Eclipse Coffee Shop Services
This script starts both the SOAP server and Flask application
"""

import subprocess
import time
import sys
import os
from pathlib import Path

def start_soap_server():
    """Start the SOAP server"""
    print("Starting SOAP server...")
    try:
        # Start SOAP server in background
        soap_process = subprocess.Popen([
            sys.executable, "soap_server_complete.py"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait a moment for server to start
        time.sleep(3)
        
        if soap_process.poll() is None:
            print("✅ SOAP server started successfully")
            return soap_process
        else:
            print("❌ Failed to start SOAP server")
            return None
            
    except Exception as e:
        print(f"❌ Error starting SOAP server: {e}")
        return None

def start_flask_app():
    """Start the Flask application"""
    print("Starting Flask application...")
    try:
        # Start Flask app
        flask_process = subprocess.Popen([
            sys.executable, "app.py"
        ])
        
        print("✅ Flask application started successfully")
        print("🌐 Open your browser and go to: http://localhost:5000")
        print("📋 Available routes:")
        print("   - Home: http://localhost:5000/")
        print("   - Guest Login: http://localhost:5000/guest-login")
        print("   - Member Login: http://localhost:5000/member-login")
        print("   - Menu: http://localhost:5000/menu (requires login)")
        print("   - Status: http://localhost:5000/status (requires login)")
        
        return flask_process
        
    except Exception as e:
        print(f"❌ Error starting Flask app: {e}")
        return None

def main():
    """Main function to start both services"""
    print("🚀 Starting Eclipse Coffee Shop Services...")
    print("=" * 50)
    
    # Check if we're in the correct directory
    if not os.path.exists("app.py"):
        print("❌ Error: Please run this script from the eclipse_coffee_soap_service directory")
        print("   Current directory:", os.getcwd())
        print("   Expected files: app.py, soap_server_complete.py")
        return
    
    # Start SOAP server
    soap_process = start_soap_server()
    if not soap_process:
        print("❌ Cannot start Flask app without SOAP server")
        return
    
    # Start Flask app
    flask_process = start_flask_app()
    if not flask_process:
        print("❌ Failed to start Flask app")
        soap_process.terminate()
        return
    
    print("=" * 50)
    print("🎉 Both services are running!")
    print("Press Ctrl+C to stop both services")
    
    try:
        # Keep the script running
        flask_process.wait()
    except KeyboardInterrupt:
        print("\n🛑 Stopping services...")
        soap_process.terminate()
        flask_process.terminate()
        print("✅ Services stopped")

if __name__ == "__main__":
    main() 