"""
Plant Service Module
Handles OpenAI API interactions for plant analysis and identification
"""

from openai import OpenAI
import streamlit as st
from typing import Generator, Optional
import logging

logger = logging.getLogger(__name__)

class PlantService:
    """Service for plant identification and analysis using OpenAI"""
    
    def __init__(self, cache_service):
        """
        Initialize PlantService with OpenAI client and cache
        
        Args:
            cache_service: Instance of CacheService for caching results
        """
        try:
            api_key = st.secrets.get("OPENAI_API_KEY")
            if not api_key:
                logger.error("OPENAI_API_KEY not found in secrets")
                st.error("⚠️ OpenAI API key not configured. Please add OPENAI_API_KEY to secrets.")
                self.client = None
            else:
                self.client = OpenAI(api_key=api_key)
                logger.info("OpenAI client initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing OpenAI client: {e}")
            st.error(f"⚠️ Error initializing OpenAI: {e}")
            self.client = None
        
        self.cache = cache_service
        
        # Import config here to avoid circular imports
        from utils.config import AppConfig
        self.config = AppConfig()
    
    def is_ready(self) -> bool:
        """Check if the service is ready to use"""
        return self.client is not None
    
    def _normalize_plant_name(self, plant_name: str) -> str:
        """
        Normalize plant name for consistent caching
        
        Args:
            plant_name: Raw plant name
            
        Returns:
            Normalized plant name
        """
        # Strip whitespace and convert to title case for consistency
        return plant_name.strip().title()
    
    def get_analysis_stream(self, plant_name: str) -> Generator[str, None, None]:
        """
        Get plant analysis with streaming support
        This method should ONLY be called when content is NOT cached
        
        Args:
            plant_name: Name of the plant to analyze
            
        Yields:
            Chunks of analysis text
        """
        # Check if OpenAI client is initialized
        if not self.client:
            yield "Error: OpenAI API not configured. Please check your API key."
            return
        
        # Normalize plant name for consistent caching
        plant_name = self._normalize_plant_name(plant_name)
        cache_key = f"{self.config.CACHE_KEY_PREFIX}{plant_name}"
        
        # Generate new analysis with streaming
        full_response = ""
        try:
            logger.info(f"Generating new analysis for: {plant_name}")
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
                success = self.cache.set(cache_key, full_response, expire=self.config.CACHE_TTL)
                if success:
                    logger.info(f"Successfully cached analysis for: {plant_name}")
                else:
                    logger.warning(f"Failed to cache analysis for: {plant_name}")
                    
        except Exception as e:
            logger.error(f"Error generating analysis for {plant_name}: {e}")
            yield f"\n\nError generating analysis: {str(e)}"
    
    def get_cached_analysis(self, plant_name: str) -> Optional[str]:
        """
        Get cached analysis if available
        
        Args:
            plant_name: Name of the plant
            
        Returns:
            Cached analysis or None if not found
        """
        # Normalize plant name for consistent caching
        plant_name = self._normalize_plant_name(plant_name)
        cache_key = f"{self.config.CACHE_KEY_PREFIX}{plant_name}"
        result = self.cache.get(cache_key)
        
        if result:
            logger.info(f"Cache HIT for: {plant_name}")
        else:
            logger.info(f"Cache MISS for: {plant_name}")
        
        return result
    
    def identify_plant_from_image(self, image_b64: str) -> str:
        """
        Identify plant from base64 encoded image
        
        Args:
            image_b64: Base64 encoded image string
            
        Returns:
            Plant name and scientific name (normalized)
        """
        if not self.client:
            raise Exception("OpenAI API not configured. Please check your API key.")
        
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