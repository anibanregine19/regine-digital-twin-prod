#!/usr/bin/env python3
"""
Vercel-Compatible Digital Twin API
Fixed for Vercel Python runtime
"""

import json
import os
import logging
import time
import psycopg2
from datetime import datetime
from typing import List, Dict, Any, Optional
import requests

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnhancedDigitalTwin:
    def __init__(self):
        self.db_url = os.getenv('DATABASE_URL')
        self.upstash_url = os.getenv('UPSTASH_VECTOR_REST_URL')
        self.upstash_token = os.getenv('UPSTASH_VECTOR_REST_TOKEN')
        self.groq_api_key = os.getenv('GROQ_API_KEY')
        self._db_initialized = False
    
    def ensure_database_setup(self):
        """Lazy database initialization"""
        if self._db_initialized or not self.db_url:
            return
            
        try:
            conn = psycopg2.connect(self.db_url)
            cur = conn.cursor()
            
            # Create chat_logs table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS chat_logs (
                    id SERIAL PRIMARY KEY,
                    query TEXT NOT NULL,
                    response TEXT NOT NULL,
                    response_time FLOAT,
                    vector_hits INTEGER,
                    query_category VARCHAR(50),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    user_ip VARCHAR(45),
                    user_agent TEXT
                );
            """)
            
            # Create popular_questions table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS popular_questions (
                    id SERIAL PRIMARY KEY,
                    question_type VARCHAR(100),
                    question_text TEXT,
                    ask_count INTEGER DEFAULT 1,
                    avg_response_time FLOAT,
                    last_asked TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            
            conn.commit()
            cur.close()
            conn.close()
            self._db_initialized = True
            logger.info("Database tables created successfully")
            
        except Exception as e:
            logger.error(f"Database setup error: {e}")
    
    def vector_search(self, query: str, limit: int = 5) -> List[Dict]:
        """Search Upstash Vector database"""
        try:
            if not self.upstash_url or not self.upstash_token:
                return []
                
            headers = {
                'Authorization': f'Bearer {self.upstash_token}',
                'Content-Type': 'application/json'
            }
            
            data = {
                'data': query,
                'topK': limit,
                'includeVectors': False,
                'includeMetadata': True
            }
            
            response = requests.post(
                f'{self.upstash_url}/query',
                headers=headers,
                json=data,
                timeout=10
            )
            
            if response.status_code == 200:
                results = response.json()
                return results.get('result', [])
            return []
                
        except Exception as e:
            logger.error(f"Vector search error: {e}")
            return []
    
    def generate_response(self, query: str, context: str) -> str:
        """Generate response using Groq"""
        try:
            if not self.groq_api_key:
                return "I apologize, but the AI service is not properly configured."
                
            headers = {
                'Authorization': f'Bearer {self.groq_api_key}',
                'Content-Type': 'application/json'
            }
            
            prompt = f"""Based on the following context about Regine Aniban, please answer the user's question professionally and comprehensively.

Context:
{context}

Question: {query}

Please provide a detailed, professional response that directly addresses the question using the context provided."""

            data = {
                'model': 'llama-3.1-8b-instant',
                'messages': [{'role': 'user', 'content': prompt}],
                'max_tokens': 1000,
                'temperature': 0.7
            }
            
            response = requests.post(
                'https://api.groq.com/openai/v1/chat/completions',
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content']
            return "I apologize, but I'm having trouble generating a response right now."
                
        except Exception as e:
            logger.error(f"Response generation error: {e}")
            return "I apologize, but I'm experiencing technical difficulties."
    
    def categorize_query(self, query: str) -> str:
        """Categorize user query"""
        query_lower = query.lower()
        
        if any(word in query_lower for word in ['competenc', 'skill', 'abilit']):
            return 'competencies'
        elif any(word in query_lower for word in ['experience', 'work', 'job', 'asurion', 'etisalat']):
            return 'experience'
        elif any(word in query_lower for word in ['stakeholder', 'manage', 'leadership']):
            return 'stakeholder_management'
        elif any(word in query_lower for word in ['methodolog', 'framework', 'approach']):
            return 'methodologies'
        elif any(word in query_lower for word in ['achievement', 'award', 'accomplish']):
            return 'achievements'
        return 'general'
    
    def answer_query(self, query: str) -> Dict[str, Any]:
        """Main query answering function"""
        start_time = time.time()
        
        try:
            # Search vector database
            search_results = self.vector_search(query)
            
            # Build context
            context_parts = []
            for result in search_results[:3]:
                if result.get('metadata'):
                    context_parts.append(result['metadata'].get('text', ''))
            
            context = '\n\n'.join(context_parts) if context_parts else "No specific context found."
            
            # Generate response
            response = self.generate_response(query, context)
            response_time = time.time() - start_time
            
            return {
                'content': response,
                'metadata': {
                    'response_time': round(response_time, 2),
                    'vector_hits': len(search_results),
                    'category': self.categorize_query(query),
                    'context_used': len(context_parts)
                }
            }
            
        except Exception as e:
            logger.error(f"Query processing error: {e}")
            return {
                'content': "I apologize, but I'm experiencing technical difficulties.",
                'metadata': {'error': str(e)}
            }

# Global instance
digital_twin = EnhancedDigitalTwin()

def handler(request, context):
    """Vercel serverless function handler"""
    try:
        # Parse request
        method = request.get('httpMethod', 'GET')
        path = request.get('path', '/')
        query_params = request.get('queryStringParameters') or {}
        headers = request.get('headers', {})
        body = request.get('body', '')
        
        # Parse JSON body for POST requests
        json_body = {}
        if method == 'POST' and body:
            try:
                json_body = json.loads(body)
            except:
                pass
        
        # Route handling
        if path == '/health':
            # Health check
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
                    'Access-Control-Allow-Headers': 'Content-Type'
                },
                'body': json.dumps({
                    'status': 'healthy',
                    'timestamp': datetime.now().isoformat(),
                    'services': {
                        'database': 'configured' if digital_twin.db_url else 'not_configured',
                        'vector_db': 'configured' if digital_twin.upstash_url else 'not_configured',
                        'groq_api': 'configured' if digital_twin.groq_api_key else 'not_configured'
                    }
                })
            }
        
        elif path == '/api/test':
            # Test endpoint
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'message': "Regine's Digital Twin API is working!",
                    'timestamp': datetime.now().isoformat(),
                    'version': '3.0',
                    'features': ['AI Chat', 'Analytics', 'Vector Search']
                })
            }
        
        elif path == '/api/query' and method == 'POST':
            # Query endpoint
            query_text = json_body.get('query', '').strip()
            
            if not query_text:
                return {
                    'statusCode': 400,
                    'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                    'body': json.dumps({'error': 'Query is required'})
                }
            
            result = digital_twin.answer_query(query_text)
            
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps(result)
            }
        
        elif path == '/' or path == '':
            # Home endpoint
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({
                    'name': "Regine's Professional Digital Twin",
                    'description': 'AI-powered assistant showcasing 13+ years of Business Analysis expertise',
                    'endpoints': {
                        'health': '/health',
                        'test': '/api/test',
                        'query': '/api/query (POST)'
                    },
                    'version': '3.0'
                })
            }
        
        else:
            # 404 Not Found
            return {
                'statusCode': 404,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'error': 'Not Found'})
            }
    
    except Exception as e:
        logger.error(f"Handler error: {e}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': 'Internal server error'})
        }
