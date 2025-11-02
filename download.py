import requests
import os
import time
from pathlib import Path

# Create directory for downloaded texts
OUTPUT_DIR = "slave_narratives"
Path(OUTPUT_DIR).mkdir(exist_ok=True)

# Extended collection: 40 slave narratives
# Format: (gutenberg_id, author, title, year)
NARRATIVES = [
    # TIER 1: Essential/Most Famous (10)
    (23, "Frederick Douglass", "Narrative of the Life of Frederick Douglass", 1845),
    (11030, "Harriet Jacobs", "Incidents in the Life of a Slave Girl", 1861),
    (15399, "Olaudah Equiano", "The Interesting Narrative of the Life of Olaudah Equiano", 1789),
    (12799, "Solomon Northup", "Twelve Years a Slave", 1853),
    (15513, "William Wells Brown", "Narrative of William W. Brown, a Fugitive Slave", 1847),
    (18567, "Harriet Beecher Stowe", "Uncle Tom's Cabin", 1852),
    (10615, "Frederick Douglass", "My Bondage and My Freedom", 1855),
    (10207, "Sojourner Truth", "Narrative of Sojourner Truth", 1850),
    (10088, "Booker T. Washington", "Up From Slavery", 1901),
    (521, "Frederick Douglass", "Life and Times of Frederick Douglass", 1892),
    
    # TIER 2: Important Narratives (15)
    (9845, "Josiah Henson", "The Life of Josiah Henson", 1849),
    (16115, "Henry Box Brown", "Narrative of the Life of Henry Box Brown", 1851),
    (10800, "Moses Roper", "A Narrative of the Adventures and Escape of Moses Roper", 1838),
    (15380, "William and Ellen Craft", "Running a Thousand Miles for Freedom", 1860),
    (22242, "Austin Steward", "Twenty-Two Years a Slave", 1857),
    (13559, "William Grimes", "Life of William Grimes, the Runaway Slave", 1825),
    (30802, "Lewis Clarke", "Narratives of the Sufferings of Lewis and Milton Clarke", 1846),
    (22889, "Charles Ball", "Fifty Years in Chains", 1859),
    (17282, "James W.C. Pennington", "The Fugitive Blacksmith", 1849),
    (14449, "Elizabeth Keckley", "Behind the Scenes", 1868),
    (10615, "Frederick Douglass", "The Heroic Slave", 1853),
    (19944, "Lydia Maria Child", "The Freedmen's Book", 1865),
    (14106, "Lydia Maria Child", "An Appeal in Favor of That Class of Americans Called Africans", 1833),
    (34936, "Jacob D. Green", "Narrative of the Life of J.D. Green, a Runaway Slave", 1864),
    (29854, "John Brown", "Slave Life in Georgia", 1855),
    
    # TIER 3: Additional Important Works (15)
    (10045, "Venture Smith", "A Narrative of the Life and Adventures of Venture", 1798),
    (28656, "Thomas H. Jones", "The Experience of Thomas H. Jones", 1862),
    (16377, "Samuel Ringgold Ward", "Autobiography of a Fugitive Negro", 1855),
    (19721, "Isaac Jefferson", "Memoirs of a Monticello Slave", 1847),
    (26617, "Peter Randolph", "Sketches of Slave Life", 1855),
    (37150, "Louis Hughes", "Thirty Years a Slave", 1897),
    (20579, "Francis Fedric", "Slave Life in Virginia and Kentucky", 1863),
    (34445, "James Mars", "Life of James Mars, a Slave", 1864),
    (26470, "John Thompson", "The Life of John Thompson, a Fugitive Slave", 1856),
    (15076, "William Parker", "The Freedman's Story", 1866),
    (16220, "Kate Drumgoold", "A Slave Girl's Story", 1898),
    (30072, "Andrew Jackson", "Narrative and Writings of Andrew Jackson", 1847),
    (42936, "William J. Anderson", "Life and Narrative of William J. Anderson", 1857),
    (29851, "Bethany Veney", "The Narrative of Bethany Veney", 1889),
    (23465, "Annie L. Burton", "Memories of Childhood's Slavery Days", 1909),
]

