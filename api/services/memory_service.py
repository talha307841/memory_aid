"""
Memory service for MemoryAid application
Handles image capture, processing, storage, and retrieval
"""

import os
import cv2
import numpy as np
from datetime import datetime, timedelta
from typing import List, Optional, Tuple
import logging
from PIL import Image
import json
import sqlite3
from pathlib import Path

from models.memory import Memory, MemoryCreate, MemorySearchResult
from services.openai_service import OpenAIService
from services.faiss_store import FAISSStore
from services.config import get_settings, get_storage_path, get_data_path

logger = logging.getLogger(__name__)

class MemoryService:
    """Service for managing memories and image processing"""
    
    def __init__(self):
        self.settings = get_settings()
        self.openai_service = OpenAIService()
        self.faiss_store = FAISSStore()
        self.storage_path = get_storage_path()
        self.data_path = get_data_path()
        
        # Ensure directories exist
        os.makedirs(self.storage_path, exist_ok=True)
        os.makedirs(self.data_path, exist_ok=True)
        
        # Initialize metadata database
        self._init_metadata_db()
    
    def _init_metadata_db(self):
        """Initialize SQLite database for metadata storage"""
        db_path = os.path.join(self.data_path, "metadata.db")
        self.db_path = db_path
        
        with sqlite3.connect(db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS memories (
                    id TEXT PRIMARY KEY,
                    timestamp TEXT NOT NULL,
                    location TEXT,
                    summary TEXT NOT NULL,
                    detailed_description TEXT NOT NULL,
                    title TEXT NOT NULL,
                    confidence REAL NOT NULL,
                    objects_detected TEXT,
                    activity TEXT,
                    colors TEXT,
                    people_count INTEGER,
                    image_path TEXT NOT NULL,
                    compressed_image_path TEXT NOT NULL,
                    original_image_path TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    vector_id INTEGER
                )
            """)
            conn.commit()
    
    async def simulate_capture(self) -> str:
        """Simulate a photo capture and process it"""
        try:
            # Generate unique ID for this memory
            memory_id = f"memory_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{np.random.randint(1000, 9999)}"
            
            # Create simulated image
            image_path = await self._create_simulated_image(memory_id)
            
            # Process the image
            memory = await self._process_image(image_path, memory_id)
            
            # Store in FAISS and database
            await self._store_memory(memory)
            
            logger.info(f"Simulated capture completed: {memory_id}")
            return memory_id
            
        except Exception as e:
            logger.error(f"Error in simulated capture: {e}")
            raise
    
    async def _create_simulated_image(self, memory_id: str) -> str:
        """Create a simulated image with timestamp and random content"""
        # Create a canvas with random content
        width, height = 800, 600
        
        # Create base image with random background
        img = np.random.randint(0, 255, (height, width, 3), dtype=np.uint8)
        
        # Add some geometric shapes for variety
        cv2.rectangle(img, (100, 100), (300, 200), (255, 0, 0), -1)
        cv2.circle(img, (500, 150), 50, (0, 255, 0), -1)
        cv2.line(img, (200, 400), (600, 400), (0, 0, 255), 5)
        
        # Add timestamp text
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cv2.putText(img, timestamp, (50, 550), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        
        # Add memory ID
        cv2.putText(img, f"ID: {memory_id}", (50, 580), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        # Save original image
        original_path = os.path.join(self.storage_path, f"{memory_id}_original.jpg")
        cv2.imwrite(original_path, img)
        
        # Compress image
        compressed_path = os.path.join(self.storage_path, f"{memory_id}.jpg")
        await self._compress_image(original_path, compressed_path)
        
        return compressed_path
    
    async def _compress_image(self, input_path: str, output_path: str) -> None:
        """Compress image to specified dimensions and quality"""
        try:
            with Image.open(input_path) as img:
                # Resize if needed
                if img.width > self.settings.max_image_width or img.height > self.settings.max_image_height:
                    img.thumbnail((self.settings.max_image_width, self.settings.max_image_height), Image.Resampling.LANCZOS)
                
                # Save with specified quality
                img.save(output_path, 'JPEG', quality=self.settings.image_quality, optimize=True)
                
        except Exception as e:
            logger.error(f"Error compressing image: {e}")
            raise
    
    async def _process_image(self, image_path: str, memory_id: str) -> Memory:
        """Process image with OpenAI to generate summary and description"""
        try:
            # Generate summary using OpenAI
            summary_data = await self.openai_service.analyze_image(image_path)
            
            # Create memory object
            memory = Memory(
                id=memory_id,
                timestamp=datetime.now(),
                location=self._generate_simulated_location(),
                summary=summary_data["summary"],
                detailed_description=summary_data["detailed_description"],
                title=summary_data["title"],
                confidence=summary_data["confidence"],
                objects_detected=summary_data["objects_detected"],
                activity=summary_data["activity"],
                colors=summary_data["colors"],
                people_count=summary_data["people_count"],
                image_path=image_path,
                compressed_image_path=image_path,
                original_image_path=image_path.replace(".jpg", "_original.jpg")
            )
            
            return memory
            
        except Exception as e:
            logger.error(f"Error processing image: {e}")
            raise
    
    def _generate_simulated_location(self) -> str:
        """Generate a simulated location for demo purposes"""
        locations = [
            "Home Office", "Kitchen", "Living Room", "Bedroom", "Garden",
            "Coffee Shop", "Park", "Library", "Gym", "Restaurant"
        ]
        return np.random.choice(locations)
    
    async def _store_memory(self, memory: Memory) -> None:
        """Store memory in both FAISS and database"""
        try:
            # Generate embedding and store in FAISS
            vector_id = await self.faiss_store.add_memory(memory)
            memory.vector_id = vector_id
            
            # Store metadata in database
            self._store_metadata(memory)
            
            logger.info(f"Memory stored successfully: {memory.id}")
            
        except Exception as e:
            logger.error(f"Error storing memory: {e}")
            raise
    
    def _store_metadata(self, memory: Memory) -> None:
        """Store memory metadata in SQLite database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO memories (
                        id, timestamp, location, summary, detailed_description,
                        title, confidence, objects_detected, activity, colors,
                        people_count, image_path, compressed_image_path,
                        original_image_path, created_at, updated_at, vector_id
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    memory.id,
                    memory.timestamp.isoformat(),
                    memory.location,
                    memory.summary,
                    memory.detailed_description,
                    memory.title,
                    memory.confidence,
                    json.dumps(memory.objects_detected),
                    memory.activity,
                    json.dumps(memory.colors),
                    memory.people_count,
                    memory.image_path,
                    memory.compressed_image_path,
                    memory.original_image_path,
                    memory.created_at.isoformat(),
                    memory.updated_at.isoformat(),
                    memory.vector_id
                ))
                conn.commit()
                
        except Exception as e:
            logger.error(f"Error storing metadata: {e}")
            raise
    
    async def search_by_timestamp(self, timestamp: datetime) -> List[MemorySearchResult]:
        """Search memories near a specific timestamp"""
        try:
            # Get memories from database within time window
            memories = self._get_memories_by_timestamp(timestamp)
            
            # Calculate similarity scores and return results
            results = []
            for memory in memories:
                # Calculate time distance
                time_diff = abs((memory.timestamp - timestamp).total_seconds() / 60)
                
                # For demo, use inverse time distance as similarity
                similarity = max(0, 1 - (time_diff / self.settings.search_window_minutes))
                
                if similarity > 0:
                    results.append(MemorySearchResult(
                        memory=memory,
                        similarity_score=similarity,
                        timestamp_distance_minutes=int(time_diff)
                    ))
            
            # Sort by similarity score
            results.sort(key=lambda x: x.similarity_score, reverse=True)
            
            return results[:self.settings.max_search_results]
            
        except Exception as e:
            logger.error(f"Error searching by timestamp: {e}")
            raise
    
    def _get_memories_by_timestamp(self, timestamp: datetime) -> List[Memory]:
        """Get memories from database within search window"""
        try:
            window_start = timestamp - timedelta(minutes=self.settings.search_window_minutes)
            window_end = timestamp + timedelta(minutes=self.settings.search_window_minutes)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT * FROM memories 
                    WHERE timestamp BETWEEN ? AND ?
                    ORDER BY timestamp DESC
                """, (window_start.isoformat(), window_end.isoformat()))
                
                rows = cursor.fetchall()
                memories = []
                
                for row in rows:
                    memory = Memory(
                        id=row[0],
                        timestamp=datetime.fromisoformat(row[1]),
                        location=row[2],
                        summary=row[3],
                        detailed_description=row[4],
                        title=row[5],
                        confidence=row[6],
                        objects_detected=json.loads(row[7]) if row[7] else [],
                        activity=row[8],
                        colors=json.loads(row[9]) if row[9] else [],
                        people_count=row[10],
                        image_path=row[11],
                        compressed_image_path=row[12],
                        original_image_path=row[13],
                        created_at=datetime.fromisoformat(row[14]),
                        updated_at=datetime.fromisoformat(row[15]),
                        vector_id=row[16]
                    )
                    memories.append(memory)
                
                return memories
                
        except Exception as e:
            logger.error(f"Error getting memories by timestamp: {e}")
            raise
    
    async def get_memory_by_id(self, memory_id: str) -> Optional[Memory]:
        """Get a specific memory by ID"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("SELECT * FROM memories WHERE id = ?", (memory_id,))
                row = cursor.fetchone()
                
                if row:
                    return Memory(
                        id=row[0],
                        timestamp=datetime.fromisoformat(row[1]),
                        location=row[2],
                        summary=row[3],
                        detailed_description=row[4],
                        title=row[5],
                        confidence=row[6],
                        objects_detected=json.loads(row[7]) if row[7] else [],
                        activity=row[8],
                        colors=json.loads(row[9]) if row[9] else [],
                        people_count=row[10],
                        image_path=row[11],
                        compressed_image_path=row[12],
                        original_image_path=row[13],
                        created_at=datetime.fromisoformat(row[14]),
                        updated_at=datetime.fromisoformat(row[15]),
                        vector_id=row[16]
                    )
                
                return None
                
        except Exception as e:
            logger.error(f"Error getting memory by ID: {e}")
            raise
    
    def get_memories_count(self) -> int:
        """Get total count of stored memories"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("SELECT COUNT(*) FROM memories")
                return cursor.fetchone()[0]
        except Exception as e:
            logger.error(f"Error getting memories count: {e}")
            return 0
    
    def get_last_capture_time(self) -> Optional[datetime]:
        """Get timestamp of the most recent capture"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("SELECT timestamp FROM memories ORDER BY timestamp DESC LIMIT 1")
                row = cursor.fetchone()
                if row:
                    return datetime.fromisoformat(row[0])
                return None
        except Exception as e:
            logger.error(f"Error getting last capture time: {e}")
            return None
