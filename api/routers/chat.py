"""
Chat router for MemoryAid API
Handles natural language queries and AI-powered memory assistance
"""

from datetime import datetime
from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import FileResponse
import os

from models.memory import ChatRequest, ChatResponse
from services.memory_service import MemoryService
from services.openai_service import OpenAIService
from services.faiss_store import FAISSStore

router = APIRouter()

@router.post("/", response_model=ChatResponse)
async def chat_with_assistant(request: ChatRequest):
    """
    Chat with the MemoryAid assistant.
    
    Accepts natural language queries and returns AI-generated responses
    based on relevant memories from the database.
    """
    try:
        # Initialize services
        memory_service = MemoryService()
        openai_service = OpenAIService()
        faiss_store = FAISSStore()
        
        # Search for relevant memories using FAISS
        relevant_memories = await faiss_store.search_similar(
            request.message, 
            k=request.max_results
        )
        
        # Get full memory details for relevant results
        memory_details = []
        for memory_id, similarity_score in relevant_memories:
            memory = await memory_service.get_memory_by_id(memory_id)
            if memory:
                memory_details.append({
                    "id": memory.id,
                    "title": memory.title,
                    "summary": memory.summary,
                    "timestamp": memory.timestamp.isoformat(),
                    "location": memory.location,
                    "similarity_score": similarity_score,
                    "image_path": memory.compressed_image_path
                })
        
        # Generate AI response using OpenAI
        user_message = {"role": "user", "content": request.message}
        
        # Create context from relevant memories
        context_memories = []
        for memory in memory_details:
            context_memories.append({
                "title": memory["title"],
                "summary": memory["summary"],
                "timestamp": memory["timestamp"],
                "location": memory["location"]
            })
        
        # Generate response
        assistant_message = await openai_service.chat_completion(
            [user_message], 
            context_memories
        )
        
        # Calculate confidence based on memory relevance
        confidence = 0.5  # Base confidence
        if memory_details:
            # Increase confidence based on best match
            best_similarity = max(memory["similarity_score"] for memory in memory_details)
            confidence = min(0.9, 0.5 + best_similarity * 0.4)
        
        # Create response
        response = ChatResponse(
            assistant_message=assistant_message,
            memory_references=memory_details,
            confidence=confidence,
            search_query=request.message,
            timestamp=datetime.now()
        )
        
        return response
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Chat request failed: {str(e)}"
        )

@router.post("/query", response_model=ChatResponse)
async def query_memories(request: ChatRequest):
    """
    Alternative endpoint for memory queries.
    
    Similar to /chat but with different response formatting.
    """
    return await chat_with_assistant(request)

@router.get("/suggestions")
async def get_chat_suggestions():
    """
    Get suggested chat queries for users.
    
    Returns a list of example questions users can ask.
    """
    suggestions = [
        "Where did I put my keys?",
        "What happened yesterday at 3pm?",
        "Show me memories from the kitchen",
        "What was I doing last week?",
        "Find memories with people in them",
        "Show me recent captures",
        "What objects did I see today?",
        "Where was I this morning?",
        "What activities did I do yesterday?",
        "Find memories by color"
    ]
    
    return {
        "suggestions": suggestions,
        "count": len(suggestions),
        "timestamp": datetime.now().isoformat()
    }

@router.post("/analyze")
async def analyze_query(request: ChatRequest):
    """
    Analyze a query without generating a full response.
    
    Returns information about how the query would be processed.
    """
    try:
        # Initialize services
        faiss_store = FAISSStore()
        openai_service = OpenAIService()
        
        # Generate embedding for the query
        query_embedding = await openai_service.generate_embedding(request.message)
        
        # Search for similar memories
        similar_memories = await faiss_store.search_by_embedding(
            query_embedding, 
            k=request.max_results
        )
        
        # Analyze query characteristics
        query_analysis = {
            "query_length": len(request.message),
            "query_words": len(request.message.split()),
            "has_time_reference": any(word in request.message.lower() for word in 
                                   ["when", "time", "today", "yesterday", "morning", "afternoon", "evening"]),
            "has_location_reference": any(word in request.message.lower() for word in 
                                        ["where", "location", "place", "room", "kitchen", "office"]),
            "has_object_reference": any(word in request.message.lower() for word in 
                                      ["what", "object", "thing", "item", "keys", "phone", "book"]),
            "embedding_dimension": len(query_embedding),
            "similar_memories_found": len(similar_memories)
        }
        
        return {
            "query": request.message,
            "analysis": query_analysis,
            "similar_memories": [
                {
                    "memory_id": memory_id,
                    "similarity_score": score
                }
                for memory_id, score in similar_memories
            ],
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Query analysis failed: {str(e)}"
        )

@router.get("/history")
async def get_chat_history(limit: int = 10):
    """
    Get recent chat history.
    
    Returns the last N chat interactions (if implemented).
    """
    # TODO: Implement chat history storage and retrieval
    return {
        "message": "Chat history not yet implemented",
        "limit": limit,
        "timestamp": datetime.now().isoformat()
    }
