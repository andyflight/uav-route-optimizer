from typing import List
from core.point import Point

class Map:
    """Represents the task with all parameters"""

    def __init__(self, start: Point, end: Point, max_distance: float, survey_radius: float):
        self.start_point = start
        self.end_point = end
        self.objects = []
        self.max_distance = max_distance
        self.survey_radius = survey_radius

    def add_object(self, point: Point):
        """Add an object for surveillance"""
        self.objects.append(point)

    def get_objects(self) -> List[Point]:
        """Get list of objects"""
        return self.objects

    def validate(self) -> bool:
        """Validate map data"""
        # Check if start and end points are different
        if self.start_point == self.end_point:
            return False

        # Check if max_distance is positive
        if self.max_distance <= 0:
            return False

        # Check if survey_radius is non-negative
        if self.survey_radius < 0:
            return False

        # Check if direct distance from start to end is within max_distance
        direct_distance = self.start_point.distance_to(self.end_point)
        if direct_distance > self.max_distance:
            return False

        return True

    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            "start_point": self.start_point.to_dict(),
            "end_point": self.end_point.to_dict(),
            "objects": [obj.to_dict() for obj in self.objects],
            "max_distance": self.max_distance,
            "survey_radius": self.survey_radius
        }

    @staticmethod
    def from_dict(data: dict):
        """Create Map from dictionary"""
        map_obj = Map(
            Point.from_dict(data["start_point"]),
            Point.from_dict(data["end_point"]),
            data["max_distance"],
            data["survey_radius"]
        )
        for obj_data in data["objects"]:
            map_obj.add_object(Point.from_dict(obj_data))
        return map_obj