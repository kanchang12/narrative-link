import google.generativeai as genai
import json
import os
import time
from pathlib import Path

# Configure Gemini
GOOGLE_API_KEY = "AIzaSyCwRjTU7mZKNCqCBp74WIylQnR9Go2DqUE"
if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY environment variable not set")

genai.configure(api_key=GOOGLE_API_KEY)

INPUT_FILE = 'processed_data/processed_chunks.json'
OUTPUT_FILE = 'processed_data/chunks_with_embeddings.json'

def generate_embeddings_batch(chunks, batch_size=100):
    """Generate embeddings for chunks in batches"""
    
    print(f"Generating embeddings for {len(chunks)} chunks...")
    print("This will take approximately 10-20 minutes...\n")
    
    chunks_with_embeddings = []
    failed = 0
    
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i + batch_size]
        batch_num = (i // batch_size) + 1
        total_batches = (len(chunks) + batch_size - 1) // batch_size
        
        print(f"Processing batch {batch_num}/{total_batches} ({len(batch)} chunks)...")
        
        for j, chunk in enumerate(batch):
            try:
                # Generate embedding for this chunk
                result = genai.embed_content(
                    model="models/text-embedding-004",
                    content=chunk['text'],
                    task_type="retrieval_document"
                )
                
                # Add embedding to chunk
                chunk_with_embedding = chunk.copy()
                chunk_with_embedding['embedding'] = result['embedding']
                chunks_with_embeddings.append(chunk_with_embedding)
                
                # Progress indicator
                if (j + 1) % 10 == 0:
                    print(f"  Completed {i + j + 1}/{len(chunks)}")
                
                # Rate limiting - be nice to API
                time.sleep(0.5)
                
            except Exception as e:
                print(f"  ERROR on chunk {i + j}: {str(e)}")
                failed += 1
                # Add chunk without embedding so we don't lose it
                chunks_with_embeddings.append(chunk)
                time.sleep(2)  # Wait longer after error
        
        # Save intermediate results after each batch
        print(f"  Saving intermediate results...")
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(chunks_with_embeddings, f)
        
        print(f"  Batch {batch_num} complete. Saved to {OUTPUT_FILE}\n")
    
    print(f"\nEmbedding generation complete!")
    print(f"Successfully processed: {len(chunks_with_embeddings) - failed}")
    print(f"Failed: {failed}")
    print(f"Output saved to: {OUTPUT_FILE}")
    
    return chunks_with_embeddings

def verify_embeddings(chunks_with_embeddings):
    """Verify embedding quality"""
    
    print("\nVerifying embeddings...")
    
    has_embedding = sum(1 for c in chunks_with_embeddings if 'embedding' in c)
    embedding_dims = []
    
    for chunk in chunks_with_embeddings:
        if 'embedding' in chunk:
            embedding_dims.append(len(chunk['embedding']))
    
    print(f"Chunks with embeddings: {has_embedding}/{len(chunks_with_embeddings)}")
    if embedding_dims:
        print(f"Embedding dimension: {embedding_dims[0]}")
        print(f"All embeddings same size: {len(set(embedding_dims)) == 1}")

def main():
    # Check if input exists
    if not os.path.exists(INPUT_FILE):
        print(f"ERROR: {INPUT_FILE} not found!")
        print("Run process_texts.py first!")
        return
    
    # Load processed chunks
    print(f"Loading chunks from {INPUT_FILE}...")
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        chunks = json.load(f)
    
    print(f"Loaded {len(chunks)} chunks")
    
    # Check if embeddings already exist
    if os.path.exists(OUTPUT_FILE):
        response = input(f"\n{OUTPUT_FILE} already exists. Overwrite? (yes/no): ")
        if response.lower() != 'yes':
            print("Aborted.")
            return
    
    # Generate embeddings
    chunks_with_embeddings = generate_embeddings_batch(chunks)
    
    # Verify
    verify_embeddings(chunks_with_embeddings)
    
    # Calculate file size
    file_size_mb = os.path.getsize(OUTPUT_FILE) / (1024 * 1024)
    print(f"\nOutput file size: {file_size_mb:.2f} MB")

if __name__ == "__main__":
    main()