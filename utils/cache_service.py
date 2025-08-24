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
            # Check if Redis secrets exist
            if not all(key in st.secrets for key in ["REDIS_HOST", "REDIS_PORT", "REDIS_PASSWORD"]):
                logger.warning("Redis secrets not found in st.secrets")
                self.redis_client = None
                self.connected = False
                self.error_message = "Redis credentials not configured"
                return
            
            # Get connection parameters
            host = st.secrets["REDIS_HOST"]
            port = int(st.secrets["REDIS_PORT"])
            password = st.secrets["REDIS_PASSWORD"]
            
            logger.info(f"Attempting Redis connection to {host}:{port}")
            
            self.redis_client = redis.Redis(
                host=host,
                port=port,
                password=password if password else None,  # Handle empty password
                decode_responses=True,
                socket_keepalive=True,
                socket_connect_timeout=5,  # 5 second timeout
                socket_keepalive_options={
                    1: 1,  # TCP_KEEPIDLE
                    2: 1,  # TCP_KEEPINTVL
                    3: 5,  # TCP_KEEPCNT
                }
            )
            # Test connection
            self.redis_client.ping()
            self.connected = True
            self.error_message = None
            logger.info(f"Redis connection established successfully to {host}:{port}")
        except KeyError as e:
            logger.error(f"Missing Redis configuration key: {e}")
            self.redis_client = None
            self.connected = False
            self.error_message = f"Missing config: {e}"
        except redis.ConnectionError as e:
            logger.error(f"Redis connection failed: {e}")
            self.redis_client = None
            self.connected = False
            self.error_message = f"Connection failed: Check if Redis server is running"
        except Exception as e:
            logger.error(f"Unexpected error connecting to Redis: {e}")
            self.redis_client = None
            self.connected = False
            self.error_message = str(e)
    
    def get(self, key: str) -> Optional[str]:
        """
        Get value from cache
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found or cache disabled
        """
        if not self.connected:
            logger.warning("Redis not connected - cache disabled")
            return None
            
        try:
            value = self.redis_client.get(key)
            if value:
                logger.info(f"Cache HIT for key: {key}")
            else:
                logger.info(f"Cache MISS for key: {key}")
            return value
        except Exception as e:
            logger.error(f"Error getting cache key {key}: {e}")
            return None
    
    def set(self, key: str, value: str, expire: Optional[int] = None) -> bool:
        """
        Set value in cache
        
        Args:
            key: Cache key
            value: Value to cache
            expire: Optional expiration time in seconds (None = no expiration)
            
        Returns:
            True if successful, False otherwise
        """
        if not self.connected:
            logger.warning("Redis not connected - cannot cache")
            return False
            
        try:
            if expire:
                self.redis_client.setex(key, expire, value)
                logger.info(f"Cache SET for key: {key} (size: {len(value)} chars, TTL: {expire}s)")
            else:
                self.redis_client.set(key, value)
                logger.info(f"Cache SET for key: {key} (size: {len(value)} chars, no expiration)")
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
    
    def get_error_message(self) -> Optional[str]:
        """Get connection error message if any"""
        return getattr(self, 'error_message', None)