def download_gutenberg_text(gutenberg_id, author, title, year):
    """Download a text from Project Gutenberg"""
    
    # Project Gutenberg URL formats to try
    urls_to_try = [
        f"https://www.gutenberg.org/files/{gutenberg_id}/{gutenberg_id}-0.txt",
        f"https://www.gutenberg.org/cache/epub/{gutenberg_id}/pg{gutenberg_id}.txt",
        f"https://www.gutenberg.org/files/{gutenberg_id}/{gutenberg_id}.txt",
    ]
    
    # Create safe filename
    safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).strip()
    safe_author = "".join(c for c in author if c.isalnum() or c in (' ', '-', '_')).strip()
    filename = f"{year} - {safe_author} - {safe_title}.txt"
    filepath = os.path.join(OUTPUT_DIR, filename)
    
    # Skip if already downloaded
    if os.path.exists(filepath):
        print(f"[SKIP] Already exists: {filename}")
        return True
    
    print(f"[DOWNLOADING] {title} by {author} ({year})...", end=" ")
    
    # Try each URL format
    for url in urls_to_try:
        try:
            response = requests.get(url, timeout=30)
            
            if response.status_code == 200:
                # Save the file
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(response.text)
                print(f"SUCCESS")
                return True
                
        except Exception as e:
            continue
    
    # If all URLs failed
    print(f"FAILED - Try manual download from https://www.gutenberg.org/ebooks/{gutenberg_id}")
    
    # Save failed ID for manual download
    with open(os.path.join(OUTPUT_DIR, "_failed_downloads.txt"), 'a') as f:
        f.write(f"{gutenberg_id},{author},{title},{year}\n")
    
    return False

def download_additional_sources():
    """Information about additional sources"""
    print("\n" + "="*70)
    print("ADDITIONAL SOURCES TO EXPAND CORPUS TO 50-100+")
    print("="*70)
    
    print("\nDocumenting the American South (UNC Chapel Hill):")
    print("https://docsouth.unc.edu/neh/")
    print("- North American Slave Narratives collection")
    print("- Searchable database with full texts")
    print("- Can download as HTML/TXT")
    
    print("\nLibrary of Congress - Born in Slavery:")
    print("https://www.loc.gov/collections/slave-narratives-from-the-federal-writers-project-1936-to-1938/")
    print("- 2,300+ WPA slave narrative interviews (1936-1938)")
    print("- Ex-slaves interviewed in their 80s-100s")
    print("- State-by-state organization")
    
    print("\nDigital Library on American Slavery:")
    print("https://library.uncg.edu/slavery/")
    print("- Court petitions and legal documents")
    print("- Complements narrative accounts")
    
    print("\nYale Slavery and Abolition Portal:")
    print("https://slavery.yale.edu/")
    print("- Letters, speeches, legal documents")
    
    print("\nTIP: After hackathon, use web scraping to bulk download UNC collection")

