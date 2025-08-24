"""
Basic tests for MemoryAid application
"""

import pytest
import asyncio
import os
import sys

# Add the api directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'api'))

from services.config import get_settings
from services.memory_service import MemoryService
from services.faiss_store import FAISSStore

def test_config_loading():
    """Test that configuration can be loaded"""
    try:
        settings = get_settings()
        assert settings is not None
        assert hasattr(settings, 'demo_mode')
        print("✅ Configuration loading test passed")
    except Exception as e:
        pytest.fail(f"Configuration loading failed: {e}")

def test_memory_service_initialization():
    """Test that memory service can be initialized"""
    try:
        service = MemoryService()
        assert service is not None
        assert hasattr(service, 'simulate_capture')
        print("✅ Memory service initialization test passed")
    except Exception as e:
        pytest.fail(f"Memory service initialization failed: {e}")

def test_faiss_store_initialization():
    """Test that FAISS store can be initialized"""
    try:
        store = FAISSStore()
        assert store is not None
        assert hasattr(store, 'add_memory')
        print("✅ FAISS store initialization test passed")
    except Exception as e:
        pytest.fail(f"FAISS store initialization failed: {e}")

def test_directory_creation():
    """Test that required directories are created"""
    try:
        from services.config import get_data_path, get_storage_path
        
        data_path = get_data_path()
        storage_path = get_storage_path()
        
        assert os.path.exists(data_path)
        assert os.path.exists(storage_path)
        
        print("✅ Directory creation test passed")
    except Exception as e:
        pytest.fail(f"Directory creation test failed: {e}")

if __name__ == "__main__":
    print("Running MemoryAid basic tests...")
    print("=" * 40)
    
    test_config_loading()
    test_memory_service_initialization()
    test_faiss_store_initialization()
    test_directory_creation()
    
    print("=" * 40)
    print("All basic tests completed!")
