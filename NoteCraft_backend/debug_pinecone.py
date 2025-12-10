import os
import sys
import django
from dotenv import load_dotenv

# Setup Django environment
sys.path.append('/app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'NoteCraft_backend.settings')
django.setup()

from NoteMaker.myutils import pc, index

def debug_pinecone():
    print("Checking Pinecone Index Stats...")
    try:
        stats = index.describe_index_stats()
        print(f"Index Stats: {stats}")
        
        namespaces = stats.get('namespaces', {})
        if not namespaces:
            print("WARNING: No namespaces found in index! The index is empty.")
            return

        print("\nTesting Retrieval...")
        # Test query similar to user's input
        test_query = "金铲铲之战双城传说版本英雄汇总介绍"
        print(f"Querying for: '{test_query}'")
        
        # Generate embedding
        embedding = pc.inference.embed(
            model="llama-text-embed-v2",
            inputs=[test_query],
            parameters={"input_type": "query"}
        )[0].values
        
        # Query 'game_mechanics' namespace
        results = index.query(
            namespace='game_mechanics',
            vector=embedding,
            top_k=3,
            include_metadata=True
        )
        
        print("\nResults from 'game_mechanics':")
        if results.matches:
            for i, match in enumerate(results.matches):
                print(f"\nMatch {i+1} (Score: {match.score}):")
                print(f"Text snippet: {match.metadata.get('text', '')[:200]}...")
        else:
            print("No matches found.")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    debug_pinecone()
