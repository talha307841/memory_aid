#!/usr/bin/env python3
"""
MemoryAid Demo Script
Creates sample memories and demonstrates the application functionality
"""

import asyncio
import os
import sys
from datetime import datetime, timedelta
import logging

# Add the api directory to the path so we can import services
sys.path.append(os.path.join(os.path.dirname(__file__), 'api'))

from services.memory_service import MemoryService
from services.openai_service import OpenAIService
from services.faiss_store import FAISSStore
from services.config import get_settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def run_demo():
    """Run the MemoryAid demo"""
    print("🚀 MemoryAid Demo Starting...")
    print("=" * 50)
    
    try:
        # Check environment
        print("📋 Checking environment...")
        settings = get_settings()
        print(f"   Demo mode: {settings.demo_mode}")
        print(f"   Capture interval: {settings.capture_interval_seconds}s")
        print(f"   Storage path: {settings.storage_path}")
        
        # Initialize services
        print("\n🔧 Initializing services...")
        memory_service = MemoryService()
        openai_service = OpenAIService()
        faiss_store = FAISSStore()
        
        # Check current state
        current_memories = memory_service.get_memories_count()
        print(f"   Current memories: {current_memories}")
        
        # Create sample memories if none exist
        if current_memories == 0:
            print("\n📸 Creating sample memories...")
            await create_sample_memories(memory_service)
        else:
            print(f"\n✅ Found {current_memories} existing memories")
        
        # Run sample queries
        print("\n🔍 Running sample queries...")
        await run_sample_queries(memory_service, openai_service, faiss_store)
        
        # Show statistics
        print("\n📊 Final Statistics...")
        await show_statistics(memory_service, faiss_store)
        
        print("\n🎉 Demo completed successfully!")
        
    except Exception as e:
        logger.error(f"Demo failed: {e}")
        print(f"\n❌ Demo failed: {e}")
        return False
    
    return True

async def create_sample_memories(memory_service: MemoryService):
    """Create sample memories for demonstration"""
    print("   Creating 5 sample memories...")
    
    # Create memories with different timestamps (past hour)
    base_time = datetime.now() - timedelta(hours=1)
    
    for i in range(5):
        try:
            print(f"     Creating memory {i+1}/5...")
            
            # Simulate capture
            memory_id = await memory_service.simulate_capture()
            
            # Update timestamp to be in the past
            # Note: This is a simplified approach. In a real implementation,
            # you'd need to modify the database directly or add a method to update timestamps
            
            print(f"       Created: {memory_id}")
            
            # Small delay between captures
            await asyncio.sleep(1)
            
        except Exception as e:
            print(f"       Error creating memory {i+1}: {e}")
    
    print("   Sample memories created!")

async def run_sample_queries(memory_service: MemoryService, openai_service: OpenAIService, faiss_store: FAISSStore):
    """Run sample queries to demonstrate functionality"""
    
    # Sample queries
    queries = [
        "Where did I put my keys?",
        "What happened this morning?",
        "Show me recent memories",
        "What objects did I see today?",
        "Find memories from the kitchen"
    ]
    
    print(f"   Running {len(queries)} sample queries...")
    
    for i, query in enumerate(queries, 1):
        try:
            print(f"\n     Query {i}: '{query}'")
            
            # Search for relevant memories
            relevant_memories = await faiss_store.search_similar(query, k=3)
            
            if relevant_memories:
                print(f"       Found {len(relevant_memories)} relevant memories:")
                for memory_id, similarity in relevant_memories[:2]:  # Show top 2
                    memory = await memory_service.get_memory_by_id(memory_id)
                    if memory:
                        print(f"         - {memory.title} (similarity: {similarity:.2f})")
            else:
                print("       No relevant memories found")
            
            # Small delay between queries
            await asyncio.sleep(0.5)
            
        except Exception as e:
            print(f"       Error processing query: {e}")
    
    print("   Sample queries completed!")

async def show_statistics(memory_service: MemoryService, faiss_store: FAISSStore):
    """Show final statistics"""
    try:
        # Memory count
        memories_count = memory_service.get_memories_count()
        print(f"   Total memories: {memories_count}")
        
        # Last capture time
        last_capture = memory_service.get_last_capture_time()
        if last_capture:
            print(f"   Last capture: {last_capture.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # FAISS index stats
        faiss_stats = faiss_store.get_index_stats()
        print(f"   FAISS vectors: {faiss_stats.get('total_vectors', 0)}")
        print(f"   Index dimension: {faiss_stats.get('dimension', 'N/A')}")
        
        # Storage usage
        settings = get_settings()
        storage_path = settings.storage_path
        if os.path.exists(storage_path):
            total_size = sum(
                os.path.getsize(os.path.join(storage_path, f))
                for f in os.listdir(storage_path)
                if os.path.isfile(os.path.join(storage_path, f))
            )
            print(f"   Storage usage: {total_size / (1024*1024):.2f} MB")
        
    except Exception as e:
        print(f"   Error getting statistics: {e}")

async def test_individual_services():
    """Test individual services separately"""
    print("\n🧪 Testing individual services...")
    
    try:
        # Test OpenAI service
        print("   Testing OpenAI service...")
        openai_service = OpenAIService()
        
        # Test embedding generation
        test_text = "This is a test query for memory search"
        embedding = await openai_service.generate_embedding(test_text)
        print(f"     Embedding generated: {len(embedding)} dimensions")
        
        # Test FAISS store
        print("   Testing FAISS store...")
        faiss_store = FAISSStore()
        stats = faiss_store.get_index_stats()
        print(f"     FAISS index: {stats.get('total_vectors', 0)} vectors")
        
        # Test memory service
        print("   Testing memory service...")
        memory_service = MemoryService()
        count = memory_service.get_memories_count()
        print(f"     Memory count: {count}")
        
        print("   All services working correctly!")
        
    except Exception as e:
        print(f"   Service test failed: {e}")

def main():
    """Main entry point"""
    print("MemoryAid Demo Runner")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists('api'):
        print("❌ Error: 'api' directory not found!")
        print("   Please run this script from the root of the MemoryAid project.")
        return 1
    
    # Check environment file
    env_file = '.env'
    if not os.path.exists(env_file):
        print(f"⚠️  Warning: {env_file} file not found!")
        print("   Please create a .env file with your OpenAI API key and other settings.")
        print("   See env.example for reference.")
        return 1
    
    # Run the demo
    success = asyncio.run(run_demo())
    
    if success:
        print("\n✅ Demo completed successfully!")
        print("\nNext steps:")
        print("1. Start the backend: cd api && uvicorn main:app --reload")
        print("2. Start the frontend: cd web && npm run dev")
        print("3. Visit http://localhost:3000 to use the web interface")
        return 0
    else:
        print("\n❌ Demo failed!")
        return 1

if __name__ == "__main__":
    exit(main())
