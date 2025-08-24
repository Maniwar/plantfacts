"""
Plant Service Module
Handles OpenAI API interactions for plant analysis and identification
"""

from openai import OpenAI
import streamlit as st
from typing import Generator, Optional
from utils.config import AppConfig
from utils.cache_service import CacheService
import logging

logger = logging.getLogger(__name__)

class PlantService:
    """Service for plant identification and analysis using OpenAI"""
    
    def __init__(self, cache_service: CacheService):
        """
        Initialize PlantService with OpenAI client and cache
        
        Args:
            cache_service: Instance of CacheService for caching results
        """
        self.client = OpenAI(api_key=st.secrets.get("OPENAI_API_KEY"))
        self.cache = cache_service
        self.config = AppConfig()
    
    def get_analysis_stream(self, plant_name: str) -> Generator[str, None, None]:
        """
        Get plant analysis with streaming support
        
        Args:
            plant_name: Name of the plant to analyze
            
        Yields:
            Chunks of analysis text
        """
        # Check cache first
        cache_key = f"{self.config.CACHE_KEY_PREFIX}{plant_name}"
        cached_result = self.cache.get(cache_key)
        
        if cached_result:
            # Return cached result immediately - NO STREAMING!
            yield cached_result
        else:
            # Generate new analysis with streaming
            full_response = ""
            try:
                stream = self.client.chat.completions.create(
                    model=self.config.OPENAI_MODEL,
                    messages=[
                        {
                            "role": "system", 
                            "content": "You are a plant expert providing detailed information about various plants."
                        },
                        {
                            "role": "user", 
                            "content": self.config.ANALYSIS_PROMPT.format(plant_name=plant_name)
                        }
                    ],
                    max_tokens=self.config.MAX_TOKENS,
                    stream=True
                )
                
                for chunk in stream:
                    if chunk.choices[0].delta.content is not None:
                        content = chunk.choices[0].delta.content
                        full_response += content
                        yield content
                
                # Cache the complete response after streaming is done
                if full_response:
                    self.cache.set(cache_key, full_response, expire=self.config.CACHE_TTL)
                    logger.info(f"Cached analysis for: {plant_name}")
                    
            except Exception as e:
                logger.error(f"Error generating analysis for {plant_name}: {e}")
                yield f"Error generating analysis: {str(e)}"
    
    def identify_plant_from_image(self, image_b64: str) -> str:
        """
        Identify plant from base64 encoded image
        
        Args:
            image_b64: Base64 encoded image string
            
        Returns:
            Plant name and scientific name (normalized)
        """
        try:
            response = self.client.chat.completions.create(
                model=self.config.OPENAI_MODEL,
                messages=[{
                    "role": "user",
                    "content": [
                        {
                            "type": "text", 
                            "text": self.config.IDENTIFICATION_PROMPT
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_b64}"
                            }
                        }
                    ]
                }],
                max_tokens=50
            )
            
            plant_name = response.choices[0].message.content.strip()
            # Normalize the plant name for consistent caching
            plant_name = self._normalize_plant_name(plant_name)
            logger.info(f"Identified plant from image: {plant_name}")
            return plant_name
            
        except Exception as e:
            logger.error(f"Error identifying plant from image: {e}")
            raise Exception(f"Failed to identify plant: {str(e)}")
    
    def get_cached_analysis(self, plant_name: str) -> Optional[str]:
        """
        Get cached analysis if available
        
        Args:
            plant_name: Name of the plant
            
        Returns:
            Cached analysis or None
        """
        cache_key = f"{self.config.CACHE_KEY_PREFIX}{plant_name}"
        return self.cache.get(cache_key)
