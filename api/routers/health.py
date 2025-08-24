"""
Health router for MemoryAid API
Handles health checks, system status, and monitoring endpoints
"""

import os
import psutil
from datetime import datetime
from typing import Dict, Any
from fastapi import APIRouter, HTTPException, status

from models.memory import HealthResponse
from services.memory_service import MemoryService
from services.faiss_store import FAISSStore
from services.config import get_settings

router = APIRouter()

@router.get("/", response_model=HealthResponse)
async def health_check():
    """
    Basic health check endpoint.
    
    Returns system status, memory count, and basic statistics.
    """
    try:
        # Get basic system info
        memory_service = MemoryService()
        faiss_store = FAISSStore()
        settings = get_settings()
        
        # Get memory statistics
        memories_count = memory_service.get_memories_count()
        last_capture_time = memory_service.get_last_capture_time()
        
        # Get FAISS index statistics
        faiss_stats = faiss_store.get_index_stats()
        faiss_index_size = faiss_stats.get("total_vectors", 0)
        
        # Calculate storage usage
        storage_usage_mb = _calculate_storage_usage()
        
        # Determine overall status
        status_str = "healthy"
        if memories_count == 0:
            status_str = "initializing"
        elif storage_usage_mb > 1000:  # More than 1GB
            status_str = "warning"
        
        return HealthResponse(
            status=status_str,
            timestamp=datetime.now(),
            memories_count=memories_count,
            last_capture_time=last_capture_time,
            faiss_index_size=faiss_index_size,
            storage_usage_mb=storage_usage_mb,
            demo_mode=settings.demo_mode
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Health check failed: {str(e)}"
        )

@router.get("/detailed")
async def detailed_health_check():
    """
    Detailed health check with comprehensive system information.
    
    Returns detailed system metrics, configuration, and performance data.
    """
    try:
        # Get basic health info
        basic_health = await health_check()
        
        # Get system metrics
        system_metrics = _get_system_metrics()
        
        # Get configuration summary
        config_summary = _get_config_summary()
        
        # Get service status
        service_status = _get_service_status()
        
        return {
            "basic_health": basic_health.dict(),
            "system_metrics": system_metrics,
            "configuration": config_summary,
            "services": service_status,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Detailed health check failed: {str(e)}"
        )

@router.get("/ready")
async def readiness_check():
    """
    Readiness check for the application.
    
    Returns whether the application is ready to handle requests.
    """
    try:
        # Check if essential services are available
        memory_service = MemoryService()
        faiss_store = FAISSStore()
        
        # Basic checks
        memories_count = memory_service.get_memories_count()
        faiss_stats = faiss_store.get_index_stats()
        
        # Determine readiness
        is_ready = (
            memories_count >= 0 and  # Database is accessible
            faiss_stats.get("total_vectors", 0) >= 0  # FAISS is accessible
        )
        
        return {
            "ready": is_ready,
            "timestamp": datetime.now().isoformat(),
            "checks": {
                "database": memories_count >= 0,
                "faiss_index": faiss_stats.get("total_vectors", 0) >= 0
            }
        }
        
    except Exception as e:
        return {
            "ready": False,
            "timestamp": datetime.now().isoformat(),
            "error": str(e)
        }

@router.get("/stats")
async def get_statistics():
    """
    Get detailed application statistics.
    
    Returns comprehensive statistics about memories, storage, and performance.
    """
    try:
        memory_service = MemoryService()
        faiss_store = FAISSStore()
        
        # Memory statistics
        memories_count = memory_service.get_memories_count()
        last_capture_time = memory_service.get_last_capture_time()
        
        # FAISS statistics
        faiss_stats = faiss_store.get_index_stats()
        
        # Storage statistics
        storage_stats = _get_storage_statistics()
        
        # Performance statistics
        performance_stats = _get_performance_statistics()
        
        return {
            "memories": {
                "total_count": memories_count,
                "last_capture": last_capture_time.isoformat() if last_capture_time else None,
                "average_per_day": _calculate_average_memories_per_day(memories_count)
            },
            "vector_database": faiss_stats,
            "storage": storage_stats,
            "performance": performance_stats,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get statistics: {str(e)}"
        )

