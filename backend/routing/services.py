import math
from typing import List, Optional

import numpy as np
from sklearn.cluster import KMeans

from rides.services import haversine_km


def _nearest_route(points: List[dict]):
    if not points:
        return []
    remaining = points[:]
    route = [remaining.pop(0)]
    while remaining:
        last = route[-1]
        next_idx = 0
        best_dist = float("inf")
        for idx, pt in enumerate(remaining):
            dist = haversine_km(last["lat"], last["lng"], pt["lat"], pt["lng"])
            if dist < best_dist:
                best_dist = dist
                next_idx = idx
        route.append(remaining.pop(next_idx))
    return route


def optimize_route(points: List[dict], clusters: Optional[int] = None):
    if len(points) <= 2:
        return points

    pts = np.array([[p["lat"], p["lng"]] for p in points])
    k = clusters or max(1, min(5, int(math.sqrt(len(points)))))
    if k > len(points):
        k = len(points)

    kmeans = KMeans(n_clusters=k, n_init=10, random_state=42)
    labels = kmeans.fit_predict(pts)

    clustered = {}
    for idx, label in enumerate(labels):
        clustered.setdefault(label, []).append(points[idx])

    centers = kmeans.cluster_centers_
    center_points = [
        {"lat": centers[i][0], "lng": centers[i][1], "label": i}
        for i in range(len(centers))
    ]

    ordered_centers = _nearest_route(center_points)
    optimized = []
    for center in ordered_centers:
        cluster_points = clustered.get(center["label"], [])
        optimized.extend(_nearest_route(cluster_points))

    return optimized
