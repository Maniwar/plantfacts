"""
Cache Service Module
Handles Redis connection and caching operations
"""

import redis
import streamlit as st
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class CacheService:
    """Service for handling Redis cache operations"""
    
    def __init__(self):
        """Initialize Redis connection using Streamlit secrets"""
        try:
            self.redis_client = redis.Redis(
                host=st.secrets["REDIS_HOST"],
                port=st.secrets["REDIS_PORT"],
                password=st.secrets["REDIS_PASSWORD"],
                decode_responses=True,
                socket_keepalive=True,
                socket_keepalive_options={
                    1: 1,  # TCP_KEEPIDLE
                    2: 1,  # TCP_KEEPINTVL
                    3: 5,  # TCP_KEEPCNT
                }
            )
            # Test connection
            self.redis_client.ping()
            self.connected = True
            logger.info("Redis connection established successfully")
        except Exception as e:
            logger.warning(f"Redis connection failed: {e}. Cache disabled.")
            self.redis_client = None
            self.connected = False
    
    def get(self, key: str) -> Optional[str]:
        """
        Get value from cache
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found or cache disabled
        """
        if not self.connected:
            return None
            
        try:
            return self.redis_client.get(key)
        except Exception as e:
            logger.error(f"Error getting cache key {key}: {e}")
            return None
    
    def set(self, key: str, value: str, expire: Optional[int] = None) -> bool:
        """
        Set value in cache
        
        Args:
            key: Cache key
            value: Value to cache
            expire: Optional expiration time in seconds
            
        Returns:
            True if successful, False otherwise
        """
        if not self.connected:
            return False
            
        try:
            if expire:
                self.redis_client.setex(key, expire, value)
            else:
                self.redis_client.set(key, value)
            return True
        except Exception as e:
            logger.error(f"Error setting cache key {key}: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """
        Delete key from cache
        
        Args:
            key: Cache key to delete
            
        Returns:
            True if successful, False otherwise
        """
        if not self.connected:
            return False
            
        try:
            self.redis_client.delete(key)
            return True
        except Exception as e:
            logger.error(f"Error deleting cache key {key}: {e}")
            return False
    
    def exists(self, key: str) -> bool:
        """
        Check if key exists in cache
        
        Args:
            key: Cache key to check
            
        Returns:
            True if key exists, False otherwise
        """
        if not self.connected:
            return False
            
        try:
            return bool(self.redis_client.exists(key))
        except Exception as e:
            logger.error(f"Error checking cache key {key}: {e}")
            return False
    
    def is_connected(self) -> bool:
        """Check if Redis is connected and available"""
        return self.connected