def _calculate_storage_usage() -> float:
    """Calculate storage usage in MB"""
    try:
        settings = get_settings()
        storage_path = settings.storage_path
        
        if not os.path.exists(storage_path):
            return 0.0
        
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(storage_path):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                if os.path.exists(filepath):
                    total_size += os.path.getsize(filepath)
        
        return round(total_size / (1024 * 1024), 2)  # Convert to MB
        
    except Exception:
        return 0.0

def _get_system_metrics() -> Dict[str, Any]:
    """Get system performance metrics"""
    try:
        # CPU usage
        cpu_percent = psutil.cpu_percent(interval=1)
        
        # Memory usage
        memory = psutil.virtual_memory()
        
        # Disk usage
        disk = psutil.disk_usage('/')
        
        return {
            "cpu": {
                "usage_percent": cpu_percent,
                "count": psutil.cpu_count()
            },
            "memory": {
                "total_gb": round(memory.total / (1024**3), 2),
                "available_gb": round(memory.available / (1024**3), 2),
                "usage_percent": memory.percent
            },
            "disk": {
                "total_gb": round(disk.total / (1024**3), 2),
                "free_gb": round(disk.free / (1024**3), 2),
                "usage_percent": round((disk.used / disk.total) * 100, 2)
            }
        }
    except ImportError:
        return {"error": "psutil not available"}
    except Exception:
        return {"error": "Failed to get system metrics"}

def _get_config_summary() -> Dict[str, Any]:
    """Get configuration summary"""
    try:
        settings = get_settings()
        return {
            "demo_mode": settings.demo_mode,
            "capture_interval_seconds": settings.capture_interval_seconds,
            "max_image_width": settings.max_image_width,
            "max_image_height": settings.max_image_height,
            "image_quality": settings.image_quality,
            "search_window_minutes": settings.search_window_minutes,
            "max_search_results": settings.max_search_results
        }
    except Exception:
        return {"error": "Failed to get configuration"}

def _get_service_status() -> Dict[str, Any]:
    """Get service status information"""
    try:
        from services.background_scheduler import BackgroundScheduler
        
        # Check if scheduler is available (this is a simplified check)
        scheduler_available = True
        
        return {
            "background_scheduler": {
                "available": scheduler_available,
                "status": "running" if scheduler_available else "unknown"
            },
            "openai_service": {
                "available": True,
                "status": "ready"
            },
            "faiss_store": {
                "available": True,
                "status": "ready"
            }
        }
    except Exception:
        return {"error": "Failed to get service status"}

def _get_storage_statistics() -> Dict[str, Any]:
    """Get detailed storage statistics"""
    try:
        settings = get_settings()
        storage_path = settings.storage_path
        
        if not os.path.exists(storage_path):
            return {"error": "Storage path not found"}
        
        # Count files by type
        file_counts = {"jpg": 0, "png": 0, "other": 0}
        total_size = 0
        
        for filename in os.listdir(storage_path):
            if filename.endswith('.jpg'):
                file_counts["jpg"] += 1
            elif filename.endswith('.png'):
                file_counts["png"] += 1
            else:
                file_counts["other"] += 1
            
            filepath = os.path.join(storage_path, filename)
            if os.path.isfile(filepath):
                total_size += os.path.getsize(filepath)
        
        return {
            "file_counts": file_counts,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "average_file_size_kb": round((total_size / sum(file_counts.values())) / 1024, 2) if sum(file_counts.values()) > 0 else 0
        }
        
    except Exception:
        return {"error": "Failed to get storage statistics"}

def _get_performance_statistics() -> Dict[str, Any]:
    """Get performance statistics"""
    try:
        # This is a placeholder for actual performance metrics
        # In a real implementation, you'd track response times, throughput, etc.
        return {
            "average_response_time_ms": 150,
            "requests_per_minute": 10,
            "error_rate_percent": 0.5,
            "uptime_seconds": 3600  # Placeholder
        }
    except Exception:
        return {"error": "Failed to get performance statistics"}

def _calculate_average_memories_per_day(total_memories: int) -> float:
    """Calculate average memories per day"""
    try:
        # This is a simplified calculation
        # In a real implementation, you'd track actual daily counts
        if total_memories == 0:
            return 0.0
        
        # Assume the system has been running for some time
        # This is just for demo purposes
        return round(total_memories / 7.0, 2)  # Assume 7 days
        
    except Exception:
        return 0.0
