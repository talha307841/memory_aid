"""
OpenAI service for MemoryAid application
Handles image analysis, text generation, and embeddings
"""

import os
import base64
import logging
from typing import Dict, List, Any
from openai import OpenAI
from services.config import get_settings

logger = logging.getLogger(__name__)

class OpenAIService:
    """Service for OpenAI API interactions"""
    
    def __init__(self):
        self.settings = get_settings()
        self.client = OpenAI(api_key=self.settings.openai_api_key)
    
    async def analyze_image(self, image_path: str) -> Dict[str, Any]:
        """Analyze an image and generate summary using OpenAI Vision"""
        try:
            # Read and encode image
            with open(image_path, "rb") as image_file:
                image_data = base64.b64encode(image_file.read()).decode('utf-8')
            
            # Create prompt for image analysis
            prompt = """
            Analyze this image and provide a comprehensive description. Include:
            
            1. A short, descriptive title (one line)
            2. A concise summary (2-3 sentences)
            3. A detailed description (3-4 sentences)
            4. List of visible objects
            5. Probable activity or context
            6. Colors present
            7. Number of people (if any)
            8. Confidence level (0.0 to 1.0)
            
            Format your response as JSON with these keys:
            {
                "title": "string",
                "summary": "string", 
                "detailed_description": "string",
                "objects_detected": ["object1", "object2"],
                "activity": "string",
                "colors": ["color1", "color2"],
                "people_count": number,
                "confidence": 0.95
            }
            
            Be descriptive but concise. Focus on what would be most useful for memory recall.
            """
            
            # Call OpenAI Vision API
            response = self.client.chat.completions.create(
                model=self.settings.openai_model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{image_data}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=500,
                temperature=0.3
            )
            
            # Parse response
            content = response.choices[0].message.content
            
            # Try to extract JSON from response
            try:
                import json
                # Find JSON in the response
                start_idx = content.find('{')
                end_idx = content.rfind('}') + 1
                if start_idx != -1 and end_idx != -1:
                    json_str = content[start_idx:end_idx]
                    result = json.loads(json_str)
                else:
                    # Fallback: create structured response from text
                    result = self._parse_fallback_response(content)
            except json.JSONDecodeError:
                logger.warning("Failed to parse JSON response, using fallback")
                result = self._parse_fallback_response(content)
            
            # Ensure all required fields are present
            result = self._ensure_required_fields(result)
            
            logger.info(f"Image analysis completed for {image_path}")
            return result
            
        except Exception as e:
            logger.error(f"Error analyzing image: {e}")
            # Return fallback response
            return self._get_fallback_response()
    
    def _parse_fallback_response(self, content: str) -> Dict[str, Any]:
        """Parse OpenAI response when JSON parsing fails"""
        # Extract key information from text response
        lines = content.split('\n')
        
        title = "Image Analysis"
        summary = content[:200] + "..." if len(content) > 200 else content
        detailed_description = content
        
        # Try to extract objects and colors
        objects_detected = []
        colors = []
        
        # Simple keyword extraction
        color_keywords = ['red', 'blue', 'green', 'yellow', 'black', 'white', 'gray', 'brown', 'purple', 'orange']
        for line in lines:
            line_lower = line.lower()
            for color in color_keywords:
                if color in line_lower:
                    colors.append(color)
            
            # Extract potential objects
            if any(word in line_lower for word in ['object', 'item', 'thing', 'shape']):
                objects_detected.append(line.strip())
        
        return {
            "title": title,
            "summary": summary,
            "detailed_description": detailed_description,
            "objects_detected": objects_detected[:5],  # Limit to 5 objects
            "activity": "Image captured",
            "colors": list(set(colors))[:5],  # Remove duplicates, limit to 5
            "people_count": 0,
            "confidence": 0.7
        }
    
    def _ensure_required_fields(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Ensure all required fields are present in the result"""
        required_fields = {
            "title": "Image Analysis",
            "summary": "Image captured and analyzed",
            "detailed_description": "Image has been processed and analyzed for memory storage",
            "objects_detected": [],
            "activity": "Image capture",
            "colors": [],
            "people_count": 0,
            "confidence": 0.8
        }
        
        for field, default_value in required_fields.items():
            if field not in result or result[field] is None:
                result[field] = default_value
        
        return result
    
    def _get_fallback_response(self) -> Dict[str, Any]:
        """Get a fallback response when image analysis fails"""
        return {
            "title": "Image Analysis Failed",
            "summary": "Unable to analyze image due to processing error",
            "detailed_description": "The image could not be processed by the AI system. This may be due to technical issues or image format problems.",
            "objects_detected": [],
            "activity": "Unknown",
            "colors": [],
            "people_count": 0,
            "confidence": 0.1
        }
    
    async def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding vector for text using OpenAI"""
        try:
            response = self.client.embeddings.create(
                model=self.settings.openai_embedding_model,
                input=text
            )
            
            embedding = response.data[0].embedding
            logger.debug(f"Generated embedding for text: {text[:50]}...")
            return embedding
            
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            # Return zero vector as fallback
            return [0.0] * 1536  # OpenAI ada-002 embedding dimension
    
    async def chat_completion(self, messages: List[Dict[str, str]], context_memories: List[Dict[str, Any]] = None) -> str:
        """Generate chat completion with optional memory context"""
        try:
            # Prepare system message
            system_message = """
            You are MemoryAid, an AI assistant that helps users recall and search through their visual memories. 
            You have access to a database of captured images and their descriptions.
            
            When responding:
            1. Be helpful and conversational
            2. Reference specific memories when relevant
            3. Provide timestamps and locations when available
            4. If you don't have relevant memories, be honest about it
            5. Keep responses concise but informative
            """
            
            # Add memory context if provided
            if context_memories:
                context_text = "\n\nRelevant memories:\n"
                for i, memory in enumerate(context_memories, 1):
                    context_text += f"{i}. {memory['title']} ({memory['timestamp']}) - {memory['summary']}\n"
                
                system_message += context_text
            
            # Prepare messages for OpenAI
            openai_messages = [{"role": "system", "content": system_message}]
            openai_messages.extend(messages)
            
            # Call OpenAI
            response = self.client.chat.completions.create(
                model="gpt-4",  # Use GPT-4 for chat
                messages=openai_messages,
                max_tokens=300,
                temperature=0.7
            )
            
            result = response.choices[0].message.content
            logger.info("Chat completion generated successfully")
            return result
            
        except Exception as e:
            logger.error(f"Error generating chat completion: {e}")
            return "I'm sorry, I'm having trouble processing your request right now. Please try again later."
