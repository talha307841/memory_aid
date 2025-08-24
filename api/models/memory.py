"""
Data models for MemoryAid application
Defines the structure for memory data and API requests/responses
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
import uuid

class MemoryBase(BaseModel):
    """Base memory model"""
    timestamp: datetime
    location: Optional[str] = None
    summary: str
    detailed_description: str
    title: str
    confidence: float = Field(ge=0.0, le=1.0)
    objects_detected: List[str] = []
    activity: Optional[str] = None
    colors: List[str] = []
    people_count: Optional[int] = None

class MemoryCreate(MemoryBase):
    """Model for creating a new memory"""
    image_path: str
    compressed_image_path: str
    original_image_path: Optional[str] = None

class Memory(MemoryBase):
    """Complete memory model with ID and metadata"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    image_path: str
    compressed_image_path: str
    original_image_path: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    vector_id: Optional[int] = None  # FAISS vector index ID
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class MemorySearchResult(BaseModel):
    """Model for memory search results"""
    memory: Memory
    similarity_score: float
    timestamp_distance_minutes: int

class MemorySearchResponse(BaseModel):
    """Response model for memory search"""
    results: List[MemorySearchResult]
    total_found: int
    search_timestamp: datetime
    query_timestamp: datetime

class ChatRequest(BaseModel):
    """Model for chat requests"""
    message: str = Field(..., min_length=1, max_length=1000)
    include_images: bool = True
    max_results: int = 5

class ChatResponse(BaseModel):
    """Model for chat responses"""
    assistant_message: str
    memory_references: List[Dict[str, Any]]
    confidence: float
    search_query: str
    timestamp: datetime

class HealthResponse(BaseModel):
    """Model for health check responses"""
    status: str
    timestamp: datetime
    memories_count: int
    last_capture_time: Optional[datetime]
    faiss_index_size: int
    storage_usage_mb: float
    demo_mode: bool

class CaptureResponse(BaseModel):
    """Model for capture responses"""
    success: bool
    memory_id: str
    message: str
    timestamp: datetime
    image_path: str

class ErrorResponse(BaseModel):
    """Model for error responses"""
    error: str
    detail: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
