import numpy as np

class Point:
    """Represents a point in 2D space"""
    def __init__(self, x: float, y: float, name: str = ""):
        self.x = x
        self.y = y
        self.name = name
        self.error = 1  # calculation error

    def distance_to(self, other: 'Point') -> float:
        """Calculate Euclidean distance to another point"""
        return np.sqrt((self.x - other.x) ** 2 + (self.y - other.y) ** 2) - self.error

    def distance_point_to_segment(self, a: 'Point', b: 'Point') -> float:
        # Вектор AB і AP
        dx = b.x - a.x
        dy = b.y - a.y
        if dx == dy == 0:  # Відрізок — це точка
            return self.distance_to(a)

        # Проекція точки P на лінію AB, обмежена на [0, 1]
        t = max(0, min(1, ((self.x - a.x) * dx + (self.y - a.y) * dy) / (dx * dx + dy * dy)))

        # Найближча точка на відрізку
        closest = Point(a.x + t * dx, a.y + t * dy)
        return self.distance_to(closest)

    def __repr__(self):
        return f"Point({self.x}, {self.y}, '{self.name}')"

    def __eq__(self, other):
        if isinstance(other, Point):
            return abs(self.x - other.x) < 0.01 and abs(self.y - other.y) < 0.01
        return False

    def __hash__(self):
        return hash((self.x, self.y))

    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {"x": self.x, "y": self.y, "name": self.name}

    @staticmethod
    def from_dict(data: dict):
        """Create Point from dictionary"""
        return Point(data["x"], data["y"], data.get("name", ""))
