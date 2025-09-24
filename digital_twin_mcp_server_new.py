import json
import os
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from dotenv import load_dotenv
from upstash_vector import Index
import numpy as np

# Load en        # Handle responses w        # Handle responses with priority
        if is_soft_skills:
            # Get both soft skills and search results
            soft_skills_response = get_soft_skills_response(query)
            search_results = search_digital_twin(query)
            
            # Combine responses if both available
            if soft_skills_response and search_results:
                experience_examples = [r for r in search_results if r['type'] == 'experience'][:1]
                if experience_examples:
                    return f"{soft_skills_response}\n\nTo illustrate with a concrete example:\n• {experience_examples[0]['content']}"
                return soft_skills_response
            
            # Use whichever response is available
            if soft_skills_response:
                return soft_skills_response
            if search_results:
                return format_response(search_results, query)
            
            # Generic soft skills response
            return "I approach this through clear communication, active listening, and collaborative problem-solving, always focusing on achieving positive outcomes while maintaining strong professional relationships."        if is_soft_skills:
            # Get both soft skills and search results
            soft_skills_response = get_soft_skills_response(query)
            search_results = search_digital_twin(query)
            
            # Combine responses if both available
            if soft_skills_response and search_results:
                experience_examples = [r for r in search_results if r['type'] == 'experience'][:1]
                if experience_examples:
                    return f"{soft_skills_response}\n\nTo illustrate with a concrete example:\n• {experience_examples[0]['content']}"
                return soft_skills_response
            
            # Use whichever response is available
            if soft_skills_response:
                return soft_skills_response
            if search_results:
                return format_response(search_results, query)
            
            # Generic soft skills response
            return "I approach this through clear communication, active listening, and collaborative problem-solving, always focusing on achieving positive outcomes while maintaining strong professional relationships."ables
load_dotenv()

# Initialize Upstash Vector client
index = Index(
    url=os.getenv("UPSTASH_VECTOR_REST_URL"),
    token=os.getenv("UPSTASH_VECTOR_REST_TOKEN")
)

# Configuration
SIMILARITY_THRESHOLD = 0.7
MAX_RESULTS = 3

def create_query_embedding(query: str) -> List[float]:
    """Create an embedding for the query text"""
    return np.random.rand(1024).tolist()

def load_soft_skills():
    """Load soft skills from the digital twin JSON"""
    try:
        with open('mytwin_refined.json', 'r') as f:
            data = json.load(f)
            return data.get('skills', {}).get('soft_skills', [])
    except Exception as e:
        print(f"Error loading soft skills: {str(e)}")
        return []

def get_soft_skills_response(query: str) -> str:
    """Get soft skills response with enhanced context and structure"""
    soft_skills = load_soft_skills()
    if not soft_skills:
        return None
        
    query_lower = query.lower()
    query_terms = set(query_lower.split())
    
    # Define categories and their context
    skill_categories = {
        'communication': {
            'terms': {'communication', 'verbal', 'written', 'presentation'},
            'context': "In my communication style, I emphasize"
        },
        'leadership': {
            'terms': {'leadership', 'lead', 'guide', 'direct', 'manage'},
            'context': "My leadership approach centers on"
        },
        'teamwork': {
            'terms': {'team', 'collaborate', 'coordination', 'group'},
            'context': "When working in teams, I focus on"
        },
        'conflict': {
            'terms': {'conflict', 'disagreement', 'difficult', 'challenge'},
            'context': "My approach to handling conflicts involves"
        },
        'stakeholder': {
            'terms': {'stakeholder', 'client', 'customer', 'relationship'},
            'context': "In stakeholder management, I prioritize"
        }
    }
    
    # Identify primary category with strength scoring
    query_category = None
    max_score = 0
    for category, info in skill_categories.items():
        score = sum(term in query_lower for term in info['terms']) * 2
        for term in info['terms']:
            if term in query_terms:
                score += 1
        if score > max_score:
            max_score = score
            query_category = category
            
    # Score skills with enhanced relevance
    scored_skills = []
    for skill in soft_skills:
        score = 0
        skill_lower = skill['skill'].lower()
        examples = ' '.join(skill['examples']).lower()
        
        # Direct matches
        if any(term in skill_lower for term in query_terms):
            score += 3
        if any(term in examples for term in query_terms):
            score += 2
            
        # Category relevance
        if query_category:
            if any(term in skill_lower for term in skill_categories[query_category]['terms']):
                score += 2
            if any(term in examples for term in skill_categories[query_category]['terms']):
                score += 1
        
        # Example relevance scoring
        example_relevance = sum(term in examples for term in query_terms)
        score += example_relevance
            
        if score > 0:
            scored_skills.append((score, skill))
    
    if scored_skills:
        scored_skills.sort(key=lambda x: x[0], reverse=True)
        
        # Format response with clear structure
        response_parts = []
        
        # Add contextual intro
        intros = {
            'communication': "In my approach to communication, I consistently",
            'leadership': "My leadership philosophy focuses on",
            'teamwork': "When collaborating in team environments, I emphasize",
            'conflict': "My strategy for handling conflicts centers on",
            'stakeholder': "In managing stakeholder relationships, I prioritize"
        }
        
        if query_category:
            response_parts.append(intros.get(query_category, skill_categories[query_category]['context']))
        else:
            response_parts.append("In addressing this, I focus on")

        # Add detailed examples with better formatting
        used_examples = set()
        for i, (_, skill) in enumerate(scored_skills[:2]):
            relevant_examples = [ex for ex in skill['examples'] if ex not in used_examples]
            if relevant_examples:
                if i == 0:
                    response = f"\n\n• {skill['skill']}: {relevant_examples[0]}"
                    if len(relevant_examples) > 1:
                        response += f"\n  Additionally, {relevant_examples[1]}"
                else:
                    response = f"\n\n• {skill['skill']}: {relevant_examples[0]}"
                response_parts.append(response)
                used_examples.update(relevant_examples[:2])
        
        return " ".join(response_parts)
    return None

