
from typing import List, Tuple, Set
from abc import ABC, abstractmethod
from core.point import Point
from core.map import Map


class Solver(ABC):
    """Abstract base class for solvers"""

    def __init__(self, map_data: Map):
        self.map_data = map_data
        self.route = []
        self.surveyed_objects = set()
        self.total_distance = 0.0

    @abstractmethod
    def solve(self) -> Tuple[List[Point], Set[Point], float]:
        """Solve the routing problem"""
        pass

    def calculate_route_distance(self, route: List[Point]) -> float:
        """Calculate total route distance"""
        if len(route) < 2:
            return 0.0

        total_distance = 0.0
        for i in range(len(route) - 1):
            total_distance += route[i].distance_to(route[i + 1])
        return total_distance

    def get_surveyed_objects(self, route: List[Point]) -> Set[Point]:
        """Determine which objects are surveyed by the route"""
        surveyed = set()
        route = [self.map_data.start_point] + route + [self.map_data.end_point]

        for obj in self.map_data.objects:
            for i in range(len(route) - 1):
                a = route[i]
                b = route[i + 1]
                if obj.distance_point_to_segment(a, b) <= self.map_data.survey_radius:
                    surveyed.add(obj)
                    break

        return surveyed

    def is_valid_route(self, route: List[Point]) -> bool:
        """Check if route is valid"""
        if len(route) < 2:
            return False

        # Check if route starts at start point and ends at end point
        if route[0] != self.map_data.start_point or route[-1] != self.map_data.end_point:
            return False

        # Check if total distance is within limit
        total_distance = self.calculate_route_distance(route)
        return total_distance <= self.map_data.max_distance