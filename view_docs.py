"""View documents in the knowledge base."""
from retriever import HybridRetriever

def view_all_docs():
    r = HybridRetriever()
    docs = r.collection.get(include=['documents', 'metadatas'])
    
    if not docs['documents']:
        print("No documents in knowledge base.")
        return
    
    print(f"\n📚 Found {len(docs['documents'])} document(s):\n")
    print("="*60)
    
    for i in range(len(docs['ids'])):
        print(f"\n📄 Document {i+1}")
        print(f"   ID: {docs['ids'][i]}")
        if docs['metadatas'][i]:
            print(f"   Source: {docs['metadatas'][i].get('source', 'N/A')}")
        print(f"\n   Content:\n   {docs['documents'][i][:500]}...")
        print("-"*60)

if __name__ == "__main__":
    view_all_docs()