def process_query(query: str) -> str:
    """Process incoming queries with enhanced response prioritization"""
    try:
        query_lower = query.lower()
        
        # Define skill categories with context patterns
        skill_categories = {
            'communication': {
                'terms': {'communication', 'verbal', 'written', 'presentation'},
                'patterns': {'communicate with', 'express', 'convey', 'present to'}
            },
            'leadership': {
                'terms': {'leadership', 'lead', 'guide', 'direct', 'manage'},
                'patterns': {'lead a team', 'manage people', 'guide others'}
            },
            'teamwork': {
                'terms': {'team', 'collaborate', 'coordination', 'group'},
                'patterns': {'work in team', 'team environment', 'collaborate with'}
            },
            'conflict': {
                'terms': {'conflict', 'disagreement', 'difficult', 'challenge', 'dispute'},
                'patterns': {'handle conflict', 'resolve', 'deal with', 'manage conflict'}
            },
            'stakeholder': {
                'terms': {'stakeholder', 'client', 'customer', 'relationship'},
                'patterns': {'manage stakeholder', 'work with client', 'handle customer'}
            }
        }
        
        # Soft skills detection with context
        is_soft_skills = False
        for category, info in skill_categories.items():
            if any(term in query_lower for term in info['terms']) or \
               any(pattern in query_lower for pattern in info['patterns']):
                is_soft_skills = True
                break
                
        # Additional soft skills contexts
        if not is_soft_skills:
            soft_skill_contexts = {
                'how do you handle', 'how do you manage', 'tell me about your',
                'what is your approach to', 'how would you describe', 'how do you approach',
                'how do you deal with', 'how do you work with', 'how do you lead',
                'what is your style', 'how do you interact', 'how do you respond',
                'what do you do when', 'how would you handle'
            }
            is_soft_skills = any(context in query_lower for context in soft_skill_contexts)
        
        # Methodology patterns - only check if not soft skills
        methodology_terms = {
            'methodology', 'methodologies', 'methods', 'framework',
            'process framework', 'methodological approach', 'process methodology'
        }
        analysis_terms = {
            'business analysis', 'process improvement', 'business process',
            'process analysis', 'analysis technique'
        }
                        
        # Only consider methodology if not soft skills
        is_methodology = False
        if not is_soft_skills:
            is_methodology = (
                any(term in query_lower for term in methodology_terms) and
                any(term in query_lower for term in analysis_terms)
            ) or (
                'methodology' in query_lower and
                any(term in query_lower for term in ['process', 'business', 'analysis'])
            )
        
        # Handle responses with priority
        if is_soft_skills:
            # Try soft skills response
            soft_skills_response = get_soft_skills_response(query)
            if soft_skills_response:
                return soft_skills_response
                
            # Fallback to digital twin search
            results = search_digital_twin(query)
            if results:
                return format_response(results, query)
            
            # Generic soft skills response
            return "I approach this through effective communication, active listening, and collaborative problem-solving."
            
        elif is_methodology:
            # Handle methodology questions
            methodology_response = get_interview_qa_response(query)
            if methodology_response:
                return methodology_response
        
        # Fallback to regular search
        results = search_digital_twin(query)
        return format_response(results, query)
        
    except Exception as e:
        return f"I apologize, but I encountered an error: {str(e)}"

def search_digital_twin(query: str) -> List[Dict[str, Any]]:
    """Search the digital twin knowledge base"""
    try:
        # Create query embedding
        query_embedding = create_query_embedding(query)
        
        # Search vector database
        results = index.query(
            vector=query_embedding,
            top_k=MAX_RESULTS * 3,
            include_metadata=True
        )
        
        # Process results
        relevant_results = []
        for result in results:
            if result.score >= SIMILARITY_THRESHOLD:
                metadata = result.metadata
                relevant_results.append({
                    'content': metadata.get('content', ''),
                    'type': metadata.get('type', 'unknown'),
                    'title': metadata.get('title', ''),
                    'tags': metadata.get('tags', []),
                    'importance': metadata.get('importance', 'low'),
                    'score': result.score,
                    'date_range': metadata.get('date_range', '')
                })
        
        return relevant_results[:MAX_RESULTS]
        
    except Exception as e:
        print(f"Error in search: {str(e)}")
        return []

