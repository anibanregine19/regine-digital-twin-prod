#!/usr/bin/env python3
"""
Optimized Digital Twin MCP Server
Uses Upstash Vector's automatic text vectorization for semantic search
"""

import json
import os
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from functools import lru_cache
from dotenv import load_dotenv
from upstash_vector import Index

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Initialize Upstash Vector clients
try:
    # Primary client for read/write operations
    index = Index(
        url=os.getenv("UPSTASH_VECTOR_REST_URL"),
        token=os.getenv("UPSTASH_VECTOR_REST_TOKEN")
    )
    
    # Read-only client for query operations (optional security enhancement)
    index_readonly = Index(
        url=os.getenv("UPSTASH_VECTOR_REST_URL"),
        token=os.getenv("UPSTASH_VECTOR_REST_READONLY_TOKEN")
    ) if os.getenv("UPSTASH_VECTOR_REST_READONLY_TOKEN") else index
    
    logger.info("✅ Upstash Vector clients initialized successfully")
except Exception as e:
    logger.error(f"❌ Failed to initialize Upstash Vector clients: {str(e)}")
    # Continue with fallback to local data only
    index = None
    index_readonly = None

# Configuration
SIMILARITY_THRESHOLD = 0.3  # Further lowered threshold for better results
MAX_RESULTS = 5
CACHE_SIZE = 128

