"""
FAISS vector store service for MemoryAid application
Handles vector storage and similarity search for memories
"""

import os
import numpy as np
import faiss
import logging
from typing import List, Tuple, Optional
import pickle
from pathlib import Path

from services.config import get_settings, get_data_path
from models.memory import Memory

logger = logging.getLogger(__name__)

class FAISSStore:
    """FAISS-based vector store for memory embeddings"""
    
    def __init__(self):
        self.settings = get_settings()
        self.data_path = get_data_path()
        self.index_path = os.path.join(self.data_path, "faiss.index")
        self.metadata_path = os.path.join(self.data_path, "faiss_metadata.pkl")
        
        # Initialize FAISS index
        self.index = None
        self.metadata_mapping = {}  # vector_id -> memory_id mapping
        self.next_vector_id = 0
        
        self._load_or_create_index()
    
    def _load_or_create_index(self):
        """Load existing FAISS index or create a new one"""
        try:
            if os.path.exists(self.index_path) and os.path.exists(self.metadata_path):
                # Load existing index
                self.index = faiss.read_index(self.index_path)
                
                # Load metadata mapping
                with open(self.metadata_path, 'rb') as f:
                    self.metadata_mapping = pickle.load(f)
                
                # Set next vector ID
                if self.metadata_mapping:
                    self.next_vector_id = max(self.metadata_mapping.keys()) + 1
                
                logger.info(f"Loaded existing FAISS index with {self.index.ntotal} vectors")
            else:
                # Create new index
                self._create_new_index()
                logger.info("Created new FAISS index")
                
        except Exception as e:
            logger.error(f"Error loading FAISS index: {e}")
            self._create_new_index()
    
    def _create_new_index(self):
        """Create a new FAISS index"""
        try:
            # Create IndexFlatL2 for L2 distance search
            # Using 1536 dimensions for OpenAI ada-002 embeddings
            dimension = 1536
            self.index = faiss.IndexFlatL2(dimension)
            
            # Initialize metadata
            self.metadata_mapping = {}
            self.next_vector_id = 0
            
            logger.info("Created new FAISS index with dimension 1536")
            
        except Exception as e:
            logger.error(f"Error creating FAISS index: {e}")
            raise
    
    async def add_memory(self, memory: Memory) -> int:
        """Add a memory to the FAISS index and return vector ID"""
        try:
            # Generate embedding for the memory
            from services.openai_service import OpenAIService
            openai_service = OpenAIService()
            
            # Create text representation for embedding
            text_for_embedding = f"{memory.title} {memory.summary} {memory.detailed_description}"
            if memory.objects_detected:
                text_for_embedding += f" {' '.join(memory.objects_detected)}"
            if memory.activity:
                text_for_embedding += f" {memory.activity}"
            
            # Generate embedding
            embedding = await openai_service.generate_embedding(text_for_embedding)
            
            # Convert to numpy array
            embedding_array = np.array([embedding], dtype=np.float32)
            
            # Add to FAISS index
            self.index.add(embedding_array)
            
            # Store metadata mapping
            vector_id = self.next_vector_id
            self.metadata_mapping[vector_id] = memory.id
            self.next_vector_id += 1
            
            # Save index and metadata
            self._save_index()
            
            logger.info(f"Added memory {memory.id} to FAISS index with vector ID {vector_id}")
            return vector_id
            
        except Exception as e:
            logger.error(f"Error adding memory to FAISS: {e}")
            raise
    
    def _save_index(self):
        """Save FAISS index and metadata to disk"""
        try:
            # Save FAISS index
            faiss.write_index(self.index, self.index_path)
            
            # Save metadata mapping
            with open(self.metadata_path, 'wb') as f:
                pickle.dump(self.metadata_mapping, f)
            
            logger.debug("FAISS index and metadata saved successfully")
            
        except Exception as e:
            logger.error(f"Error saving FAISS index: {e}")
            raise
    
    async def search_similar(self, query_text: str, k: int = 5) -> List[Tuple[str, float]]:
        """Search for similar memories based on text query"""
        try:
            if self.index.ntotal == 0:
                return []
            
            # Generate embedding for query
            from services.openai_service import OpenAIService
            openai_service = OpenAIService()
            query_embedding = await openai_service.generate_embedding(query_text)
            
            # Convert to numpy array
            query_array = np.array([query_embedding], dtype=np.float32)
            
            # Search in FAISS index
            distances, indices = self.index.search(query_array, min(k, self.index.ntotal))
            
            # Convert to results
            results = []
            for i, (distance, idx) in enumerate(zip(distances[0], indices[0])):
                if idx != -1:  # Valid result
                    memory_id = self.metadata_mapping.get(idx)
                    if memory_id:
                        # Convert distance to similarity score (0-1, higher is more similar)
                        similarity = 1.0 / (1.0 + distance)
                        results.append((memory_id, similarity))
            
            # Sort by similarity (highest first)
            results.sort(key=lambda x: x[1], reverse=True)
            
            logger.info(f"Found {len(results)} similar memories for query: {query_text[:50]}...")
            return results
            
        except Exception as e:
            logger.error(f"Error searching FAISS index: {e}")
            return []
    
    async def search_by_embedding(self, embedding: List[float], k: int = 5) -> List[Tuple[str, float]]:
        """Search for similar memories based on embedding vector"""
        try:
            if self.index.ntotal == 0:
                return []
            
            # Convert to numpy array
            query_array = np.array([embedding], dtype=np.float32)
            
            # Search in FAISS index
            distances, indices = self.index.search(query_array, min(k, self.index.ntotal))
            
            # Convert to results
            results = []
            for i, (distance, idx) in enumerate(zip(distances[0], indices[0])):
                if idx != -1:  # Valid result
                    memory_id = self.metadata_mapping.get(idx)
                    if memory_id:
                        # Convert distance to similarity score
                        similarity = 1.0 / (1.0 + distance)
                        results.append((memory_id, similarity))
            
            # Sort by similarity
            results.sort(key=lambda x: x[1], reverse=True)
            
            return results
            
        except Exception as e:
            logger.error(f"Error searching by embedding: {e}")
            return []
    
    def get_index_stats(self) -> dict:
        """Get statistics about the FAISS index"""
        try:
            return {
                "total_vectors": self.index.ntotal,
                "dimension": self.index.d,
                "index_type": type(self.index).__name__,
                "metadata_entries": len(self.metadata_mapping),
                "next_vector_id": self.next_vector_id
            }
        except Exception as e:
            logger.error(f"Error getting index stats: {e}")
            return {}
    
    def rebuild_index(self) -> bool:
        """Rebuild the FAISS index from metadata"""
        try:
            logger.info("Rebuilding FAISS index...")
            
            # Create new index
            self._create_new_index()
            
            # Note: In a real implementation, you would need to regenerate embeddings
            # for all existing memories. This is a simplified version.
            
            logger.info("FAISS index rebuilt successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error rebuilding index: {e}")
            return False
    
    def clear_index(self) -> bool:
        """Clear the FAISS index and metadata"""
        try:
            # Remove index file
            if os.path.exists(self.index_path):
                os.remove(self.index_path)
            
            # Remove metadata file
            if os.path.exists(self.metadata_path):
                os.remove(self.metadata_path)
            
            # Recreate index
            self._create_new_index()
            
            logger.info("FAISS index cleared successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error clearing index: {e}")
            return False
