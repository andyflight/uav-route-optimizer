import numpy as np
from typing import List, Tuple, Set
from core.solver import Solver
from core.point import Point
from core.map import Map


class HeuristicSolver(Solver):
    """Metaheuristic algorithm implementation"""

    def __init__(self, map_data: Map):
        super().__init__(map_data)
        self.max_iterations = 50

    def solve(self) -> Tuple[List[Point], Set[Point], float]:
        """Solve using metaheuristic approach"""
        # Initial greedy route
        route = self._greedy_initial_route()
        iteration = 0

        while iteration < self.max_iterations:
            # Local search
            route = self._local_search_2opt(route)

            # Geometric optimization
            route = self._geometric_optimization(route)

            # Check constraint
            current_distance = self.calculate_route_distance(route)
            if current_distance <= self.map_data.max_distance:
                break

            # Remove farthest point if route is too long
            route = self._remove_farthest_point(route)

            if len(route) <= 2:
                break

            iteration += 1

        surveyed_objects = self.get_surveyed_objects(route)
        total_distance = self.calculate_route_distance(route)

        self.route = route
        self.surveyed_objects = surveyed_objects
        self.total_distance = total_distance

        return route, surveyed_objects, total_distance

    def _greedy_initial_route(self) -> List[Point]:
        """Build initial route using greedy algorithm"""
        route = [self.map_data.start_point]
        remaining_objects = self.map_data.objects.copy()
        current_position = self.map_data.start_point

        while remaining_objects:
            closest_obj = min(remaining_objects, key=lambda obj: current_position.distance_to(obj))
            route.append(closest_obj)
            remaining_objects.remove(closest_obj)
            current_position = closest_obj

        route.append(self.map_data.end_point)
        return route

    def _local_search_2opt(self, route: List[Point]) -> List[Point]:
        """Local search using 2-opt"""
        best_route = route.copy()
        best_distance = self.calculate_route_distance(best_route)
        improved = True

        while improved:
            improved = False
            for i in range(1, len(route) - 2):
                for j in range(i + 1, len(route) - 1):
                    # Create new route with reversed segment
                    new_route = route[:i] + route[i:j + 1][::-1] + route[j + 1:]
                    new_distance = self.calculate_route_distance(new_route)

                    if new_distance < best_distance:
                        best_route = new_route
                        best_distance = new_distance
                        route = new_route
                        improved = True
                        break
                if improved:
                    break

        return best_route

    def _geometric_optimization(self, route: List[Point]) -> List[Point]:
        """Geometric optimization of point positions"""
        optimized_route = route.copy()

        for i in range(1, len(route) - 1):
            original_obj = None
            # Find original object for this route point
            for obj in self.map_data.objects:
                if route[i].distance_to(obj) <= self.map_data.survey_radius:
                    original_obj = obj
                    break

            if original_obj:
                new_position = self._optimize_point_position(
                    original_obj, route[i - 1], route[i + 1]
                )

                # Check if this improves the route
                old_dist = route[i - 1].distance_to(route[i]) + route[i].distance_to(route[i + 1])
                new_dist = route[i - 1].distance_to(new_position) + new_position.distance_to(route[i + 1])

                if new_dist < old_dist:
                    optimized_route[i] = new_position

        return optimized_route

    def _remove_farthest_point(self, route: List[Point]) -> List[Point]:
        """Remove the point that least affects the route"""
        if len(route) <= 3:
            return [self.map_data.start_point, self.map_data.end_point]

        best_route = route
        min_distance = self.calculate_route_distance(route)

        for i in range(1, len(route) - 1):
            temp_route = route[:i] + route[i + 1:]
            temp_distance = self.calculate_route_distance(temp_route)

            if temp_distance < min_distance:
                min_distance = temp_distance
                best_route = temp_route

        return best_route

    def _project_point_on_segment(self, point: Point, seg_start: Point, seg_end: Point) -> Point:
        """Project point onto line segment"""
        seg_vec_x = seg_end.x - seg_start.x
        seg_vec_y = seg_end.y - seg_start.y

        point_vec_x = point.x - seg_start.x
        point_vec_y = point.y - seg_start.y

        seg_len_sq = seg_vec_x ** 2 + seg_vec_y ** 2

        if seg_len_sq == 0:
            return seg_start

        t = max(0, min(1, (point_vec_x * seg_vec_x + point_vec_y * seg_vec_y) / seg_len_sq))

        proj_x = seg_start.x + t * seg_vec_x
        proj_y = seg_start.y + t * seg_vec_y

        return Point(proj_x, proj_y)

    def _optimize_point_position(self, obj_point: Point, prev_point: Point, next_point: Point) -> Point:
        """Optimize position of point on survey radius boundary"""
        projection = self._project_point_on_segment(obj_point, prev_point, next_point)

        to_proj_x = projection.x - obj_point.x
        to_proj_y = projection.y - obj_point.y
        dist_to_proj = np.sqrt(to_proj_x ** 2 + to_proj_y ** 2)

        if dist_to_proj == 0:
            return obj_point

        # Normalize vector
        to_proj_x /= dist_to_proj
        to_proj_y /= dist_to_proj

        # If projection is closer than survey radius, use it
        if dist_to_proj <= self.map_data.survey_radius:
            return projection

        # Otherwise move point to radius boundary
        new_x = obj_point.x + to_proj_x * self.map_data.survey_radius
        new_y = obj_point.y + to_proj_y * self.map_data.survey_radius

        return Point(new_x, new_y)

