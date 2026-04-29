# backend/src/api/routes/optimize.py
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Dict
from src.core.entities import Order, Shipper, ShipperStatus
from src.optimizer.cluster_assign import cluster_and_assign
from src.optimizer.astar import astar_route
from src.infra.dependencies import get_prediction_service
from datetime import datetime
from src.utils.geo import haversine
from src.services.prediction_service import PredictionService
from src.services.osrm_service import osrm

router = APIRouter(prefix="/api/v1")

class OrderSchema(BaseModel):
    order_id: str
    latitude: float
    longitude: float
    weight_kg: float

class ShipperSchema(BaseModel):
    shipper_id: str
    current_lat: float
    current_lng: float
    status: str
    max_load_kg: float

class OptimizeRequest(BaseModel):
    orders: List[OrderSchema]
    shippers: List[ShipperSchema]

class RouteResponse(BaseModel):
    shipper_id: str
    route: List[str] # List of order_ids

class RouteSegment(BaseModel):
    origin: List[float] # [lat, lng]
    destination: List[float]

class RouteGeometryRequest(BaseModel):
    segments: List[RouteSegment]

@router.post("/route_geometry")
def get_route_geometry(body: RouteGeometryRequest):
    results = []
    for seg in body.segments:
        result = osrm.get_route_geometry(
            tuple(seg.origin),
            tuple(seg.destination)
        )
        results.append(result)
    return {"segments": results}

@router.post("/optimize_route", response_model=List[RouteResponse])
def optimize_route(
    req: OptimizeRequest,
    svc: PredictionService = Depends(get_prediction_service),
):
    if not req.orders or not req.shippers:
        return []

    # Convert schemas to domain entities
    domain_orders = [
        Order(order_id=o.order_id, latitude=o.latitude, longitude=o.longitude, placed_at=None, weight_kg=o.weight_kg)
        for o in req.orders
    ]
    domain_shippers = [
        Shipper(
            shipper_id=s.shipper_id, 
            current_lat=s.current_lat, 
            current_lng=s.current_lng, 
            status=ShipperStatus(s.status), 
            max_load_kg=s.max_load_kg
        )
        for s in req.shippers
    ]

    try:
        # Cluster orders to shippers
        clusters = cluster_and_assign(domain_orders, domain_shippers)
        
        results = []
        hour = datetime.now().hour

        # Build one OSRM distance matrix for all locations
        all_locations = []
        location_index = {}
        for s in domain_shippers:
            location_index[s.shipper_id] = len(all_locations)
            all_locations.append((s.current_lat, s.current_lng))
        for o in domain_orders:
            location_index[o.order_id] = len(all_locations)
            all_locations.append((o.latitude, o.longitude))
        
        matrix_result = osrm.get_distance_matrix(all_locations)
        duration_matrix = matrix_result["durations"]
        dist_lookup = {
            (i, j): duration_matrix[i][j]
            for i in range(len(all_locations))
            for j in range(len(all_locations))
        }
        
        for shipper_id, cluster_orders in clusters.items():
            if not cluster_orders:
                results.append(RouteResponse(shipper_id=shipper_id, route=[]))
                continue
            
            # Find shipper entity for start coordinates
            shipper = next(s for s in domain_shippers if s.shipper_id == shipper_id)
            
            # Safeguard: If cluster size > 10, A* will likely timeout. 
            # Use simple greedy approach as fallback.
            if len(cluster_orders) > 10:
                # Simple Nearest Neighbor greedy approach using OSRM durations
                path = []
                remaining = list(cluster_orders)
                curr_id = shipper.shipper_id
                while remaining:
                    # Find nearest next order based on OSRM duration
                    curr_idx = location_index[curr_id]
                    next_idx = min(range(len(remaining)), 
                                   key=lambda i: dist_lookup.get((curr_idx, location_index[remaining[i].order_id]), float('inf')))
                    next_order = remaining.pop(next_idx)
                    path.append(next_order)
                    curr_id = next_order.order_id
                optimized_path = path
            else:
                # Run A*
                optimized_path = astar_route(
                    orders=cluster_orders, 
                    start_lat=shipper.current_lat, 
                    start_lng=shipper.current_lng, 
                    dist_lookup=dist_lookup,
                    location_index=location_index,
                    start_id=shipper.shipper_id
                )
            
            results.append(RouteResponse(shipper_id=shipper_id, route=[o.order_id for o in optimized_path]))
            
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
