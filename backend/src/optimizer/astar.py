# backend/src/optimizer/astar.py
import heapq
from dataclasses import dataclass, field
from typing import Callable
from src.core.entities import Order

@dataclass(order=True)
class AStarNode:
    f_score:   float
    g_score:   float         = field(compare=False)
    path:      list[Order]   = field(compare=False)
    remaining: frozenset     = field(compare=False)


def astar_route(
    orders:     list[Order],
    start_lat:  float,
    start_lng:  float,
    dist_lookup: dict,
    location_index: dict,
    start_id: str,
    predict_fn: Callable[[Order, float, float], float] = None,
) -> list[Order]:
    """
    Tìm thứ tự giao hàng tối ưu bằng A*.
    Sử dụng dist_lookup (OSRM durations) làm cost và heuristic.
    """
    if not orders:
        return []
    if len(orders) == 1:
        return orders

    all_orders = frozenset(o.order_id for o in orders)
    order_map  = {o.order_id: o for o in orders}

    heap: list[AStarNode] = []
    heapq.heappush(heap, AStarNode(
        f_score=0, g_score=0, path=[], remaining=all_orders
    ))

    closed_set: set[tuple] = set()
    best_cost = float("inf")
    best_path: list[Order] = list(orders)

    while heap:
        node = heapq.heappop(heap)

        # Trạng thái được xác định bởi (điểm cuối hiện tại, danh sách còn lại)
        last_id   = node.path[-1].order_id if node.path else start_id
        state_key = (last_id, node.remaining)
        if state_key in closed_set:
            continue
        closed_set.add(state_key)

        if not node.remaining:
            if node.g_score < best_cost:
                best_cost = node.g_score
                best_path = node.path
            continue

        if node.g_score >= best_cost:
            continue

        for oid in node.remaining:
            next_order = order_map[oid]
            cur_id = node.path[-1].order_id if node.path else start_id
            
            idx1 = location_index[cur_id]
            idx2 = location_index[next_order.order_id]
            travel_time = dist_lookup.get((idx1, idx2), 0)
            
            remaining_after = node.remaining - {oid}
            
            # Heuristic: Tổng duration từ điểm hiện tại đến tất cả các điểm còn lại
            # Đây là một heuristic đơn giản và an toàn (admissible if durations are >= 0)
            h_new = 0
            for rid in remaining_after:
                idx_r = location_index[rid]
                h_new += dist_lookup.get((idx2, idx_r), 0)

            g_new = node.g_score + travel_time

            heapq.heappush(heap, AStarNode(
                f_score   = g_new + h_new,
                g_score   = g_new,
                path      = node.path + [next_order],
                remaining = remaining_after,
            ))

    return best_path
