#!/usr/bin/env python3
"""
Run both the Flask web interface and SOAP service simultaneously.
This script starts both services for easy testing and development.
"""

import subprocess
import sys
import time
import threading
import os
from pathlib import Path

def run_service(script_name, port, service_name):
    """Run a service in a subprocess"""
    try:
        print(f"Starting {service_name} on port {port}...")
        process = subprocess.Popen([sys.executable, script_name], 
                                 stdout=subprocess.PIPE, 
                                 stderr=subprocess.PIPE,
                                 text=True)
        
        # Wait a moment for the service to start
        time.sleep(2)
        
        if process.poll() is None:
            print(f"✅ {service_name} started successfully on port {port}")
            return process
        else:
            stdout, stderr = process.communicate()
            print(f"❌ Failed to start {service_name}: {stderr}")
            return None
            
    except Exception as e:
        print(f"❌ Error starting {service_name}: {e}")
        return None

def monitor_process(process, service_name):
    """Monitor a process and print its output"""
    if process:
        try:
            while True:
                output = process.stdout.readline()
                if output:
                    print(f"[{service_name}] {output.strip()}")
                if process.poll() is not None:
                    break
        except KeyboardInterrupt:
            pass

def main():
    """Main function to run both services"""
    print("🚀 Eclipse Coffee Shop Services")
    print("=" * 40)
    
    # Check if required files exist
    required_files = ['soap_service.py', 'soap_server.py']
    for file in required_files:
        if not Path(file).exists():
            print(f"❌ Required file not found: {file}")
            sys.exit(1)
    
    # Start Flask web service
    flask_process = run_service('soap_service.py', 5000, 'Flask Web Interface')
    
    # Start SOAP service
    soap_process = run_service('soap_server.py', 8000, 'SOAP Service')
    
    if not flask_process or not soap_process:
        print("❌ Failed to start one or more services")
        sys.exit(1)
    
    print("\n" + "=" * 40)
    print("🎉 Both services are running!")
    print("\n📱 Web Interface: http://localhost:5000")
    print("🔗 SOAP WSDL: http://localhost:8000/?wsdl")
    print("🧪 Test Client: python test_soap_client.py")
    print("\nPress Ctrl+C to stop all services")
    print("=" * 40)
    
    try:
        # Monitor both processes
        flask_thread = threading.Thread(target=monitor_process, args=(flask_process, 'Flask'))
        soap_thread = threading.Thread(target=monitor_process, args=(soap_process, 'SOAP'))
        
        flask_thread.daemon = True
        soap_thread.daemon = True
        
        flask_thread.start()
        soap_thread.start()
        
        # Keep main thread alive
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n🛑 Stopping services...")
        
        if flask_process:
            flask_process.terminate()
            print("✅ Flask service stopped")
        
        if soap_process:
            soap_process.terminate()
            print("✅ SOAP service stopped")
        
        print("👋 All services stopped. Goodbye!")

if __name__ == "__main__":
    main() 