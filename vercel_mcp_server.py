#!/usr/bin/env python3
"""
Enhanced Digital Twin MCP Server for Vercel + Neon PostgreSQL
Standalone version - no external imports
"""

import json
import os
import logging
import time
import psycopg2
from datetime import datetime
from typing import List, Dict, Any, Optional
from functools import lru_cache
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import requests

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Create Flask app
app = Flask(__name__)
CORS(app, origins=["*"])

class EnhancedDigitalTwin:
    def __init__(self):
        self.db_url = os.getenv('DATABASE_URL')
        self.upstash_url = os.getenv('UPSTASH_VECTOR_REST_URL')
        self.upstash_token = os.getenv('UPSTASH_VECTOR_REST_TOKEN')
        self.groq_api_key = os.getenv('GROQ_API_KEY')
        self.setup_database()
    
    def setup_database(self):
        """Create PostgreSQL tables for analytics"""
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
            logger.info("Database tables created successfully")
            
        except Exception as e:
            logger.error(f"Database setup error: {e}")
    
    def vector_search(self, query: str, limit: int = 5) -> List[Dict]:
        """Search Upstash Vector database"""
        try:
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
            else:
                logger.error(f"Vector search failed: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Vector search error: {e}")
            return []
    
    def generate_response(self, query: str, context: str) -> str:
        """Generate response using Groq"""
        try:
            headers = {
                'Authorization': f'Bearer {self.groq_api_key}',
                'Content-Type': 'application/json'
            }
            
            prompt = f"""Based on the following context about Regine Aniban, please answer the user's question professionally and comprehensively.

Context:
{context}

Question: {query}

Please provide a detailed, professional response that directly addresses the question using the context provided. If the context doesn't contain enough information, provide a helpful response based on what is available."""

            data = {
                'model': 'llama-3.1-8b-instant',
                'messages': [
                    {
                        'role': 'user',
                        'content': prompt
                    }
                ],
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
            else:
                logger.error(f"Groq API failed: {response.status_code}")
                return "I apologize, but I'm having trouble generating a response right now. Please try again later."
                
        except Exception as e:
            logger.error(f"Response generation error: {e}")
            return "I apologize, but I'm experiencing technical difficulties. Please try again later."
    
    def categorize_query(self, query: str) -> str:
        """Categorize the user query"""
        query_lower = query.lower()
        
        if any(word in query_lower for word in ['competenc', 'skill', 'abilit', 'strength']):
            return 'competencies'
        elif any(word in query_lower for word in ['experience', 'work', 'job', 'role', 'position', 'asurion', 'etisalat']):
            return 'experience'
        elif any(word in query_lower for word in ['stakeholder', 'manage', 'leadership', 'team']):
            return 'stakeholder_management'
        elif any(word in query_lower for word in ['methodolog', 'framework', 'approach', 'process']):
            return 'methodologies'
        elif any(word in query_lower for word in ['achievement', 'award', 'accomplish', 'success']):
            return 'achievements'
        else:
            return 'general'
    
    def log_chat(self, query: str, response: str, response_time: float, vector_hits: int, user_ip: str = None, user_agent: str = None):
        """Log chat interaction to PostgreSQL"""
        try:
            conn = psycopg2.connect(self.db_url)
            cur = conn.cursor()
            
            category = self.categorize_query(query)
            
            cur.execute("""
                INSERT INTO chat_logs (query, response, response_time, vector_hits, query_category, user_ip, user_agent)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (query, response, response_time, vector_hits, category, user_ip, user_agent))
            
            conn.commit()
            cur.close()
            conn.close()
            
        except Exception as e:
            logger.error(f"Chat logging error: {e}")
    
    def answer_query(self, query: str, user_ip: str = None, user_agent: str = None) -> Dict[str, Any]:
        """Main query answering function"""
        start_time = time.time()
        
        try:
            # Search vector database
            search_results = self.vector_search(query)
            
            # Build context from search results
            context_parts = []
            for result in search_results[:3]:  # Use top 3 results
                if result.get('metadata'):
                    context_parts.append(result['metadata'].get('text', ''))
            
            context = '\n\n'.join(context_parts) if context_parts else "No specific context found."
            
            # Generate response
            response = self.generate_response(query, context)
            
            response_time = time.time() - start_time
            vector_hits = len(search_results)
            
            # Log the interaction
            self.log_chat(query, response, response_time, vector_hits, user_ip, user_agent)
            
            return {
                'content': response,
                'metadata': {
                    'response_time': round(response_time, 2),
                    'vector_hits': vector_hits,
                    'category': self.categorize_query(query),
                    'context_used': len(context_parts)
                }
            }
            
        except Exception as e:
            logger.error(f"Query processing error: {e}")
            return {
                'content': "I apologize, but I'm experiencing technical difficulties. Please try again later.",
                'metadata': {
                    'error': str(e),
                    'response_time': time.time() - start_time
                }
            }
    
    def get_analytics(self) -> Dict[str, Any]:
        """Get chat analytics"""
        try:
            conn = psycopg2.connect(self.db_url)
            cur = conn.cursor()
            
            # Total chats
            cur.execute("SELECT COUNT(*) FROM chat_logs")
            total_chats = cur.fetchone()[0]
            
            # Average response time
            cur.execute("SELECT AVG(response_time) FROM chat_logs")
            avg_response_time = cur.fetchone()[0] or 0
            
            # Popular categories
            cur.execute("""
                SELECT query_category, COUNT(*) as count 
                FROM chat_logs 
                GROUP BY query_category 
                ORDER BY count DESC 
                LIMIT 5
            """)
            popular_categories = cur.fetchall()
            
            # Recent chats
            cur.execute("""
                SELECT query, created_at 
                FROM chat_logs 
                ORDER BY created_at DESC 
                LIMIT 10
            """)
            recent_chats = cur.fetchall()
            
            cur.close()
            conn.close()
            
            return {
                'total_chats': total_chats,
                'avg_response_time': round(avg_response_time, 2),
                'popular_categories': [{'category': cat, 'count': count} for cat, count in popular_categories],
                'recent_chats': [{'query': query, 'timestamp': timestamp.isoformat()} for query, timestamp in recent_chats]
            }
            
        except Exception as e:
            logger.error(f"Analytics error: {e}")
            return {'error': str(e)}

# Initialize the enhanced digital twin
digital_twin = EnhancedDigitalTwin()

# Flask routes
@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    try:
        # Test database connection
        conn = psycopg2.connect(digital_twin.db_url)
        conn.close()
        db_status = "connected"
    except:
        db_status = "error"
    
    # Test Upstash connection
    try:
        headers = {'Authorization': f'Bearer {digital_twin.upstash_token}'}
        response = requests.get(f'{digital_twin.upstash_url}/info', headers=headers, timeout=5)
        upstash_status = "connected" if response.status_code == 200 else "error"
    except:
        upstash_status = "error"
    
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'services': {
            'database': db_status,
            'vector_db': upstash_status,
            'groq_api': 'configured' if digital_twin.groq_api_key else 'missing'
        }
    })

@app.route('/api/test', methods=['GET'])
def test():
    """Quick test endpoint"""
    return jsonify({
        'message': "Regine's Digital Twin API is working!",
        'timestamp': datetime.now().isoformat(),
        'version': '2.0',
        'features': ['AI Chat', 'Analytics', 'Vector Search']
    })

@app.route('/api/query', methods=['POST'])
def query():
    """Main query endpoint"""
    try:
        data = request.get_json()
        query_text = data.get('query', '').strip()
        
        if not query_text:
            return jsonify({'error': 'Query is required'}), 400
        
        user_ip = request.remote_addr
        user_agent = request.headers.get('User-Agent')
        
        result = digital_twin.answer_query(query_text, user_ip, user_agent)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Query endpoint error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/analytics', methods=['GET'])
def analytics():
    """Analytics endpoint"""
    try:
        data = digital_twin.get_analytics()
        return jsonify(data)
    except Exception as e:
        logger.error(f"Analytics endpoint error: {e}")
        return jsonify({'error': 'Analytics unavailable'}), 500

@app.route('/', methods=['GET'])
def home():
    """Home endpoint"""
    return jsonify({
        'name': "Regine's Professional Digital Twin",
        'description': 'AI-powered assistant showcasing 13+ years of Business Analysis expertise',
        'endpoints': {
            'health': '/health',
            'test': '/api/test',
            'query': '/api/query (POST)',
            'analytics': '/api/analytics'
        },
        'version': '2.0'
    })

# Vercel serverless function handler
def handler(request):
    """Vercel serverless function handler"""
    return app(request.environ, lambda status, headers: None)

if __name__ == '__main__':
    # For local development
    port = int(os.getenv('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=True)
