"""
Fast-F1 Client

Wrapper around the Fast-F1 library for retrieving F1 session data
with caching and error handling.
"""

import time
from typing import Any, Dict, List, Optional, Tuple
import pandas as pd

try:
    import fastf1
    from fastf1.core import Session, Laps
except ImportError:
    fastf1 = None
    Session = None
    Laps = None

from .cache_manager import CacheManager


class FastF1Client:
    """
    Client for accessing F1 data via the Fast-F1 library.
    
    Provides methods to retrieve tyre data, speed data, lap times,
    and weather information with automatic caching and retry logic.
    """
    
    def __init__(self, cache_manager: Optional[CacheManager] = None):
        """
        Initialize the Fast-F1 client.
        
        Args:
            cache_manager: CacheManager instance for data caching.
                          If None, creates a new instance.
        
        Raises:
            ImportError: If fastf1 library is not installed
        """
        if fastf1 is None:
            raise ImportError(
                "fastf1 library is not installed. "
                "Install it with: pip install fastf1>=3.0.0"
            )
        
        self.cache_manager = cache_manager or CacheManager()
        
        # Configure Fast-F1 to use our cache directory
        fastf1_cache_dir = self.cache_manager.cache_dir / 'fastf1'
        fastf1_cache_dir.mkdir(parents=True, exist_ok=True)
        fastf1.Cache.enable_cache(str(fastf1_cache_dir))
        
        # Retry configuration
        self.max_retries = 3
        self.retry_delay = 2  # seconds
    
    def _load_session_with_retry(
        self, 
        year: int, 
        event: str, 
        session_type: str
    ) -> Any:
        """
        Load a session with retry logic.
        
        Args:
            year: Season year
            event: Event name (e.g., 'Monaco', 'Silverstone')
            session_type: Type of session ('Race', 'Qualifying', 'FP1', etc.)
        
        Returns:
            Loaded Fast-F1 Session object
        
        Raises:
            Exception: If session cannot be loaded after retries
        """
        # Check cache first
        cached_session = self.cache_manager.load_session_data(
            year, event, session_type
        )
        if cached_session is not None:
            return cached_session
        
        # Load from Fast-F1 with retries
        last_error = None
        for attempt in range(self.max_retries):
            try:
                session = fastf1.get_session(year, event, session_type)
                session.load()
                
                # Cache the loaded session
                self.cache_manager.save_session_data(
                    year, event, session_type, session
                )
                
                return session
            except Exception as e:
                last_error = e
                if attempt < self.max_retries - 1:
                    print(f"Attempt {attempt + 1} failed: {e}. Retrying...")
                    time.sleep(self.retry_delay)
                else:
                    print(f"All {self.max_retries} attempts failed.")
        
        raise Exception(
            f"Failed to load session {year} {event} {session_type} "
            f"after {self.max_retries} attempts: {last_error}"
        )
    
    def get_tyre_data(
        self, 
        year: int, 
        event: str, 
        session_type: str,
        driver: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Get tyre compound data for a session.
        
        Args:
            year: Season year
            event: Event name
            session_type: Type of session
            driver: Driver abbreviation (e.g., 'VER', 'HAM'). 
                   If None, returns data for all drivers.
        
        Returns:
            DataFrame with columns: Driver, Lap, Compound, TyreLife, LapTime
        
        Raises:
            Exception: If data cannot be retrieved
        """
        session = self._load_session_with_retry(year, event, session_type)
        
        # Get laps data
        if driver:
            laps = session.laps.pick_driver(driver)
        else:
            laps = session.laps
        
        # Extract relevant tyre information
        tyre_data = laps[['Driver', 'LapNumber', 'Compound', 'TyreLife', 'LapTime']].copy()
        tyre_data.columns = ['Driver', 'Lap', 'Compound', 'TyreLife', 'LapTime']
        
        return tyre_data
    
    def get_speed_data(
        self, 
        year: int, 
        event: str, 
        session_type: str,
        driver: str,
        lap_number: Optional[int] = None
    ) -> pd.DataFrame:
        """
        Get speed telemetry data for a driver.
        
        Args:
            year: Season year
            event: Event name
            session_type: Type of session
            driver: Driver abbreviation (e.g., 'VER', 'HAM')
            lap_number: Specific lap number. If None, returns fastest lap.
        
        Returns:
            DataFrame with telemetry data including Speed, Distance, Time
        
        Raises:
            Exception: If data cannot be retrieved
        """
        session = self._load_session_with_retry(year, event, session_type)
        
        # Get driver laps
        driver_laps = session.laps.pick_driver(driver)
        
        if driver_laps.empty:
            raise ValueError(f"No laps found for driver {driver}")
        
        # Select lap
        if lap_number is not None:
            lap = driver_laps[driver_laps['LapNumber'] == lap_number].iloc[0]
        else:
            # Get fastest lap
            lap = driver_laps.pick_fastest()
        
        # Get telemetry
        telemetry = lap.get_telemetry()
        
        return telemetry
    
    def get_lap_times(
        self, 
        year: int, 
        event: str, 
        session_type: str,
        driver: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Get lap times for a session.
        
        Args:
            year: Season year
            event: Event name
            session_type: Type of session
            driver: Driver abbreviation. If None, returns all drivers.
        
        Returns:
            DataFrame with lap time data
        
        Raises:
            Exception: If data cannot be retrieved
        """
        session = self._load_session_with_retry(year, event, session_type)
        
        if driver:
            laps = session.laps.pick_driver(driver)
        else:
            laps = session.laps
        
        # Extract relevant lap time information
        lap_times = laps[[
            'Driver', 'LapNumber', 'LapTime', 'Sector1Time', 
            'Sector2Time', 'Sector3Time', 'Compound'
        ]].copy()
        
        return lap_times
    
    def get_weather_data(
        self, 
        year: int, 
        event: str, 
        session_type: str
    ) -> pd.DataFrame:
        """
        Get weather data for a session.
        
        Args:
            year: Season year
            event: Event name
            session_type: Type of session
        
        Returns:
            DataFrame with weather data including temperature, humidity, etc.
        
        Raises:
            Exception: If data cannot be retrieved
        """
        session = self._load_session_with_retry(year, event, session_type)
        
        # Get weather data
        weather = session.weather_data
        
        return weather
    
    def get_session_info(
        self, 
        year: int, 
        event: str, 
        session_type: str
    ) -> Dict[str, Any]:
        """
        Get general information about a session.
        
        Args:
            year: Season year
            event: Event name
            session_type: Type of session
        
        Returns:
            Dictionary with session metadata
        
        Raises:
            Exception: If data cannot be retrieved
        """
        session = self._load_session_with_retry(year, event, session_type)
        
        return {
            'event': session.event['EventName'],
            'location': session.event['Location'],
            'country': session.event['Country'],
            'session_type': session_type,
            'date': str(session.date),
            'total_laps': len(session.laps),
            'drivers': sorted(session.laps['Driver'].unique().tolist())
        }
    
    def get_driver_standings(
        self,
        year: int,
        event: str
    ) -> List[Dict[str, Any]]:
        """
        Get driver championship standings after a specific event.
        
        Args:
            year: Season year
            event: Event name
        
        Returns:
            List of dictionaries with driver standings
        
        Raises:
            Exception: If data cannot be retrieved
        """
        # Load race session to get results
        session = self._load_session_with_retry(year, event, 'Race')
        
        results = session.results
        
        standings = []
        for _, row in results.iterrows():
            standings.append({
                'position': row['Position'],
                'driver': row['Abbreviation'],
                'driver_name': row['FullName'],
                'team': row['TeamName'],
                'points': row.get('Points', 0)
            })
        
        return standings
    
    def compare_drivers(
        self,
        year: int,
        event: str,
        session_type: str,
        driver1: str,
        driver2: str,
        lap_number: Optional[int] = None
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Compare telemetry data between two drivers.
        
        Args:
            year: Season year
            event: Event name
            session_type: Type of session
            driver1: First driver abbreviation
            driver2: Second driver abbreviation
            lap_number: Specific lap to compare. If None, uses fastest laps.
        
        Returns:
            Tuple of (driver1_telemetry, driver2_telemetry)
        
        Raises:
            Exception: If data cannot be retrieved
        """
        telemetry1 = self.get_speed_data(year, event, session_type, driver1, lap_number)
        telemetry2 = self.get_speed_data(year, event, session_type, driver2, lap_number)
        
        return telemetry1, telemetry2

# Made with Bob
