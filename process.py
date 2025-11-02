import os
import re
import json
from pathlib import Path

INPUT_DIR = "slave_narratives"
OUTPUT_DIR = "processed_data"
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

def clean_gutenberg_text(text):
    """Remove Project Gutenberg headers and footers"""
    
    # Find start of actual content
    start_markers = [
        "*** START OF THE PROJECT GUTENBERG",
        "*** START OF THIS PROJECT GUTENBERG",
        "*END*THE SMALL PRINT",
    ]
    
    for marker in start_markers:
        if marker in text:
            text = text.split(marker)[1]
            break
    
    # Find end of actual content
    end_markers = [
        "*** END OF THE PROJECT GUTENBERG",
        "*** END OF THIS PROJECT GUTENBERG",
        "End of the Project Gutenberg",
    ]
    
    for marker in end_markers:
        if marker in text:
            text = text.split(marker)[0]
            break
    
    # Clean up excessive whitespace
    text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)
    text = re.sub(r' +', ' ', text)
    
    return text.strip()

def extract_metadata_from_filename(filename):
    """Extract author, title, year from filename"""
    # Format: YEAR - AUTHOR - TITLE.txt
    parts = filename.replace('.txt', '').split(' - ')
    
    if len(parts) >= 3:
        year = parts[0].strip()
        author = parts[1].strip()
        title = ' - '.join(parts[2:]).strip()
    else:
        year = "Unknown"
        author = "Unknown"
        title = filename.replace('.txt', '')
    
    return {
        'year': year,
        'author': author,
        'title': title,
        'filename': filename
    }

def chunk_text(text, chunk_size=CHUNK_SIZE, overlap=CHUNK_OVERLAP):
    """Split text into overlapping chunks"""
    words = text.split()
    chunks = []
    
    for i in range(0, len(words), chunk_size - overlap):
        chunk = ' '.join(words[i:i + chunk_size])
        if len(chunk.strip()) > 100:  # Skip tiny chunks
            chunks.append(chunk)
    
    return chunks

def process_all_narratives():
    """Process all downloaded narratives"""
    
    Path(OUTPUT_DIR).mkdir(exist_ok=True)
    
    all_chunks = []
    
    txt_files = [f for f in os.listdir(INPUT_DIR) 
                 if f.endswith('.txt') and not f.startswith('_')]
    
    print(f"Processing {len(txt_files)} narratives...")
    
    for i, filename in enumerate(txt_files, 1):
        print(f"[{i}/{len(txt_files)}] Processing: {filename}")
        
        filepath = os.path.join(INPUT_DIR, filename)
        
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                text = f.read()
            
            # Clean text
            cleaned_text = clean_gutenberg_text(text)
            
            # Extract metadata
            metadata = extract_metadata_from_filename(filename)
            
            # Chunk text
            chunks = chunk_text(cleaned_text)
            
            # Add metadata to each chunk
            for chunk_idx, chunk in enumerate(chunks):
                all_chunks.append({
                    'id': f"{filename}_{chunk_idx}",
                    'text': chunk,
                    'author': metadata['author'],
                    'title': metadata['title'],
                    'year': metadata['year'],
                    'filename': metadata['filename'],
                    'chunk_index': chunk_idx,
                    'total_chunks': len(chunks)
                })
            
            print(f"  Created {len(chunks)} chunks")
            
        except Exception as e:
            print(f"  ERROR: {str(e)}")
    
    # Save processed data
    output_file = os.path.join(OUTPUT_DIR, 'processed_chunks.json')
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_chunks, f, indent=2)
    
    print(f"\nProcessing complete!")
    print(f"Total chunks created: {len(all_chunks)}")
    print(f"Saved to: {output_file}")
    
    # Create summary
    authors = set(chunk['author'] for chunk in all_chunks)
    years = set(chunk['year'] for chunk in all_chunks)
    
    summary = {
        'total_chunks': len(all_chunks),
        'total_narratives': len(txt_files),
        'unique_authors': len(authors),
        'year_range': f"{min(years)} - {max(years)}",
        'avg_chunks_per_narrative': len(all_chunks) // len(txt_files)
    }
    
    summary_file = os.path.join(OUTPUT_DIR, 'summary.json')
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2)
    
    print(f"\nSummary saved to: {summary_file}")
    return all_chunks

if __name__ == "__main__":
    process_all_narratives()