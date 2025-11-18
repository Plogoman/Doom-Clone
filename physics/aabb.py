"""Axis-Aligned Bounding Box for collision detection."""
import numpy as np


class AABB:
    """Axis-Aligned Bounding Box."""

    def __init__(self, min_point, max_point):
        """Initialize AABB.

        Args:
            min_point: Minimum corner [x, y, z]
            max_point: Maximum corner [x, y, z]
        """
        self.min = np.array(min_point, dtype=np.float32)
        self.max = np.array(max_point, dtype=np.float32)

    @classmethod
    def from_center_size(cls, center, size):
        """Create AABB from center and size.

        Args:
            center: Center point [x, y, z]
            size: Size [width, height, depth]

        Returns:
            AABB object
        """
        half_size = np.array(size, dtype=np.float32) * 0.5
        center = np.array(center, dtype=np.float32)
        return cls(center - half_size, center + half_size)

    def intersects(self, other):
        """Check if this AABB intersects another AABB.

        Args:
            other: Another AABB

        Returns:
            True if AABBs intersect
        """
        return (self.min[0] <= other.max[0] and self.max[0] >= other.min[0] and
                self.min[1] <= other.max[1] and self.max[1] >= other.min[1] and
                self.min[2] <= other.max[2] and self.max[2] >= other.min[2])

    def contains_point(self, point):
        """Check if point is inside AABB.

        Args:
            point: Point [x, y, z]

        Returns:
            True if point is inside
        """
        point = np.array(point, dtype=np.float32)
        return (self.min[0] <= point[0] <= self.max[0] and
                self.min[1] <= point[1] <= self.max[1] and
                self.min[2] <= point[2] <= self.max[2])

    def get_center(self):
        """Get center point.

        Returns:
            Center [x, y, z]
        """
        return (self.min + self.max) * 0.5

    def get_size(self):
        """Get size.

        Returns:
            Size [width, height, depth]
        """
        return self.max - self.min

    def translate(self, offset):
        """Translate AABB by offset.

        Args:
            offset: Translation vector [x, y, z]

        Returns:
            New translated AABB
        """
        offset = np.array(offset, dtype=np.float32)
        return AABB(self.min + offset, self.max + offset)

    def expand(self, amount):
        """Expand AABB by amount.

        Args:
            amount: Amount to expand

        Returns:
            New expanded AABB
        """
        expand_vec = np.array([amount, amount, amount], dtype=np.float32)
        return AABB(self.min - expand_vec, self.max + expand_vec)

    def intersect_ray(self, origin, direction):
        """Ray-AABB intersection test.

        Args:
            origin: Ray origin [x, y, z]
            direction: Ray direction [x, y, z] (should be normalized)

        Returns:
            (hit, t_near, t_far) tuple
        """
        origin = np.array(origin, dtype=np.float32)
        direction = np.array(direction, dtype=np.float32)

        # Avoid division by zero
        direction = np.where(np.abs(direction) < 1e-8, 1e-8, direction)

        t1 = (self.min - origin) / direction
        t2 = (self.max - origin) / direction

        t_near = np.max(np.minimum(t1, t2))
        t_far = np.min(np.maximum(t1, t2))

        if t_near > t_far or t_far < 0:
            return False, 0.0, 0.0

        return True, t_near, t_far

    def __repr__(self):
        """String representation."""
        return f"AABB(min={self.min}, max={self.max})"
