from typing import List
import random
from core.point import Point
from core.map import Map

class DataGenerator:
    """Generates test tasks"""
    def __init__(self, plane_size: float = 200):
        self.plane_size = plane_size
        self.min_objects = 10
        self.max_objects = 50
        self.distance_options = [100, 150, 200, 250, 300, 350, 400, 450, 500]
        self.radius_range = (0, 15)

    def generate_single_task(self, n: int, L: float, r: float) -> Map:
        """Generate single task with specific parameters"""
        # Start and end points
        start = Point(0, random.uniform(0, self.plane_size), "Start")
        end = Point(self.plane_size, random.uniform(0, self.plane_size), "End")

        if start.distance_to(end) > L:
            L = int(start.distance_to(end)*1.2)

        # Create map
        map_data = Map(start, end, L, r)

        # Generate objects
        for i in range(n):
            while True:
                x = random.uniform(0, self.plane_size)
                y = random.uniform(0, self.plane_size)
                new_point = Point(x, y, f"Object_{ i +1}")

                # Check uniqueness
                if self._is_point_unique(new_point, [start, end] + map_data.objects):
                    map_data.add_object(new_point)
                    break

        return map_data

    def generate_test_suite(self) -> List[Map]:
        """Generate comprehensive test suite"""
        test_suite = []

        # Generate tasks with different parameters
        for n in range(self.min_objects, self.max_objects, 5):  # 5, 10, 15, ..., 50 objects
            for L in self.distance_options:
                # Generate 3 different radius values for each combination
                for _ in range(3):
                    r = random.uniform(*self.radius_range)
                    map_data = self.generate_single_task(n, L, r)
                    test_suite.append(map_data)

        return test_suite

    def generate_random_point(self, exclude_points: List[Point] = None) -> Point:
        """Generate random point that doesn't overlap with existing points"""
        if exclude_points is None:
            exclude_points = []

        while True:
            x = random.uniform(0, self.plane_size)
            y = random.uniform(0, self.plane_size)
            new_point = Point(x, y)

            if self._is_point_unique(new_point, exclude_points):
                return new_point

    def _is_point_unique(self, point: Point, existing_points: List[Point]) -> bool:
        """Check if point is unique (doesn't overlap with existing points)"""
        min_distance = 5.0  # Minimum distance between points

        for existing in existing_points:
            if point.distance_to(existing) < min_distance:
                return False
        return True