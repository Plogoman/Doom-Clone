"""Wall segment representation."""
import numpy as np


class Wall:
    """Represents a wall segment between two points."""

    def __init__(self, start, end, sector, other_sector=None):
        """Initialize wall.

        Args:
            start: Start point [x, y, z]
            end: End point [x, y, z]
            sector: Sector this wall belongs to
            other_sector: Sector on other side (None for solid wall)
        """
        self.start = np.array(start, dtype=np.float32)
        self.end = np.array(end, dtype=np.float32)
        self.sector = sector
        self.other_sector = other_sector

        # Textures
        self.upper_texture = 'default_wall' if other_sector else None
        self.middle_texture = 'default_wall'
        self.lower_texture = 'default_wall' if other_sector else None

        # Portal flag
        self.is_portal = other_sector is not None

        # Precompute normal
        self._compute_normal()

    def _compute_normal(self):
        """Compute wall normal vector."""
        direction = self.end - self.start
        # Normal points to the right of direction (in XZ plane)
        self.normal = np.array([direction[2], 0, -direction[0]], dtype=np.float32)
        length = np.linalg.norm(self.normal)
        if length > 0:
            self.normal /= length

    def get_length(self):
        """Get wall length.

        Returns:
            Length of wall segment
        """
        return np.linalg.norm(self.end - self.start)

    def get_midpoint(self):
        """Get wall midpoint.

        Returns:
            Midpoint coordinates
        """
        return (self.start + self.end) * 0.5

    def intersects_ray(self, origin, direction):
        """Check if ray intersects this wall.

        Args:
            origin: Ray origin [x, y, z]
            direction: Ray direction [x, y, z]

        Returns:
            (hit, distance, point) tuple
        """
        # 2D line-line intersection in XZ plane
        x1, z1 = self.start[0], self.start[2]
        x2, z2 = self.end[0], self.end[2]
        x3, z3 = origin[0], origin[2]
        dx, dz = direction[0], direction[2]

        denom = (x1 - x2) * dz - (z1 - z2) * dx
        if abs(denom) < 1e-6:
            return False, float('inf'), None

        t = ((x1 - x3) * dz - (z1 - z3) * dx) / denom
        u = -((x1 - x2) * (z1 - z3) - (z1 - z2) * (x1 - x3)) / denom

        if 0 <= t <= 1 and u >= 0:
            hit_point = origin + direction * u
            return True, u, hit_point

        return False, float('inf'), None

    def __repr__(self):
        """String representation."""
        portal_str = " (portal)" if self.is_portal else ""
        return f"Wall({self.start} -> {self.end}){portal_str}"
