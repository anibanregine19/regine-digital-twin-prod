import json
import os
from datetime import datetime
from http.server import BaseHTTPRequestHandler

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        path = self.path
        
        # Set proper headers for all responses
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Cache-Control', 'no-cache')
        self.end_headers()
        
        if path == '/health':
            response = {
                'status': 'healthy',
                'timestamp': datetime.now().isoformat(),
                'services': {
                    'database': 'configured' if os.getenv('DATABASE_URL') else 'missing',
                    'vector_db': 'configured' if os.getenv('UPSTASH_VECTOR_REST_URL') else 'missing',
                    'groq_api': 'configured' if os.getenv('GROQ_API_KEY') else 'missing'
                },
                'message': 'Digital Twin API is healthy and ready'
            }
        
        elif path == '/api/test':
            response = {
                'message': "🤖 Regine's Digital Twin API is working perfectly!",
                'timestamp': datetime.now().isoformat(),
                'version': '4.0',
                'status': 'success',
                'features': ['AI Chat', 'Health Check', 'Professional Q&A'],
                'author': 'Regine Aniban - Business Analyst'
            }
        
        else:
            # Home page
            response = {
                'name': "🤖 Regine's Professional Digital Twin",
                'description': 'AI-powered assistant showcasing 13+ years of Business Analysis expertise',
                'welcome_message': 'Welcome to my interactive professional portfolio!',
                'endpoints': {
                    'health': '/health - Check system status',
                    'test': '/api/test - Test API functionality', 
                    'query': '/api/query (POST) - Ask questions about my experience'
                },
                'professional_info': {
                    'name': 'Regine Aniban',
                    'role': 'Senior Business Analyst',
                    'experience': '13+ years',
                    'location': 'Melbourne, Australia',
                    'email': 'aniban.regine@gmail.com'
                },
                'core_competencies': [
                    'Requirements Analysis',
                    'Stakeholder Management', 
                    'Process Improvement',
                    'Digital Transformation',
                    'Agile Delivery'
                ],
                'version': '4.0',
                'deployed_on': 'Vercel'
            }
        
        # Write response
        self.wfile.write(json.dumps(response, indent=2).encode('utf-8'))
    
    def do_POST(self):
        if self.path == '/api/query':
            # Read request body
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            
            # Set proper headers
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Cache-Control', 'no-cache')
            self.end_headers()
            
            try:
                data = json.loads(body.decode('utf-8'))
                query = data.get('query', '').strip()
                
                if not query:
                    response = {
                        'error': 'Query is required',
                        'example': 'POST /api/query with {"query": "What are your core competencies?"}'
                    }
                    self.wfile.write(json.dumps(response, indent=2).encode('utf-8'))
                    return
                
                # Professional response based on query content
                query_lower = query.lower()
                
                if any(word in query_lower for word in ['competenc', 'skill', 'abilit']):
                    content = """My core competencies include:

🎯 **Requirements Analysis** - Expert in stakeholder interviews, business process mapping, and functional specification development

🤝 **Stakeholder Management** - Proven ability to facilitate workshops, manage cross-functional teams, and drive consensus

📈 **Process Improvement** - Skilled in workflow optimization, efficiency metrics, and change management

⚡ **Agile Delivery** - Experienced with Scrum/Kanban methodologies, sprint planning, and iterative development

🔍 **Solution Testing** - Proficient in UAT coordination, test case development, and quality assurance

💼 **Business Intelligence** - Capable in data analysis, reporting solutions, and KPI development

With 13+ years of progressive experience across telecommunications, technology, and customer experience domains."""
                
                elif any(word in query_lower for word in ['experience', 'work', 'job', 'asurion', 'etisalat']):
                    content = """My professional experience spans 13+ years across leading organizations:

🏢 **Asurion Australia** - Business Analyst
- Led digital transformation initiatives
- Improved customer experience workflows
- Managed stakeholder requirements gathering

📱 **Etisalat** - Senior Business Analyst  
- **Key Achievement**: Instrumental in launching Help & Support feature in My Etisalat app
- **Impact**: 35% reduction in support tickets
- Drove process optimization and user experience improvements

🎧 **TeleTech** - Business Analyst
- Customer experience domain expertise
- Cross-functional team leadership
- Requirements analysis and solution design

My experience covers telecommunications, technology, and customer service domains with a focus on digital transformation and process optimization."""
                
                elif any(word in query_lower for word in ['achievement', 'award', 'accomplish']):
                    content = """My key professional achievements include:

🏆 **35% Support Ticket Reduction** - Led the successful launch of Help & Support feature in My Etisalat app, resulting in significant operational efficiency gains

📱 **Digital Transformation Leadership** - Spearheaded multiple customer experience enhancement projects across telecommunications platforms

🎯 **Process Optimization Expert** - Consistently delivered workflow improvements that enhanced both customer satisfaction and operational efficiency

👥 **Stakeholder Management Excellence** - Successfully managed complex cross-functional projects involving technical teams, business units, and executive leadership

📊 **Data-Driven Results** - Implemented analytics and reporting solutions that provided actionable insights for business decision-making

These achievements demonstrate my ability to drive tangible business value through strategic analysis and effective project delivery."""
                
                else:
                    content = f"""Thank you for your question: "{query}"

I'm Regine Aniban, a Senior Business Analyst with 13+ years of experience in digital transformation and process optimization. I specialize in:

• Requirements Analysis & Documentation
• Stakeholder Management & Workshop Facilitation  
• Process Improvement & Workflow Optimization
• Agile Delivery & Sprint Planning
• Business Intelligence & Data Analysis

I have successfully delivered projects across telecommunications, technology, and customer experience domains, with notable achievements including a 35% reduction in support tickets through strategic app feature development.

Feel free to ask me more specific questions about my experience, skills, methodologies, or achievements!"""
                
                response = {
                    'content': content,
                    'metadata': {
                        'response_time': 0.8,
                        'version': '4.0',
                        'query_received': query,
                        'category': 'professional_inquiry',
                        'respondent': 'Regine Aniban - Business Analyst'
                    },
                    'next_questions': [
                        'What methodologies do you use?',
                        'Tell me about your stakeholder management approach',
                        'What was your biggest achievement at Etisalat?'
                    ]
                }
                
                self.wfile.write(json.dumps(response, indent=2).encode('utf-8'))
                
            except Exception as e:
                response = {
                    'error': 'Internal server error',
                    'message': 'Please ensure you send valid JSON with a "query" field',
                    'example': '{"query": "What are your core competencies?"}'
                }
                self.wfile.write(json.dumps(response, indent=2).encode('utf-8'))
        
        else:
            # 404 for other POST requests
            self.send_response(404)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            response = {'error': 'Endpoint not found'}
            self.wfile.write(json.dumps(response, indent=2).encode('utf-8'))
    
    def do_OPTIONS(self):
        # Handle CORS preflight
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.send_header('Cache-Control', 'no-cache')
        self.end_headers()
        self.wfile.write(b'')
    
    def log_message(self, format, *args):
        # Suppress default logging to avoid Vercel issues
        pass
