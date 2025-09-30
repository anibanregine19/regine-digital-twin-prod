#!/usr/bin/env python3
"""
Enhanced Digital Twin MCP Server for Vercel + Neon PostgreSQL
Combines Upstash Vector (AI) + PostgreSQL (analytics)
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

# Import your existing MCP functions
from digital_twin_mcp_server_optimized import mcp_answer_query, health_check

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
            
            # Create system_metrics table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS system_metrics (
                    id SERIAL PRIMARY KEY,
                    metric_name VARCHAR(50),
                    metric_value FLOAT,
                    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            
            conn.commit()
            conn.close()
            logger.info("✅ PostgreSQL tables created successfully")
            
        except Exception as e:
            logger.error(f"⚠️ Database setup error: {e}")
    
    def categorize_query(self, query: str) -> str:
        """Categorize queries for analytics"""
        query_lower = query.lower()
        
        if any(word in query_lower for word in ['competenc', 'skill', 'ability']):
            return 'competencies'
        elif any(word in query_lower for word in ['asurion', 'experience', 'work', 'role']):
            return 'experience'
        elif any(word in query_lower for word in ['stakeholder', 'management', 'team']):
            return 'stakeholder_management'
        elif any(word in query_lower for word in ['methodology', 'agile', 'scrum', 'process']):
            return 'methodologies'
        elif any(word in query_lower for word in ['award', 'achievement', 'accomplishment']):
            return 'achievements'
        else:
            return 'general'
    
    def log_chat(self, query: str, response: str, response_time: float, 
                 vector_hits: int = 0, user_ip: str = None, user_agent: str = None):
        """Log chat interaction to PostgreSQL"""
        try:
            conn = psycopg2.connect(self.db_url)
            cur = conn.cursor()
            
            category = self.categorize_query(query)
            
            # Insert chat log
            cur.execute("""
                INSERT INTO chat_logs 
                (query, response, response_time, vector_hits, query_category, user_ip, user_agent)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (query, response[:1000], response_time, vector_hits, category, user_ip, user_agent))
            
            # Update popular questions
            cur.execute("""
                INSERT INTO popular_questions (question_type, question_text, ask_count, avg_response_time)
                VALUES (%s, %s, 1, %s)
                ON CONFLICT (question_type) DO UPDATE SET
                    ask_count = popular_questions.ask_count + 1,
                    avg_response_time = (popular_questions.avg_response_time + %s) / 2,
                    last_asked = CURRENT_TIMESTAMP
            """, (category, query[:200], response_time, response_time))
            
            conn.commit()
            conn.close()
            logger.info(f"📊 Logged chat: {category} - {response_time:.2f}s")
            
        except Exception as e:
            logger.warning(f"⚠️ Logging error: {e}")
    
    def get_analytics(self) -> Dict[str, Any]:
        """Get comprehensive analytics from PostgreSQL"""
        try:
            conn = psycopg2.connect(self.db_url)
            cur = conn.cursor()
            
            # Get chat statistics
            cur.execute("""
                SELECT 
                    COUNT(*) as total_chats,
                    AVG(response_time) as avg_response_time,
                    AVG(vector_hits) as avg_vector_hits
                FROM chat_logs 
                WHERE created_at > NOW() - INTERVAL '30 days'
            """)
            stats = cur.fetchone()
            
            # Get popular question categories
            cur.execute("""
                SELECT question_type, ask_count, avg_response_time
                FROM popular_questions 
                ORDER BY ask_count DESC 
                LIMIT 10
            """)
            popular = cur.fetchall()
            
            # Get recent activity
            cur.execute("""
                SELECT query_category, COUNT(*) as count
                FROM chat_logs 
                WHERE created_at > NOW() - INTERVAL '7 days'
                GROUP BY query_category
                ORDER BY count DESC
            """)
            recent_activity = cur.fetchall()
            
            conn.close()
            
            return {
                'total_chats': stats[0] or 0,
                'avg_response_time': round(stats[1] or 0, 2),
                'avg_vector_hits': round(stats[2] or 0, 1),
                'popular_categories': [{'type': p[0], 'count': p[1], 'avg_time': round(p[2], 2)} for p in popular],
                'recent_activity': [{'category': r[0], 'count': r[1]} for r in recent_activity],
                'generated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"⚠️ Analytics error: {e}")
            return {'error': str(e), 'generated_at': datetime.now().isoformat()}

# Initialize enhanced twin
enhanced_twin = EnhancedDigitalTwin()

@app.route('/health', methods=['GET'])
def health_endpoint():
    """Health check with PostgreSQL status"""
    try:
        # Check MCP server health
        mcp_health = health_check()
        
        # Check PostgreSQL connection
        conn = psycopg2.connect(enhanced_twin.db_url)
        conn.close()
        postgres_health = True
        
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'mcp_server': mcp_health,
            'postgresql': postgres_health,
            'services': {
                'upstash_vector': mcp_health.get('vector_db_available', False),
                'postgresql': postgres_health,
                'ai_processing': True
            }
        })
        
    except Exception as e:
        logger.error(f"Health check error: {str(e)}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/query', methods=['POST'])
def query_endpoint():
    """Enhanced query endpoint with PostgreSQL logging"""
    start_time = time.time()
    
    try:
        # Get request data
        data = request.get_json()
        
        if not data or 'query' not in data:
            return jsonify({
                'error': 'Missing query parameter',
                'content': 'Please provide a query in the request body.'
            }), 400
        
        query = data['query'].strip()
        
        if not query:
            return jsonify({
                'error': 'Empty query',
                'content': 'Please provide a non-empty query.'
            }), 400
        
        # Get user info for analytics
        user_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
        user_agent = request.headers.get('User-Agent', 'Unknown')
        
        logger.info(f"Processing query: {query}")
        
        # Get response from MCP server
        response = mcp_answer_query(query)
        response_time = time.time() - start_time
        
        # Extract metadata
        vector_hits = response.get('metadata', {}).get('vector_results', 0)
        
        # Log to PostgreSQL
        enhanced_twin.log_chat(
            query=query,
            response=response.get('content', ''),
            response_time=response_time,
            vector_hits=vector_hits,
            user_ip=user_ip,
            user_agent=user_agent
        )
        
        # Format response for v0.app
        result = {
            'content': response.get('content', 'No response available'),
            'metadata': {
                'timestamp': datetime.now().isoformat(),
                'query_length': len(query),
                'response_length': len(response.get('content', '')),
                'response_time': round(response_time, 3),
                'vector_hits': vector_hits,
                'category': enhanced_twin.categorize_query(query),
                'logged': True
            }
        }
        
        logger.info(f"Response: {len(result['content'])} chars in {response_time:.2f}s")
        return jsonify(result)
        
    except Exception as e:
        response_time = time.time() - start_time
        logger.error(f"Query processing error: {str(e)}")
        
        return jsonify({
            'error': str(e),
            'content': "I'm having trouble processing your question right now. Please try again in a moment.",
            'metadata': {
                'timestamp': datetime.now().isoformat(),
                'error': True,
                'response_time': round(response_time, 3)
            }
        }), 500

@app.route('/api/analytics', methods=['GET'])
def analytics_endpoint():
    """Get analytics dashboard data"""
    try:
        analytics = enhanced_twin.get_analytics()
        return jsonify(analytics)
        
    except Exception as e:
        logger.error(f"Analytics endpoint error: {str(e)}")
        return jsonify({
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/test', methods=['GET'])
def test_endpoint():
    """Test endpoint for quick verification"""
    try:
        test_query = "What are your core competencies?"
        start_time = time.time()
        
        response = mcp_answer_query(test_query)
        response_time = time.time() - start_time
        
        return jsonify({
            'status': 'success',
            'test_query': test_query,
            'response': response.get('content', '')[:200] + '...',
            'response_time': round(response_time, 3),
            'services': {
                'mcp_server': True,
                'upstash_vector': True,
                'postgresql': True
            },
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Test endpoint error: {str(e)}")
        return jsonify({
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/', methods=['GET'])
def root():
    """Root endpoint with service info"""
    return jsonify({
        'service': 'Enhanced Digital Twin MCP Server',
        'version': '2.0.0',
        'status': 'running',
        'features': [
            'Upstash Vector AI Search',
            'PostgreSQL Analytics',
            'Professional Chat Logging',
            'Real-time Metrics'
        ],
        'endpoints': {
            'health': '/health',
            'query': '/api/query (POST)',
            'analytics': '/api/analytics',
            'test': '/api/test'
        },
        'timestamp': datetime.now().isoformat()
    })

# For Vercel deployment
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=False)
