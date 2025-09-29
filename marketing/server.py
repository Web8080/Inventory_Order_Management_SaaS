#!/usr/bin/env python3
"""
Simple HTTP server for the marketing website
"""

import http.server
import socketserver
import os
import sys
from urllib.parse import urlparse

class MarketingHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=os.path.dirname(os.path.abspath(__file__)), **kwargs)
    
    def do_GET(self):
        # Parse the URL
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        # Default to index.html for root path
        if path == '/':
            path = '/index.html'
        
        # Set the path for the parent class
        self.path = path
        return super().do_GET()
    
    def end_headers(self):
        # Add CORS headers
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

def main():
    PORT = 3000
    
    # Check if port is available
    try:
        with socketserver.TCPServer(("", PORT), MarketingHTTPRequestHandler) as httpd:
            print(f"🚀 Marketing website server running at http://localhost:{PORT}")
            print(f"📁 Serving files from: {os.path.dirname(os.path.abspath(__file__))}")
            print("Press Ctrl+C to stop the server")
            httpd.serve_forever()
    except OSError as e:
        if e.errno == 48:  # Address already in use
            print(f"❌ Port {PORT} is already in use. Trying port {PORT + 1}")
            PORT += 1
            with socketserver.TCPServer(("", PORT), MarketingHTTPRequestHandler) as httpd:
                print(f"🚀 Marketing website server running at http://localhost:{PORT}")
                print(f"📁 Serving files from: {os.path.dirname(os.path.abspath(__file__))}")
                print("Press Ctrl+C to stop the server")
                httpd.serve_forever()
        else:
            print(f"❌ Error starting server: {e}")
            sys.exit(1)

if __name__ == "__main__":
    main()