def format_response(results: List[Dict[str, Any]], query: str) -> str:
    """Format search results into a natural, context-aware response"""
    if not results:
        return "I don't have enough information to provide a specific answer to that question."
    
    # Analyze query intent
    query_lower = query.lower()
    is_behavioral = any(term in query_lower for term in ['tell me about a time', 'example of', 'situation where'])
    is_when = any(word in query_lower for word in ['when', 'what year', 'what time', 'how long'])
    is_where = any(word in query_lower for word in ['where', 'which company', 'location'])
    is_how = any(word in query_lower for word in ['how', 'what approach', 'what method'])
    
    # Organize results by type
    experience_results = [r for r in results if r['type'] == 'experience']
    skill_results = [r for r in results if r['type'] == 'skills']
    project_results = [r for r in results if r['type'] == 'project']
    other_results = [r for r in results if r['type'] not in ['experience', 'skills', 'project']]
    
    response_parts = []
    
    # Format based on query intent
    if is_behavioral and experience_results:
        response_parts.append("Here's a relevant example from my experience:")
        for result in experience_results[:2]:
            response_parts.append(f"\n• {result['content']}")
    
    elif is_how and (skill_results or project_results):
        if skill_results:
            response_parts.append("My approach involves:")
            for result in skill_results[:2]:
                response_parts.append(f"\n• {result['content']}")
        if project_results:
            prefix = response_parts and "\nTo illustrate this:" or "Here's a practical example:"
            response_parts.append(f"{prefix}\n• {project_results[0]['content']}")
    
    else:
        # General response format
        if experience_results:
            prefix = "In my experience, "
            if is_when:
                prefix = f"During {experience_results[0]['date_range']}, "
            elif is_where and 'title' in experience_results[0]:
                prefix = f"At {experience_results[0]['title'].split(' - ')[0]}, "
            
            content = experience_results[0]['content']
            if content.lower().startswith(("at ", "in ", "during ")):
                content = content.split(", ", 1)[1] if ", " in content else content
            response_parts.append(prefix + content)
        
        if skill_results:
            if response_parts:
                response_parts.append("\n\nRelevant skills and competencies:")
            else:
                response_parts.append("I apply these skills and competencies:")
            for result in skill_results[:2]:
                response_parts.append(f"• {result['content']}")
        
        for result in project_results + other_results:
            prefix = "\n\n"
            if result['type'] == 'project':
                response_parts.append(f"{prefix}To demonstrate this in practice: {result['content']}")
            else:
                response_parts.append(f"{prefix}{result['content']}")
    
    # Join response parts
    if not response_parts:
        return "I don't have specific examples to share for this question."
    
    return "\n".join(response_parts)

def load_interview_qa() -> Dict:
    """Load interview Q&A data from JSON"""
    try:
        with open('mytwin_refined.json', 'r') as f:
            data = json.load(f)
            return data.get('interview_qa', {})
    except Exception as e:
        print(f"Error loading interview Q&A: {str(e)}")
        return {}

def get_interview_qa_response(query: str) -> str:
    """Get a formatted response from interview Q&A data"""
    qa_data = load_interview_qa()
    if not qa_data:
        return None
        
    query_lower = query.lower()
    query_words = set(query_lower.split())
    
    # Score each QA pair
    scored_answers = []
    for category, qa_list in qa_data.items():
        for qa in qa_list:
            score = 0
            qa_lower = qa['question'].lower()
            qa_words = set(qa_lower.split())
            
            # Exact match
            if query_lower.strip() == qa_lower.strip():
                score += 10
                
            # Word overlap
            common_words = query_words & qa_words
            score += len(common_words) * 2
            
            # Category match
            if category.replace('_', ' ') in query_lower:
                score += 3
            
            # Keywords
            for keyword in qa.get('keywords', []):
                if keyword.lower() in query_lower:
                    score += 2
            
            if score > 0:
                scored_answers.append((score, qa, category))
    
    if scored_answers:
        # Return highest scoring answer
        scored_answers.sort(key=lambda x: x[0], reverse=True)
        return scored_answers[0][1]['answer']
        
    return None

# MCP server endpoints
def mcp_answer_query(query: str) -> Dict[str, Any]:
    """MCP endpoint for answering queries"""
    try:
        is_valid, error = validate_query(query)
        if not is_valid:
            return {"error": error, "status": "error"}
        
        response = process_query(query)
        return {
            "answer": response,
            "status": "success",
            "metadata": {
                "query_length": len(query),
                "timestamp": datetime.now().isoformat()
            }
        }
    except Exception as e:
        return {
            "error": f"An unexpected error occurred: {str(e)}",
            "status": "error"
        }

def validate_query(query: str) -> Tuple[bool, Optional[str]]:
    """Validate the incoming query"""
    if not query:
        return False, "Query cannot be empty"
    if len(query) > 500:
        return False, "Query is too long. Please limit to 500 characters"
    return True, None