def create_metadata_file():
    """Create comprehensive metadata file"""
    metadata_path = os.path.join(OUTPUT_DIR, "_METADATA.txt")
    
    with open(metadata_path, 'w', encoding='utf-8') as f:
        f.write("SLAVE NARRATIVES COLLECTION - COMPREHENSIVE METADATA\n")
        f.write("="*70 + "\n")
        f.write(f"Total narratives: {len(NARRATIVES)}\n")
        f.write(f"Date range: 1789-1909\n")
        f.write(f"Collection purpose: Academic research tool\n")
        f.write("="*70 + "\n\n")
        
        # Group by tier
        f.write("TIER 1: ESSENTIAL NARRATIVES (Most Famous)\n")
        f.write("-"*70 + "\n")
        for i in range(10):
            gutenberg_id, author, title, year = NARRATIVES[i]
            f.write(f"{i+1}. {author} - {title} ({year})\n")
            f.write(f"   Gutenberg ID: {gutenberg_id}\n")
            f.write(f"   URL: https://www.gutenberg.org/ebooks/{gutenberg_id}\n\n")
        
        f.write("\nTIER 2: IMPORTANT NARRATIVES\n")
        f.write("-"*70 + "\n")
        for i in range(10, 25):
            gutenberg_id, author, title, year = NARRATIVES[i]
            f.write(f"{i+1}. {author} - {title} ({year})\n")
            f.write(f"   Gutenberg ID: {gutenberg_id}\n\n")
        
        f.write("\nTIER 3: ADDITIONAL IMPORTANT WORKS\n")
        f.write("-"*70 + "\n")
        for i in range(25, len(NARRATIVES)):
            gutenberg_id, author, title, year = NARRATIVES[i]
            f.write(f"{i+1}. {author} - {title} ({year})\n")
            f.write(f"   Gutenberg ID: {gutenberg_id}\n\n")
        
        # Statistics
        f.write("\n" + "="*70 + "\n")
        f.write("CORPUS STATISTICS\n")
        f.write("="*70 + "\n")
        
        years = [year for _, _, _, year in NARRATIVES]
        authors = list(set([author for _, author, _, _ in NARRATIVES]))
        
        f.write(f"Unique authors: {len(authors)}\n")
        f.write(f"Date range: {min(years)}-{max(years)}\n")
        f.write(f"Pre-1850: {len([y for y in years if y < 1850])}\n")
        f.write(f"1850-1865 (Civil War era): {len([y for y in years if 1850 <= y <= 1865])}\n")
        f.write(f"Post-1865 (Reconstruction+): {len([y for y in years if y > 1865])}\n")
        
        # Gender analysis (approximate)
        women_authors = ["Harriet Jacobs", "Harriet Beecher Stowe", "Sojourner Truth", 
                        "Elizabeth Keckley", "Lydia Maria Child", "Kate Drumgoold", 
                        "Bethany Veney", "Annie L. Burton"]
        f.write(f"\nWomen's narratives: ~{len([a for a in authors if a in women_authors])}\n")
        f.write(f"Men's narratives: ~{len(authors) - len([a for a in authors if a in women_authors])}\n")

def main():
    print("="*70)
    print("COMPREHENSIVE SLAVE NARRATIVE DOWNLOADER")
    print("="*70)
    print(f"\nDownloading {len(NARRATIVES)} texts from Project Gutenberg...")
    print(f"Saving to: {os.path.abspath(OUTPUT_DIR)}\n")
    print("This will take approximately 2-3 minutes...\n")
    
    success_count = 0
    failed_count = 0
    
    for i, (gutenberg_id, author, title, year) in enumerate(NARRATIVES, 1):
        print(f"[{i}/{len(NARRATIVES)}] ", end="")
        result = download_gutenberg_text(gutenberg_id, author, title, year)
        if result:
            success_count += 1
        else:
            failed_count += 1
        
        # Be nice to Project Gutenberg servers
        time.sleep(2)
    
    print("\n" + "="*70)
    print(f"DOWNLOAD COMPLETE")
    print("="*70)
    print(f"Successful: {success_count}")
    print(f"Failed: {failed_count}")
    
    if failed_count > 0:
        print(f"\nFailed downloads saved to: _failed_downloads.txt")
        print("You can manually download these from Project Gutenberg")
    
    print(f"\nTotal files in directory: {len([f for f in os.listdir(OUTPUT_DIR) if f.endswith('.txt') and not f.startswith('_')])}")
    print("="*70)
    
    # Create metadata
    create_metadata_file()
    print(f"\nMetadata saved to: {os.path.join(OUTPUT_DIR, '_METADATA.txt')}")
    
    # Show additional sources
    download_additional_sources()
    
    print("\n" + "="*70)
    print("NEXT STEPS")
    print("="*70)
    print("1. Review downloaded files in the 'slave_narratives' folder")
    print("2. Manually download any failed texts from Project Gutenberg")
    print("3. Consider adding WPA narratives for 100+ corpus")
    print("4. Begin processing texts for RAG implementation")
    print("="*70)

if __name__ == "__main__":
    main()