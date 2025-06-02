import numpy as np
from typing import List, Tuple, Set

from core.solver import Solver
from core.point import Point

class GreedySolver(Solver):
    """Greedy algorithm implementation"""

    def solve(self) -> Tuple[List[Point], Set[Point], float]:
        """Solve using greedy approach"""
        route = [self.map_data.start_point]
        surveyed_objects = set()
        current_position = self.map_data.start_point
        route_length = 0.0

        # Copy objects for working
        unsurveyed_objects = set(self.map_data.objects)

        while route_length + current_position.distance_to(
                self.map_data.end_point) <= self.map_data.max_distance and unsurveyed_objects:
            # Find nearest unsurveyed object
            nearest_object = None
            min_distance = float('inf')

            for obj in unsurveyed_objects:
                dist = current_position.distance_to(obj)
                if dist < min_distance:
                    min_distance = dist
                    nearest_object = obj

            if nearest_object is None:
                break

            # Find intersection point with survey circle
            intersection = self._find_intersection_with_circle(
                current_position, nearest_object, nearest_object, self.map_data.survey_radius
            )

            if intersection is None:
                unsurveyed_objects.remove(nearest_object)
                continue

            # Check if we have enough fuel
            new_route_length = route_length + current_position.distance_to(intersection)
            distance_to_end = intersection.distance_to(self.map_data.end_point)
            total_needed = new_route_length + distance_to_end

            if total_needed > self.map_data.max_distance:
                break

            # Add point to route
            route.append(intersection)
            route_length = new_route_length
            current_position = intersection

            # Mark surveyed objects
            objects_to_survey = []
            for obj in unsurveyed_objects:
                if intersection.distance_to(obj) <= self.map_data.survey_radius:
                    objects_to_survey.append(obj)

            for obj in objects_to_survey:
                surveyed_objects.add(obj)
                unsurveyed_objects.remove(obj)

        # Check objects on path to end
        if unsurveyed_objects and route_length + current_position.distance_to(
                self.map_data.end_point) <= self.map_data.max_distance:
            for obj in unsurveyed_objects:
                dist_to_path = self._point_to_line_distance(obj, current_position, self.map_data.end_point)
                if dist_to_path <= self.map_data.survey_radius:
                    surveyed_objects.add(obj)

        # Complete route
        route.append(self.map_data.end_point)
        total_distance = self.calculate_route_distance(route)

        self.route = route
        self.surveyed_objects = surveyed_objects
        self.total_distance = total_distance

        return route, surveyed_objects, total_distance

    def _find_intersection_with_circle(self, start: Point, target: Point, center: Point, radius: float) -> Point:
        """Find intersection point with circle around object"""
        dx = target.x - start.x
        dy = target.y - start.y
        dist = np.sqrt(dx ** 2 + dy ** 2)

        if dist == 0:
            return start

        # Normalized direction vector
        dx /= dist
        dy /= dist

        # Distance from center to start
        dist_to_center = start.distance_to(center)

        # If we're already inside the circle
        if dist_to_center <= radius:
            return start

        # Projection of start->center on direction
        projection = (center.x - start.x) * dx + (center.y - start.y) * dy

        if projection <= 0:
            return None

        # Closest point on line to center
        closest_x = start.x + projection * dx
        closest_y = start.y + projection * dy

        # Distance from center to closest point
        dist_to_line = np.sqrt((center.x - closest_x) ** 2 + (center.y - closest_y) ** 2)

        if dist_to_line > radius:
            return None

        # Distance from closest point to intersection
        offset = np.sqrt(radius ** 2 - dist_to_line ** 2)

        # Intersection point
        intersection_x = closest_x - offset * dx
        intersection_y = closest_y - offset * dy

        return Point(intersection_x, intersection_y)

    def _point_to_line_distance(self, point: Point, line_start: Point, line_end: Point) -> float:
        """Calculate distance from point to line segment"""
        x1, y1 = line_start.x, line_start.y
        x2, y2 = line_end.x, line_end.y
        x0, y0 = point.x, point.y

        line_length = line_start.distance_to(line_end)

        if line_length == 0:
            return point.distance_to(line_start)

        t = max(0, min(1, ((x0 - x1) * (x2 - x1) + (y0 - y1) * (y2 - y1)) / line_length ** 2))

        nearest_x = x1 + t * (x2 - x1)
        nearest_y = y1 + t * (y2 - y1)

        return np.sqrt((x0 - nearest_x) ** 2 + (y0 - nearest_y) ** 2)