@lru_cache(maxsize=CACHE_SIZE)
def load_digital_twin_data(section: Optional[str] = None) -> Dict:
    """Load data from the digital twin JSON with caching"""
    try:
        with open('mytwin_refined.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            if section:
                return data.get(section, {})
            return data
    except Exception as e:
        logger.error(f"Error loading digital twin data: {str(e)}")
        return {}

def safe_vector_query(query_text: str, top_k: int = MAX_RESULTS, 
                     filter_type: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Safely query Upstash Vector with automatic text embedding
    Uses raw text query - Upstash handles the embedding automatically
    """
    if not index_readonly:
        logger.warning("Vector database not available, falling back to local search")
        return []
    
    try:
        # Query with raw text - Upstash handles embedding automatically
        # Note: Removed filter for now due to API format issues
        response = index_readonly.query(
            data=query_text,  # Raw text query
            top_k=top_k,
            include_metadata=True
        )
        
        # Process results - handle Upstash Vector response format
        results = []
        matches = response if isinstance(response, list) else []
            
        for match in matches:
            # Handle QueryResult objects from Upstash Vector
            score = match.score if hasattr(match, 'score') else 0.0
            match_id = match.id if hasattr(match, 'id') else ''
            metadata = match.metadata if hasattr(match, 'metadata') else {}
                
            if score >= SIMILARITY_THRESHOLD:
                # Apply filter after retrieval if specified
                if filter_type and metadata.get('type') != filter_type:
                    continue
                    
                result = {
                    'id': match_id,
                    'score': score,
                    'metadata': metadata,
                    'content': metadata.get('content', metadata.get('description', '')),
                    'type': metadata.get('type', 'unknown')
                }
                results.append(result)
        
        logger.info(f"✅ Vector query returned {len(results)} relevant results")
        return results
        
    except Exception as e:
        logger.error(f"❌ Vector query failed: {str(e)}")
        if "authentication" in str(e).lower():
            logger.error("Check UPSTASH_VECTOR_REST_TOKEN in .env file")
        elif "quota" in str(e).lower():
            logger.error("Query quota exceeded - check your Upstash plan")
        return []

def get_relevant_experiences(query: str, category: Optional[str] = None) -> List[Dict[str, Any]]:
    """Get relevant professional experiences using vector search"""
    
    # First try vector search
    vector_results = safe_vector_query(query, top_k=3, filter_type='professional_experience')
    
    if vector_results:
        experiences = []
        for result in vector_results:
            metadata = result.get('metadata', {})
            experience = {
                'company': metadata.get('company', 'Unknown'),
                'position': metadata.get('position', 'Unknown'),
                'duration': metadata.get('duration', 'Unknown'),
                'content': result.get('content', ''),
                'relevance_score': result.get('score', 0.0),
                'type': 'experience'
            }
            experiences.append(experience)
        return experiences
    
    # Fallback to local data if vector search fails
    logger.info("Falling back to local experience search")
    data = load_digital_twin_data()
    experiences = data.get('professional_experience', [])
    
    # Simple keyword matching for fallback
    query_lower = query.lower()
    relevant = []
    
    for exp in experiences:
        relevance = 0
        text_to_search = f"{exp.get('company', '')} {exp.get('position', '')} {exp.get('description', '')}"
        
        # Simple keyword scoring
        for word in query_lower.split():
            if word in text_to_search.lower():
                relevance += 1
        
        if relevance > 0:
            exp_copy = exp.copy()
            exp_copy['relevance_score'] = relevance / len(query_lower.split())
            exp_copy['type'] = 'experience'
            relevant.append(exp_copy)
    
    # Sort by relevance and return top results
    relevant.sort(key=lambda x: x['relevance_score'], reverse=True)
    return relevant[:3]

def search_skills_and_competencies(query: str) -> List[Dict[str, Any]]:
    """Search for skills and competencies using vector search"""
    
    # Vector search for skills
    vector_results = safe_vector_query(query, top_k=5, filter_type='core_competency')
    
    if vector_results:
        skills = []
        for result in vector_results:
            metadata = result.get('metadata', {})
            skill = {
                'skill_name': metadata.get('skill_name', 'Unknown'),
                'description': result.get('content', ''),
                'relevance_score': result.get('score', 0.0),
                'type': 'skill'
            }
            skills.append(skill)
        return skills
    
    # Fallback to local skills search
    logger.info("Falling back to local skills search")
    data = load_digital_twin_data()
    personal_info = data.get('personalInfo', {})
    competencies = personal_info.get('core_competencies', {})
    
    query_lower = query.lower()
    relevant_skills = []
    
    for skill_key, description in competencies.items():
        skill_name = skill_key.replace('_', ' ').title()
        relevance = 0
        
        # Check skill name and description for matches
        search_text = f"{skill_name} {description}".lower()
        for word in query_lower.split():
            if word in search_text:
                relevance += 1
        
        if relevance > 0:
            skill = {
                'skill_name': skill_name,
                'description': description,
                'relevance_score': relevance / len(query_lower.split()),
                'type': 'skill'
            }
            relevant_skills.append(skill)
    
    relevant_skills.sort(key=lambda x: x['relevance_score'], reverse=True)
    return relevant_skills[:5]

def search_interview_qa(query: str) -> List[Dict[str, Any]]:
    """Search interview Q&A using vector search"""
    
    # Vector search for Q&A
    vector_results = safe_vector_query(query, top_k=3, filter_type='interview_qa')
    
    if vector_results:
        qa_results = []
        for result in vector_results:
            metadata = result.get('metadata', {})
            qa = {
                'question': metadata.get('question', 'Unknown'),
                'answer': result.get('content', '').split('Answer: ')[-1] if 'Answer: ' in result.get('content', '') else result.get('content', ''),
                'category': metadata.get('category', 'general'),
                'relevance_score': result.get('score', 0.0),
                'type': 'qa'
            }
            qa_results.append(qa)
        return qa_results
    
    # Fallback to local Q&A search
    logger.info("Falling back to local Q&A search")
    return get_local_qa_fallback(query)

def get_local_qa_fallback(query: str) -> List[Dict[str, Any]]:
    """Fallback method for Q&A search using local data"""
    data = load_digital_twin_data()
    interview_qa = data.get('interview_qa', {})
    
    query_lower = query.lower()
    relevant_qa = []
    
    for category, qa_list in interview_qa.items():
        for qa in qa_list:
            question = qa.get('question', '')
            answer = qa.get('answer', '')
            keywords = qa.get('keywords', [])
            
            relevance = 0
            search_text = f"{question} {answer} {' '.join(keywords)}".lower()
            
            for word in query_lower.split():
                if word in search_text:
                    relevance += 1
            
            if relevance > 0:
                qa_result = {
                    'question': question,
                    'answer': answer,
                    'category': category,
                    'relevance_score': relevance / len(query_lower.split()),
                    'type': 'qa'
                }
                relevant_qa.append(qa_result)
    
    relevant_qa.sort(key=lambda x: x['relevance_score'], reverse=True)
    return relevant_qa[:3]

def comprehensive_search(query: str) -> Dict[str, Any]:
    """Perform comprehensive search across all data types"""
    results = {
        'experiences': get_relevant_experiences(query),
        'skills': search_skills_and_competencies(query),
        'qa': search_interview_qa(query),
        'query': query,
        'timestamp': datetime.now().isoformat()
    }
    
    # Also search for personal info if query seems relevant
    if any(word in query.lower() for word in ['name', 'contact', 'location', 'summary', 'about']):
        vector_results = safe_vector_query(query, top_k=1, filter_type='personal_info')
        if vector_results:
            results['personal_info'] = vector_results[0]
        else:
            # Fallback to local personal info
            data = load_digital_twin_data()
            results['personal_info'] = data.get('personalInfo', {})
    
    return results

def format_comprehensive_response(results: Dict[str, Any], query: str) -> str:
    """Format comprehensive search results into a coherent response"""
    response_parts = []
    
    # Handle personal info queries
    if 'personal_info' in results and results['personal_info']:
        personal = results['personal_info']
        if isinstance(personal, dict):
            name = personal.get('name', '')
            title = personal.get('title', '')
            summary = personal.get('summary', '')
            
            if any(word in query.lower() for word in ['name', 'who are you']):
                response_parts.append(f"I'm {name}, {title}.")
            
            if 'summary' in query.lower() or 'about' in query.lower():
                response_parts.append(summary)
    
    # Handle experience results
    experiences = results.get('experiences', [])
    if experiences:
        response_parts.append("Based on my professional experience:")
        for exp in experiences[:2]:  # Top 2 most relevant
            company = exp.get('company', 'Unknown')
            position = exp.get('position', 'Unknown')
            content = exp.get('content', '')
            
            if content:
                # Extract key info from content
                lines = content.split('\n')
                key_info = [line for line in lines if any(keyword in line.lower() 
                           for keyword in ['achievement', 'key', 'result', 'improvement'])]
                
                if key_info:
                    response_parts.append(f"At {company} as {position}: {key_info[0]}")
                else:
                    response_parts.append(f"At {company}, I worked as {position}.")
    
    # Handle skills results  
    skills = results.get('skills', [])
    if skills:
        if not experiences:  # Only add this header if no experience section
            response_parts.append("Regarding my skills and competencies:")
        
        skill_descriptions = []
        for skill in skills[:3]:  # Top 3 most relevant
            skill_name = skill.get('skill_name', '')
            description = skill.get('description', '')
            if skill_name and description:
                skill_descriptions.append(f"{skill_name}: {description}")
        
        if skill_descriptions:
            response_parts.extend(skill_descriptions)
    
    # Handle Q&A results
    qa_results = results.get('qa', [])
    if qa_results and not (experiences or skills):  # Only if no other results
        best_qa = qa_results[0]  # Most relevant Q&A
        answer = best_qa.get('answer', '')
        if answer:
            response_parts.append(answer)
    
    if response_parts:
        return '\n\n'.join(response_parts)
    else:
        return "I don't have specific information about that topic. Could you please ask about my professional experience, skills, or career background?"

@lru_cache(maxsize=CACHE_SIZE)
def cached_query(query: str) -> str:
    """Cached version of the main query function"""
    results = comprehensive_search(query)
    return format_comprehensive_response(results, query)

def mcp_answer_query(query: str) -> Dict[str, Any]:
    """
    Main MCP function to answer queries about the digital twin
    Uses Upstash Vector's automatic embedding for semantic search
    """
    try:
        # Validate input
        if not query or not query.strip():
            return {
                'content': "Please provide a question about my professional background, skills, or experience.",
                'metadata': {'error': 'empty_query'}
            }
        
        # Get comprehensive response
        response_content = cached_query(query.strip())
        
        return {
            'content': response_content,
            'metadata': {
                'query': query,
                'timestamp': datetime.now().isoformat(),
                'vector_search_enabled': index_readonly is not None
            }
        }
        
    except Exception as e:
        logger.error(f"Error processing query '{query}': {str(e)}")
        return {
            'content': "I'm sorry, I encountered an error processing your question. Please try rephrasing your query.",
            'metadata': {'error': str(e)}
        }

def get_interview_qa_response(query: str) -> str:
    """Get interview Q&A response - simplified interface"""
    result = mcp_answer_query(query)
    return result.get('content', '')

def validate_query(query: str) -> Tuple[bool, Optional[str]]:
    """Validate query input"""
    if not query or not query.strip():
        return False, "Query cannot be empty"
    
    if len(query.strip()) < 3:
        return False, "Query too short - please provide more context"
    
    if len(query) > 1000:
        return False, "Query too long - please keep it under 1000 characters"
    
    return True, None

# Health check function
def health_check() -> Dict[str, Any]:
    """Check system health"""
    health_status = {
        'timestamp': datetime.now().isoformat(),
        'vector_db_available': index_readonly is not None,
        'local_data_available': bool(load_digital_twin_data()),
    }
    
    if index_readonly:
        try:
            # Test vector query
            test_results = safe_vector_query("test", top_k=1)
            health_status['vector_db_responsive'] = True
            health_status['vector_db_count'] = len(test_results)
        except:
            health_status['vector_db_responsive'] = False
    
    return health_status

if __name__ == "__main__":
    # Test the system
    print("🔧 Testing Digital Twin MCP Server with Automatic Embedding")
    
    # Health check
    health = health_check()
    print(f"📊 Health Status: {health}")
    
    # Test queries
    test_queries = [
        "What are your core skills?",
        "Tell me about your experience at Asurion",
        "What methodologies do you use?",
        "What awards have you received?"
    ]
    
    for query in test_queries:
        print(f"\n❓ Query: {query}")
        response = mcp_answer_query(query)
        print(f"✅ Response: {response['content'][:200]}...")
        
    print("\n🎉 Testing completed!")
