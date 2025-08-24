"""
Memory router for MemoryAid API
Handles memory search, retrieval, and management endpoints
"""

from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, HTTPException, status, Query
from fastapi.responses import FileResponse
import os

from models.memory import Memory, MemorySearchResponse, MemorySearchResult
from services.memory_service import MemoryService
from services.config import get_settings

router = APIRouter()

@router.get("/search", response_model=MemorySearchResponse)
async def search_memories_by_timestamp(
    timestamp: str = Query(..., description="ISO format timestamp (YYYY-MM-DDTHH:MM:SS)")
):
    """
    Search for memories near a specific timestamp.
    
    Returns memories within the configured search window (default ±30 minutes).
    Results are ordered by similarity to the target timestamp.
    """
    try:
        # Parse timestamp
        try:
            target_time = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid timestamp format. Use ISO format: YYYY-MM-DDTHH:MM:SS"
            )
        
        # Search memories
        memory_service = MemoryService()
        search_results = await memory_service.search_by_timestamp(target_time)
        
        # Convert to response format
        results = []
        for result in search_results:
            results.append(MemorySearchResult(
                memory=result.memory,
                similarity_score=result.similarity_score,
                timestamp_distance_minutes=result.timestamp_distance_minutes
            ))
        
        return MemorySearchResponse(
            results=results,
            total_found=len(results),
            search_timestamp=datetime.now(),
            query_timestamp=target_time
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Search failed: {str(e)}"
        )

@router.get("/{memory_id}", response_model=Memory)
async def get_memory(memory_id: str):
    """
    Get a specific memory by ID.
    
    Returns the complete memory data including metadata, summary, and image paths.
    """
    try:
        memory_service = MemoryService()
        memory = await memory_service.get_memory_by_id(memory_id)
        
        if not memory:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Memory with ID {memory_id} not found"
            )
        
        return memory
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve memory: {str(e)}"
        )

@router.get("/{memory_id}/image")
async def get_memory_image(memory_id: str, original: bool = Query(False, description="Return original image if true")):
    """
    Get the image for a specific memory.
    
    Returns the compressed image by default, or the original image if original=true.
    """
    try:
        memory_service = MemoryService()
        memory = await memory_service.get_memory_by_id(memory_id)
        
        if not memory:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Memory with ID {memory_id} not found"
            )
        
        # Determine image path
        if original and memory.original_image_path:
            image_path = memory.original_image_path
        else:
            image_path = memory.compressed_image_path
        
        # Check if image file exists
        if not os.path.exists(image_path):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Image file not found: {image_path}"
            )
        
        # Return image file
        return FileResponse(
            image_path,
            media_type="image/jpeg",
            filename=f"{memory_id}.jpg"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve image: {str(e)}"
        )

@router.get("/{memory_id}/thumbnail")
async def get_memory_thumbnail(memory_id: str, size: int = Query(200, description="Thumbnail size in pixels")):
    """
    Get a thumbnail version of the memory image.
    
    Returns a resized version of the compressed image for display purposes.
    """
    try:
        from PIL import Image
        import io
        
        memory_service = MemoryService()
        memory = await memory_service.get_memory_by_id(memory_id)
        
        if not memory:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Memory with ID {memory_id} not found"
            )
        
        # Check if image file exists
        if not os.path.exists(memory.compressed_image_path):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Image file not found: {memory.compressed_image_path}"
            )
        
        # Create thumbnail
        with Image.open(memory.compressed_image_path) as img:
            # Resize image maintaining aspect ratio
            img.thumbnail((size, size), Image.Resampling.LANCZOS)
            
            # Convert to bytes
            img_byte_arr = io.BytesIO()
            img.save(img_byte_arr, format='JPEG', quality=85)
            img_byte_arr.seek(0)
            
            # Return thumbnail
            return FileResponse(
                img_byte_arr,
                media_type="image/jpeg",
                filename=f"{memory_id}_thumb.jpg"
            )
        
    except ImportError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Pillow library not available for thumbnail generation"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate thumbnail: {str(e)}"
        )

@router.delete("/{memory_id}")
async def delete_memory(memory_id: str):
    """
    Delete a memory and its associated data.
    
    Removes the memory from the database, FAISS index, and deletes image files.
    """
    try:
        memory_service = MemoryService()
        memory = await memory_service.get_memory_by_id(memory_id)
        
        if not memory:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Memory with ID {memory_id} not found"
            )
        
        # TODO: Implement memory deletion
        # This would require adding delete methods to the services
        
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Memory deletion not yet implemented"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete memory: {str(e)}"
        )
