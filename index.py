import json
import os
from datetime import datetime
from http.server import BaseHTTPRequestHandler
import requests

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        path = self.path
        
        if path == '/health':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            response = {
                'status': 'healthy',
                'timestamp': datetime.now().isoformat(),
                'services': {
                    'database': 'configured' if os.getenv('DATABASE_URL') else 'missing',
                    'vector_db': 'configured' if os.getenv('UPSTASH_VECTOR_REST_URL') else 'missing',
                    'groq_api': 'configured' if os.getenv('GROQ_API_KEY') else 'missing'
                }
            }
            
            self.wfile.write(json.dumps(response).encode())
            return
        
        elif path == '/api/test':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            response = {
                'message': "Regine's Digital Twin API is working!",
                'timestamp': datetime.now().isoformat(),
                'version': '4.0',
                'status': 'success'
            }
            
            self.wfile.write(json.dumps(response).encode())
            return
        
        else:
            # Home page
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            response = {
                'name': "Regine's Professional Digital Twin",
                'description': 'AI-powered assistant showcasing 13+ years of Business Analysis expertise',
                'endpoints': {
                    'health': '/health',
                    'test': '/api/test',
                    'query': '/api/query (POST)'
                },
                'version': '4.0'
            }
            
            self.wfile.write(json.dumps(response).encode())
            return
    
    def do_POST(self):
        if self.path == '/api/query':
            # Read request body
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            
            try:
                data = json.loads(body.decode())
                query = data.get('query', '').strip()
                
                if not query:
                    self.send_response(400)
                    self.send_header('Content-Type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    self.wfile.write(json.dumps({'error': 'Query is required'}).encode())
                    return
                
                # Simple response for now - we can add AI later once basic deployment works
                response = {
                    'content': f"Thank you for asking: '{query}'. I'm Regine Aniban, a Business Analyst with 13+ years of experience. I specialize in requirements analysis, stakeholder management, and digital transformation projects.",
                    'metadata': {
                        'response_time': 0.5,
                        'version': '4.0',
                        'query_received': query
                    }
                }
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps(response).encode())
                return
                
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({'error': 'Internal server error'}).encode())
                return
        
        else:
            self.send_response(404)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({'error': 'Not Found'}).encode())
            return
    
    def do_OPTIONS(self):
        # Handle CORS preflight
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        return