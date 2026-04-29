"""
OSRM routing service.
Replaces all Haversine distance calls with real road distances.
Uses:
  - /table/v1/driving/  → NxN distance+duration matrix (batch, efficient)
  - /route/v1/driving/  → single route with GeoJSON geometry (for map rendering)
"""

import requests
import logging
import math
from typing import Optional

logger = logging.getLogger(__name__)

OSRM_BASE_URL = "http://router.project-osrm.org"  # Override with env var in production
OSRM_PROFILE = "driving"
OSRM_TIMEOUT = 30


class OSRMService:
    def __init__(self, base_url: str = OSRM_BASE_URL):
        self.base_url = base_url.rstrip("/")
        self.profile = OSRM_PROFILE
        self._route_cache: dict = {}

    def get_distance_matrix(self, locations: list[tuple[float, float]]) -> dict:
        """
        Build NxN road distance + duration matrix via OSRM /table endpoint.
        Single HTTP call replaces N² haversine calls.

        Args:
            locations: list of (lat, lng) tuples — same order as nodes in optimizer

        Returns:
            {
                "distances": List[List[float]],   # meters, NxN
                "durations": List[List[float]],   # seconds, NxN
                "fallback_used": bool
            }
        """
        if not locations:
            return {"distances": [], "durations": [], "fallback_used": False}

        # OSRM expects lng,lat (GeoJSON order)
        coords_str = ";".join(f"{lng},{lat}" for lat, lng in locations)
        url = f"{self.base_url}/table/v1/{self.profile}/{coords_str}"
        params = {"annotations": "distance,duration"}

        try:
            resp = requests.get(url, params=params, timeout=OSRM_TIMEOUT)
            resp.raise_for_status()
            data = resp.json()

            if data.get("code") != "Ok":
                logger.warning(f"OSRM table non-Ok: {data.get('code')} — falling back to Haversine")
                return self._haversine_matrix_fallback(locations)

            return {
                "distances": data["distances"],
                "durations": data["durations"],
                "fallback_used": False,
            }

        except requests.exceptions.RequestException as e:
            logger.error(f"OSRM table request failed: {e} — falling back to Haversine")
            return self._haversine_matrix_fallback(locations)

    def get_route_geometry(
        self, origin: tuple[float, float], destination: tuple[float, float]
    ) -> dict:
        """
        Get road route geometry between two points for React map rendering.

        Returns:
            {
                "distance_meters": float,
                "duration_seconds": float,
                "geometry": GeoJSON LineString coordinates [[lng,lat], ...],
                "status": "ok" | "error"
            }
        """
        cache_key = f"{origin}|{destination}"
        if cache_key in self._route_cache:
            return self._route_cache[cache_key]

        lat1, lng1 = origin
        lat2, lng2 = destination
        url = f"{self.base_url}/route/v1/{self.profile}/{lng1},{lat1};{lng2},{lat2}"
        params = {"overview": "full", "geometries": "geojson", "steps": "false"}

        try:
            resp = requests.get(url, params=params, timeout=OSRM_TIMEOUT)
            resp.raise_for_status()
            data = resp.json()

            if data.get("code") != "Ok" or not data.get("routes"):
                return {"status": "error", "distance_meters": None, "duration_seconds": None, "geometry": None}

            route = data["routes"][0]
            result = {
                "distance_meters": route["distance"],
                "duration_seconds": route["duration"],
                "geometry": route["geometry"]["coordinates"],  # [[lng,lat], ...]
                "status": "ok",
            }
            self._route_cache[cache_key] = result
            return result

        except requests.exceptions.RequestException as e:
            logger.error(f"OSRM route request failed: {e}")
            return {"status": "error", "distance_meters": None, "duration_seconds": None, "geometry": None}

    def _haversine_matrix_fallback(self, locations: list[tuple[float, float]]) -> dict:
        """Fallback when OSRM is unreachable — uses straight-line Haversine."""
        n = len(locations)
        matrix = [[0.0] * n for _ in range(n)]
        for i in range(n):
            for j in range(n):
                if i != j:
                    matrix[i][j] = self._haversine(locations[i], locations[j])
        return {"distances": matrix, "durations": matrix, "fallback_used": True}

    @staticmethod
    def _haversine(p1: tuple, p2: tuple) -> float:
        R = 6371000
        lat1, lng1 = map(math.radians, p1)
        lat2, lng2 = map(math.radians, p2)
        dlat, dlng = lat2 - lat1, lng2 - lng1
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlng/2)**2
        return R * 2 * math.asin(math.sqrt(a))


# Singleton — import this everywhere
import os
osrm_base_url = os.getenv("OSRM_BASE_URL", OSRM_BASE_URL)
osrm = OSRMService(base_url=osrm_base_url)
