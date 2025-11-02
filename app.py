from flask import Flask, request, jsonify, render_template
import google.generativeai as genai
import json
import os
import numpy as np
from typing import List, Dict



app = Flask(__name__, static_folder='static')

# Configure Gemini
GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)

# Load processed data with embeddings
EMBEDDINGS_FILE = 'processed_data/chunks_with_embeddings.json'
chunks_data = []

def load_data():
    global chunks_data
    if os.path.exists(EMBEDDINGS_FILE):
        print(f"Loading embeddings from {EMBEDDINGS_FILE}...")
        with open(EMBEDDINGS_FILE, 'r', encoding='utf-8') as f:
            chunks_data = json.load(f)
        
        # Verify embeddings exist
        has_embeddings = sum(1 for c in chunks_data if 'embedding' in c)
        print(f"Loaded {len(chunks_data)} chunks ({has_embeddings} with embeddings)")
        
        if has_embeddings == 0:
            print("WARNING: No embeddings found! Run embedding_generator.py first!")
    else:
        print(f"WARNING: {EMBEDDINGS_FILE} not found! Run embedding_generator.py first!")

def cosine_similarity(vec1, vec2):
    """Calculate cosine similarity between two vectors"""
    vec1 = np.array(vec1)
    vec2 = np.array(vec2)
    
    dot_product = np.dot(vec1, vec2)
    norm1 = np.linalg.norm(vec1)
    norm2 = np.linalg.norm(vec2)
    
    if norm1 == 0 or norm2 == 0:
        return 0
    
    return dot_product / (norm1 * norm2)

def semantic_search(query: str, top_k: int = 5) -> List[Dict]:
    """Semantic search using pre-computed embeddings"""
    
    if not chunks_data:
        return []
    
    # Check if we have embeddings
    has_embeddings = any('embedding' in chunk for chunk in chunks_data)
    
    if not has_embeddings:
        print("WARNING: No embeddings found, falling back to keyword search")
        return keyword_search(query, top_k)
    
    try:
        # Get query embedding
        query_result = genai.embed_content(
            model="models/text-embedding-004",
            content=query,
            task_type="retrieval_query"
        )
        query_embedding = query_result['embedding']
        
        # Calculate similarities
        results = []
        for chunk in chunks_data:
            if 'embedding' not in chunk:
                continue
            
            similarity = cosine_similarity(query_embedding, chunk['embedding'])
            results.append({
                'chunk': chunk,
                'score': similarity
            })
        
        # Sort by similarity
        results.sort(key=lambda x: x['score'], reverse=True)
        
        print(f"Top 5 similarity scores: {[r['score'] for r in results[:5]]}")
        
        return [r['chunk'] for r in results[:top_k]]
    
    except Exception as e:
        print(f"Semantic search error: {str(e)}")
        # Fallback to keyword search
        return keyword_search(query, top_k)

def keyword_search(query: str, top_k: int = 5) -> List[Dict]:
    """Fallback keyword-based search"""
    results = []
    query_lower = query.lower()
    query_words = set(query_lower.split())
    
    for chunk in chunks_data:
        chunk_lower = chunk['text'].lower()
        chunk_words = set(chunk_lower.split())
        matches = len(query_words.intersection(chunk_words))
        
        if matches > 0:
            results.append({
                'chunk': chunk,
                'score': matches
            })
    
    results.sort(key=lambda x: x['score'], reverse=True)
    return [r['chunk'] for r in results[:top_k]]

def generate_response(query: str, context_chunks: List[Dict]) -> str:
    """Generate response using Gemini with retrieved context"""
    
    if not context_chunks:
        return "I couldn't find relevant passages in the slave narratives to answer your question."
    
    # Build context from chunks
    context = "\n\n---\n\n".join([
        f"From '{chunk['title']}' by {chunk['author']} ({chunk['year']}):\n{chunk['text']}"
        for chunk in context_chunks
    ])
    
    # Create prompt
    prompt = f"""You are a scholarly assistant specializing in slave narratives and abolitionist literature.

Based on the following passages from historical slave narratives, answer the user's question.

IMPORTANT RULES:
1. Only use information from the provided passages
2. Cite your sources by mentioning the author and title
3. If comparing across narratives, explicitly note the differences
4. Maintain respectful, academic tone when discussing trauma and violence
5. If the passages don't contain enough information, say so

PASSAGES:
{context}

USER QUESTION: {query}

Please provide a thoughtful, well-cited response:"""

    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error generating response: {str(e)}"

@app.route('/')
def index():
    return render_template('index.html') 

@app.route('/api/search', methods=['POST'])
def search():
    """Search endpoint"""
    data = request.json
    query = data.get('query', '')
    
    if not query:
        return jsonify({'error': 'No query provided'}), 400
    
    # Get relevant chunks using semantic search
    relevant_chunks = semantic_search(query, top_k=5)
    
    # Generate response
    answer = generate_response(query, relevant_chunks)
    
    # Format sources
    sources = []
    seen = set()
    for chunk in relevant_chunks:
        key = f"{chunk['author']}|{chunk['title']}"
        if key not in seen:
            sources.append({
                'author': chunk['author'],
                'title': chunk['title'],
                'year': chunk['year']
            })
            seen.add(key)
    
    return jsonify({
        'answer': answer,
        'sources': sources,
        'relevant_passages': [
            {
                'text': chunk['text'][:300] + '...',
                'author': chunk['author'],
                'title': chunk['title'],
                'year': chunk['year']
            }
            for chunk in relevant_chunks[:3]
        ]
    })

@app.route('/api/stats', methods=['GET'])
def stats():
    """Get corpus statistics"""
    if not chunks_data:
        return jsonify({'error': 'No data loaded'}), 500
    
    authors = set(chunk['author'] for chunk in chunks_data)
    years = set(chunk['year'] for chunk in chunks_data)
    narratives = set(chunk['filename'] for chunk in chunks_data)
    has_embeddings = sum(1 for chunk in chunks_data if 'embedding' in chunk)
    
    return jsonify({
        'total_chunks': len(chunks_data),
        'total_narratives': len(narratives),
        'unique_authors': len(authors),
        'year_range': f"{min(years)} - {max(years)}",
        'authors': sorted(list(authors)),
        'embeddings_ready': has_embeddings > 0
    })

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'chunks_loaded': len(chunks_data),
        'embeddings_available': any('embedding' in c for c in chunks_data)
    })

load_data()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)
