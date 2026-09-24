"""
Cache Manager for F1 Data

Manages local caching of Fast-F1 session data to minimize API calls
and improve performance.
"""

import json
import os
import pickle
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, Optional


class CacheManager:
    """
    Manages caching of F1 session data with freshness checking.
    
    The cache is organized by year/event/session type to enable
    efficient lookups and cache invalidation.
    """
    
    def __init__(self, cache_dir: Optional[str] = None):
        """
        Initialize the cache manager.
        
        Args:
            cache_dir: Directory for cache storage. Defaults to .f1_data_cache/
                      in the user's home directory.
        """
        if cache_dir is None:
            cache_dir = os.path.join(Path.home(), '.f1_data_cache')
        
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Cache index file tracks metadata for all cached sessions
        self.index_file = self.cache_dir / 'cache_index.json'
        self.index = self._load_index()
        
        # Default cache freshness: 7 days
        self.cache_ttl = timedelta(days=7)
    
    def _load_index(self) -> Dict[str, Any]:
        """
        Load the cache index from disk.
        
        Returns:
            Dictionary containing cache metadata
        """
        if self.index_file.exists():
            try:
                with open(self.index_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Warning: Could not load cache index: {e}")
                return {}
        return {}
    
    def _save_index(self) -> None:
        """Save the cache index to disk."""
        try:
            with open(self.index_file, 'w') as f:
                json.dump(self.index, f, indent=2)
        except IOError as e:
            print(f"Warning: Could not save cache index: {e}")
    
    def _get_cache_key(self, year: int, event: str, session_type: str) -> str:
        """
        Generate a cache key for a session.
        
        Args:
            year: Season year
            event: Event name (e.g., 'Monaco', 'Silverstone')
            session_type: Type of session ('Race', 'Qualifying', 'Practice 1', etc.)
        
        Returns:
            Cache key string
        """
        # Normalize inputs for consistent keys
        event_normalized = event.lower().replace(' ', '_')
        session_normalized = session_type.lower().replace(' ', '_')
        return f"{year}_{event_normalized}_{session_normalized}"
    
    def _get_cache_path(self, cache_key: str) -> Path:
        """
        Get the file path for a cache key.
        
        Args:
            cache_key: Cache key string
        
        Returns:
            Path to cache file
        """
        return self.cache_dir / f"{cache_key}.pkl"
    
    def is_cache_fresh(self, year: int, event: str, session_type: str) -> bool:
        """
        Check if cached data exists and is still fresh.
        
        Args:
            year: Season year
            event: Event name
            session_type: Type of session
        
        Returns:
            True if cache exists and is fresh, False otherwise
        """
        cache_key = self._get_cache_key(year, event, session_type)
        
        if cache_key not in self.index:
            return False
        
        cache_info = self.index[cache_key]
        cached_time = datetime.fromisoformat(cache_info['timestamp'])
        
        # Check if cache has expired
        if datetime.now() - cached_time > self.cache_ttl:
            return False
        
        # Check if cache file still exists
        cache_path = self._get_cache_path(cache_key)
        return cache_path.exists()
    
    def load_session_data(
        self, 
        year: int, 
        event: str, 
        session_type: str
    ) -> Optional[Any]:
        """
        Load cached session data.
        
        Args:
            year: Season year
            event: Event name
            session_type: Type of session
        
        Returns:
            Cached session data if available and fresh, None otherwise
        """
        if not self.is_cache_fresh(year, event, session_type):
            return None
        
        cache_key = self._get_cache_key(year, event, session_type)
        cache_path = self._get_cache_path(cache_key)
        
        try:
            with open(cache_path, 'rb') as f:
                return pickle.load(f)
        except (pickle.PickleError, IOError) as e:
            print(f"Warning: Could not load cached data for {cache_key}: {e}")
            return None
    
    def save_session_data(
        self, 
        year: int, 
        event: str, 
        session_type: str, 
        data: Any
    ) -> bool:
        """
        Save session data to cache.
        
        Args:
            year: Season year
            event: Event name
            session_type: Type of session
            data: Session data to cache
        
        Returns:
            True if save was successful, False otherwise
        """
        cache_key = self._get_cache_key(year, event, session_type)
        cache_path = self._get_cache_path(cache_key)
        
        try:
            # Save the data
            with open(cache_path, 'wb') as f:
                pickle.dump(data, f)
            
            # Update index
            self.index[cache_key] = {
                'year': year,
                'event': event,
                'session_type': session_type,
                'timestamp': datetime.now().isoformat(),
                'file_size': cache_path.stat().st_size
            }
            self._save_index()
            
            return True
        except (pickle.PickleError, IOError) as e:
            print(f"Warning: Could not save data to cache for {cache_key}: {e}")
            return False
    
    def clear_cache(self, year: Optional[int] = None) -> int:
        """
        Clear cached data.
        
        Args:
            year: If specified, only clear cache for this year.
                 If None, clear all cache.
        
        Returns:
            Number of cache entries cleared
        """
        cleared_count = 0
        keys_to_remove = []
        
        for cache_key, cache_info in self.index.items():
            if year is None or cache_info['year'] == year:
                cache_path = self._get_cache_path(cache_key)
                try:
                    if cache_path.exists():
                        cache_path.unlink()
                    keys_to_remove.append(cache_key)
                    cleared_count += 1
                except IOError as e:
                    print(f"Warning: Could not delete cache file {cache_path}: {e}")
        
        # Remove from index
        for key in keys_to_remove:
            del self.index[key]
        
        self._save_index()
        return cleared_count
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the cache.
        
        Returns:
            Dictionary with cache statistics
        """
        total_size = 0
        entry_count = len(self.index)
        
        for cache_key in self.index:
            cache_path = self._get_cache_path(cache_key)
            if cache_path.exists():
                total_size += cache_path.stat().st_size
        
        return {
            'entry_count': entry_count,
            'total_size_bytes': total_size,
            'total_size_mb': round(total_size / (1024 * 1024), 2),
            'cache_directory': str(self.cache_dir)
        }

# Made with Bob
