from django.core.management.base import BaseCommand
import requests
from bs4 import BeautifulSoup, Comment
from NoteMaker.myutils import pc, index
import uuid
import time
import re

class Command(BaseCommand):
    help = 'Crawl TFT/Golden Spatula data and upload to Pinecone'

    def add_arguments(self, parser):
        parser.add_argument('url', type=str, help='The URL to crawl')
        parser.add_argument('--namespace', type=str, default='game_mechanics', help='Pinecone namespace')

    def handle(self, *args, **options):
        url = options['url']
        namespace = options['namespace']
        
        self.stdout.write(f"Starting crawl for {url}...")
        
        try:
            # 1. Fetch Content
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            # 2. Parse Content
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove noise elements
            for element in soup(["script", "style", "nav", "footer", "header", "aside", "iframe", "noscript", "meta", "link"]):
                element.decompose()
            
            # Remove comments
            for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
                comment.extract()

            # Try to find main content
            # Common class names/ids for main content
            content_selectors = [
                'article', 'main', 
                {'class_': re.compile(r'content|article|post|detail|main|news_con', re.I)},
                {'id': re.compile(r'content|article|post|detail|main', re.I)}
            ]
            
            main_content = None
            for selector in content_selectors:
                if isinstance(selector, str):
                    found = soup.find(selector)
                else:
                    found = soup.find(**selector)
                
                if found:
                    # Check if it has enough text to be considered main content
                    if len(found.get_text(strip=True)) > 200:
                        main_content = found
                        self.stdout.write(f"Found main content using selector: {selector}")
                        break
            
            if not main_content:
                self.stdout.write("No specific main content area found, using cleaned body.")
                main_content = soup.body or soup

            # Get text and clean it
            text = main_content.get_text(separator='\n')
            
            # Advanced cleaning
            lines = []
            for line in text.splitlines():
                line = line.strip()
                # Filter out short lines that look like menu items or noise (unless they end with punctuation)
                if len(line) > 10 or (len(line) > 2 and line[-1] in '.!?。！？'):
                    lines.append(line)
            
            text_content = '\n'.join(lines)
            
            if len(text_content) < 100:
                 self.stdout.write(self.style.WARNING("Extracted text is very short. The page might be dynamic or empty."))

            self.stdout.write(f"Extracted {len(text_content)} characters of clean text.")
            
            # 3. Chunking
            chunk_size = 1000
            # Overlap chunks slightly for better context
            overlap = 100
            text_chunks = []
            for i in range(0, len(text_content), chunk_size - overlap):
                chunk = text_content[i:i + chunk_size]
                if len(chunk) > 50: # Ignore very small chunks
                    text_chunks.append(chunk)
            
            self.stdout.write(f"Split into {len(text_chunks)} chunks.")
            
            # 4. Embed and Upsert
            vectors = []
            batch_size = 10
            
            for i, chunk in enumerate(text_chunks):
                self.stdout.write(f"Processing chunk {i+1}/{len(text_chunks)}...")
                
                try:
                    embedding = pc.inference.embed(
                        model="llama-text-embed-v2",
                        inputs=[chunk],
                        parameters={"input_type": "passage"}
                    )[0].values
                    
                    vector_id = f"crawl_{uuid.uuid4()}"
                    
                    vectors.append({
                        "id": vector_id,
                        "values": embedding,
                        "metadata": {
                            "text": chunk,
                            "source": url,
                            "type": "web_crawl",
                            "title": soup.title.string if soup.title else "No Title"
                        }
                    })
                    
                    if len(vectors) >= batch_size:
                        index.upsert(vectors=vectors, namespace=namespace)
                        self.stdout.write(f"Upserted batch of {len(vectors)} vectors.")
                        vectors = []
                        time.sleep(1)
                        
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Error processing chunk {i}: {str(e)}"))
            
            if vectors:
                index.upsert(vectors=vectors, namespace=namespace)
                self.stdout.write(f"Upserted final batch of {len(vectors)} vectors.")
                
            self.stdout.write(self.style.SUCCESS("Crawling and indexing completed successfully!"))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Failed to crawl: {str(e)}"))
