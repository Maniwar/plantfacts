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
        self.redis_client = None
        self.connected = False
        self.error_message = None
        
        try:
            # Check if we're in development mode (no Redis)
            if "REDIS_HOST" not in st.secrets:
                logger.info("Redis not configured - running without cache")
                self.error_message = "Redis not configured (optional)"
                return
            
            # Check if Redis secrets exist and are not empty
            host = st.secrets.get("REDIS_HOST", "").strip()
            port = st.secrets.get("REDIS_PORT", 6379)
            password = st.secrets.get("REDIS_PASSWORD", "").strip()
            
            if not host:
                logger.warning("Redis host is empty - running without cache")
                self.error_message = "Redis host not provided"
                return
            
            logger.info(f"Attempting Redis connection to {host}:{port}")
            
            # Configure Redis connection with better defaults
            self.redis_client = redis.Redis(
                host=host,
                port=int(port),
                password=password if password else None,
                decode_responses=True,
                socket_keepalive=True,
                socket_connect_timeout=3,  # Reduced timeout
                retry_on_timeout=True,
                retry_on_error=[redis.ConnectionError, redis.TimeoutError],
                health_check_interval=30
            )
            
            # Test connection with timeout
            self.redis_client.ping()
            self.connected = True
            self.error_message = None
            logger.info(f"✅ Redis connected successfully to {host}:{port}")
            
        except redis.ConnectionError as e:
            logger.warning(f"Redis connection failed (app will work without cache): {str(e)[:100]}")
            self.redis_client = None
            self.connected = False
            self.error_message = "Redis connection failed (optional feature)"
        except redis.TimeoutError as e:
            logger.warning(f"Redis timeout (app will work without cache): {str(e)[:100]}")
            self.redis_client = None
            self.connected = False
            self.error_message = "Redis timeout (optional feature)"
        except ValueError as e:
            logger.error(f"Invalid Redis configuration: {e}")
            self.redis_client = None
            self.connected = False
            self.error_message = f"Invalid config: {str(e)[:50]}"
        except Exception as e:
            logger.warning(f"Redis initialization failed (app will work without cache): {str(e)[:100]}")
            self.redis_client = None
            self.connected = False
            self.error_message = "Cache unavailable (optional)"
    
    def get(self, key: str) -> Optional[str]:
        """
        Get value from cache
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found or cache disabled
        """
        if not self.connected or not self.redis_client:
            return None
            
        try:
            value = self.redis_client.get(key)
            if value:
                logger.debug(f"Cache HIT for key: {key}")
            return value
        except (redis.ConnectionError, redis.TimeoutError) as e:
            logger.debug(f"Cache get failed for {key}: {str(e)[:50]}")
            # Don't crash the app if cache fails
            self.connected = False
            return None
        except Exception as e:
            logger.debug(f"Unexpected cache error for {key}: {str(e)[:50]}")
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
        if not self.connected or not self.redis_client:
            return False
            
        try:
            if expire:
                self.redis_client.setex(key, expire, value)
            else:
                self.redis_client.set(key, value)
            logger.debug(f"Cache SET for key: {key} (size: {len(value)} chars)")
            return True
        except (redis.ConnectionError, redis.TimeoutError) as e:
            logger.debug(f"Cache set failed for {key}: {str(e)[:50]}")
            self.connected = False
            return False
        except Exception as e:
            logger.debug(f"Unexpected cache error setting {key}: {str(e)[:50]}")
            return False
    
    def delete(self, key: str) -> bool:
        """
        Delete key from cache
        
        Args:
            key: Cache key to delete
            
        Returns:
            True if successful, False otherwise
        """
        if not self.connected or not self.redis_client:
            return False
            
        try:
            result = self.redis_client.delete(key)
            return bool(result)
        except Exception as e:
            logger.debug(f"Error deleting cache key {key}: {str(e)[:50]}")
            return False
    
    def exists(self, key: str) -> bool:
        """
        Check if key exists in cache
        
        Args:
            key: Cache key to check
            
        Returns:
            True if key exists, False otherwise
        """
        if not self.connected or not self.redis_client:
            return False
            
        try:
            return bool(self.redis_client.exists(key))
        except Exception as e:
            logger.debug(f"Error checking cache key {key}: {str(e)[:50]}")
            return False
    
    def is_connected(self) -> bool:
        """Check if Redis is connected and available"""
        if not self.redis_client:
            return False
            
        if self.connected:
            # Periodic health check
            try:
                self.redis_client.ping()
                return True
            except:
                self.connected = False
                return False
        return False
    
    def get_error_message(self) -> Optional[str]:
        """Get connection error message if any"""
        return self.error_message
