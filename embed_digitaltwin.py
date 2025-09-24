import json
import os
from dotenv import load_dotenv
from upstash_vector import Index
import numpy as np

# Load environment variables
load_dotenv()

# Initialize Upstash Vector client
index = Index(
    url=os.getenv("UPSTASH_VECTOR_REST_URL"),
    token=os.getenv("UPSTASH_VECTOR_REST_TOKEN")
)

def create_embeddings(text):
    """Create simple embeddings for testing"""
    # This is a simplified embedding function for testing
    # In production, you should use a proper embedding model
    return np.random.rand(1024).tolist()  # Upstash Vector expects 1024 dimensions

def load_digital_twin():
    """Load the digital twin JSON file"""
    with open('mytwin_refined.json', 'r') as f:
        return json.load(f)

def prepare_chunks(data):
    """Convert the digital twin data into chunks suitable for embedding"""
    chunks = data.get('content_chunks', [])
    
    # Add soft skills chunks
    soft_skills = data.get('skills', {}).get('soft_skills', [])
    for skill in soft_skills:
        chunks.append({
            'id': f"chunk_soft_skill_{skill['skill'].lower().replace(' ', '_')}",
            'type': 'soft_skills',
            'title': f"Soft Skill: {skill['skill']}",
            'content': f"{skill['skill']}: {' '.join(skill['examples'])} - {skill['context']}",
            'metadata': {
                'category': 'soft_skills',
                'tags': ['soft skills', skill['skill'].lower(), 'interpersonal'],
                'importance': 'high',
                'examples': skill['examples'],
                'context': skill['context']
            }
        })
    
    return chunks

def embed_chunks(chunks):
    """Embed each chunk into Upstash Vector"""
    for chunk in chunks:
        # Create a meaningful text representation
        text = f"{chunk['title']}: {chunk['content']}"
        
        # Generate embedding
        embedding = create_embeddings(text)
        
        # Prepare metadata with optional fields
        metadata = {
            'type': chunk['type'],
            'title': chunk['title'],
            'content': chunk['content'],
            'tags': chunk['metadata'].get('tags', []),
            'importance': chunk['metadata'].get('importance', 'medium')
        }
        
        # Add optional metadata fields
        if 'date_range' in chunk['metadata']:
            metadata['date_range'] = chunk['metadata']['date_range']
        if 'examples' in chunk['metadata']:
            metadata['examples'] = chunk['metadata']['examples']
        if 'context' in chunk['metadata']:
            metadata['context'] = chunk['metadata']['context']
        
        # Store in Upstash Vector
        index.upsert([{
            'id': chunk['id'],
            'vector': embedding,
            'metadata': metadata
        }])
        print(f"Embedded chunk: {chunk['id']}")

def main():
    print("Loading digital twin data...")
    twin_data = load_digital_twin()
    
    print("Preparing chunks for embedding...")
    chunks = prepare_chunks(twin_data)
    
    print(f"Found {len(chunks)} chunks to embed...")
    embed_chunks(chunks)
    
    print("Digital twin successfully embedded into Upstash Vector!")

if __name__ == "__main__":
    main()