"""
Element Cache - Vision Element Caching

Reduces API calls by caching detected element locations.
Significantly improves performance and reduces rate limit issues.
"""

from datetime import datetime, timedelta
from typing import Any, Dict, Optional, Tuple
from dataclasses import dataclass
import hashlib


@dataclass
class CachedElement:
    """Cached element location"""
    element_type: str
    description: str
    x: int
    y: int
    confidence: float
    selector_hint: Optional[str]
    cached_at: datetime
    page_url: str
    page_hash: str  # Hash of page content for invalidation


class ElementCache:
    """
    Cache for vision-detected UI elements
    
    Features:
    - TTL-based expiration
    - Page URL scoping
    - Content-based invalidation
    - Hit rate tracking
    """
    
    def __init__(self, ttl_seconds: int = 30, max_entries: int = 500):
        """
        Initialize element cache
        
        Args:
            ttl_seconds: Time-to-live for cached elements
            max_entries: Maximum cache entries before eviction
        """
        self.ttl = timedelta(seconds=ttl_seconds)
        self.max_entries = max_entries
        self.cache: Dict[str, CachedElement] = {}
        
        # Statistics
        self.hits = 0
        self.misses = 0
        self.evictions = 0
    
    def _make_key(self, page_url: str, element_desc: str, element_type: str) -> str:
        """Create cache key from page URL and element description"""
        normalized_desc = element_desc.lower().strip()
        return f"{page_url}:{element_type}:{normalized_desc}"
    
    def _hash_page_content(self, content: Optional[str] = None) -> str:
        """Create hash of page content for invalidation"""
        if content:
            return hashlib.md5(content.encode()).hexdigest()[:8]
        return "unknown"
    
    def get(
        self,
        page_url: str,
        element_desc: str,
        element_type: str = "button",
        page_content: Optional[str] = None
    ) -> Optional[CachedElement]:
        """
        Get cached element location
        
        Returns None if:
        - Element not in cache
        - Cache entry expired
        - Page content changed (if page_content provided)
        """
        key = self._make_key(page_url, element_desc, element_type)
        
        if key not in self.cache:
            self.misses += 1
            return None
        
        cached = self.cache[key]
        
        # Check TTL
        if datetime.now() - cached.cached_at > self.ttl:
            del self.cache[key]
            self.misses += 1
            return None
        
        # Check page content hash if provided
        if page_content:
            current_hash = self._hash_page_content(page_content)
            if cached.page_hash != current_hash:
                del self.cache[key]
                self.misses += 1
                return None
        
        self.hits += 1
        return cached
    
    def set(
        self,
        page_url: str,
        element_desc: str,
        element_type: str,
        x: int,
        y: int,
        confidence: float,
        selector_hint: Optional[str] = None,
        page_content: Optional[str] = None
    ):
        """Cache an element location"""
        # Evict oldest entries if at capacity
        if len(self.cache) >= self.max_entries:
            self._evict_oldest()
        
        key = self._make_key(page_url, element_desc, element_type)
        
        self.cache[key] = CachedElement(
            element_type=element_type,
            description=element_desc,
            x=x,
            y=y,
            confidence=confidence,
            selector_hint=selector_hint,
            cached_at=datetime.now(),
            page_url=page_url,
            page_hash=self._hash_page_content(page_content)
        )
    
    def _evict_oldest(self):
        """Evict oldest cache entries"""
        if not self.cache:
            return
        
        # Sort by cached_at and remove oldest 10%
        sorted_keys = sorted(
            self.cache.keys(),
            key=lambda k: self.cache[k].cached_at
        )
        
        evict_count = max(1, len(sorted_keys) // 10)
        for key in sorted_keys[:evict_count]:
            del self.cache[key]
            self.evictions += 1
    
    def invalidate_page(self, page_url: str):
        """Invalidate all cached elements for a page"""
        keys_to_remove = [
            key for key in self.cache
            if self.cache[key].page_url == page_url
        ]
        
        for key in keys_to_remove:
            del self.cache[key]
    
    def invalidate_all(self):
        """Clear entire cache"""
        self.cache.clear()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total_requests = self.hits + self.misses
        hit_rate = self.hits / total_requests if total_requests > 0 else 0
        
        return {
            "entries": len(self.cache),
            "max_entries": self.max_entries,
            "ttl_seconds": self.ttl.total_seconds(),
            "hits": self.hits,
            "misses": self.misses,
            "evictions": self.evictions,
            "hit_rate": round(hit_rate * 100, 2),
            "api_calls_saved": self.hits
        }
    
    def get_cached_elements(self, page_url: Optional[str] = None) -> list[Dict[str, Any]]:
        """Get list of cached elements, optionally filtered by page"""
        elements = []
        
        for key, cached in self.cache.items():
            if page_url and cached.page_url != page_url:
                continue
            
            age_seconds = (datetime.now() - cached.cached_at).total_seconds()
            
            elements.append({
                "description": cached.description,
                "element_type": cached.element_type,
                "x": cached.x,
                "y": cached.y,
                "confidence": cached.confidence,
                "selector_hint": cached.selector_hint,
                "page_url": cached.page_url,
                "age_seconds": round(age_seconds, 1),
                "expires_in": round(self.ttl.total_seconds() - age_seconds, 1)
            })
        
        return elements


# Global element cache instance
_element_cache: Optional[ElementCache] = None


def get_element_cache() -> ElementCache:
    """Get or create global element cache"""
    global _element_cache
    if _element_cache is None:
        _element_cache = ElementCache()
    return _element_cache


def init_element_cache(ttl_seconds: int = 30, max_entries: int = 500) -> ElementCache:
    """Initialize global element cache with custom settings"""
    global _element_cache
    _element_cache = ElementCache(ttl_seconds=ttl_seconds, max_entries=max_entries)
    return _element_cache
