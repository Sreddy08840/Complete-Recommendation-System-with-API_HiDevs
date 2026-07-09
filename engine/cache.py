
"""
In-memory cache for recommendation system using TTLCache.
"""
import logging
from typing import Any, Tuple, Dict
from cachetools import TTLCache
from collections import defaultdict

# Configure logging for cache events
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class RecommendationCache:
    """
    In-memory cache for recommendations with TTL.
    """

    def __init__(self, ttl_seconds: int = 300, max_size: int = 1000):
        """
        Initialize recommendation cache.

        Args:
            ttl_seconds: Time-to-live for cache entries (default 5 minutes)
            max_size: Maximum number of cache entries (default 1000)
        """
        self.cache = TTLCache(maxsize=max_size, ttl=ttl_seconds)
        self.stats = defaultdict(int)

    def get(self, key: Tuple[int, int]) -> Any:
        """
        Get an entry from the cache.

        Args:
            key: Cache key as (user_id, limit) tuple

        Returns:
            Cached value if present, else None
        """
        if key in self.cache:
            self.stats["hits"] += 1
            logger.info(f"Cache HIT: {key}")
            return self.cache[key]
        else:
            self.stats["misses"] += 1
            logger.info(f"Cache MISS: {key}")
            return None

    def set(self, key: Tuple[int, int], value: Any) -> None:
        """
        Set a cache entry.

        Args:
            key: Cache key as (user_id, limit) tuple
            value: Value to cache
        """
        self.cache[key] = value
        logger.info(f"Cache SET: {key}")

    def invalidate_user(self, user_id: int) -> None:
        """
        Invalidate all cache entries for a specific user.

        Args:
            user_id: User ID whose cache entries to invalidate
        """
        keys_to_delete = [
            key for key in self.cache
            if key[0] == user_id
        ]
        for key in keys_to_delete:
            del self.cache[key]
        logger.info(f"Invalidated cache entries for user {user_id}: {len(keys_to_delete)} entries")

    def clear(self) -> None:
        """
        Clear all cache entries.
        """
        self.cache.clear()
        logger.info("Cache cleared completely")

    def get_stats(self) -> Dict[str, int]:
        """
        Get cache statistics.

        Returns:
            Dictionary with stats: hits, misses, current_size, max_size
        """
        stats = {
            "hits": self.stats["hits"],
            "misses": self.stats["misses"],
            "current_size": len(self.cache),
            "max_size": self.cache.maxsize
        }
        logger.info(f"Cache stats: {stats}")
        return stats

    def reset_stats(self) -> None:
        """
        Reset hit and miss counts.
        """
        self.stats.clear()
        logger.info("Cache stats reset")
