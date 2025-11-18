"""Doom-style sector representation."""
import numpy as np


class Sector:
    """Represents a sector (room/area) with floor and ceiling."""

    def __init__(self, sector_id, floor_height=0.0, ceiling_height=2.5):
        """Initialize sector.

        Args:
            sector_id: Unique sector identifier
            floor_height: Floor height
            ceiling_height: Ceiling height
        """
        self.id = sector_id
        self.floor_height = floor_height
        self.ceiling_height = ceiling_height

        self.floor_texture = 'default_floor'
        self.ceiling_texture = 'default_ceiling'

        self.light_level = 1.0  # 0.0 to 1.0

        # Walls belonging to this sector
        self.walls = []

        # Floor/ceiling vertex data (filled by level builder)
        self.floor_vertices = []
        self.ceiling_vertices = []

    def add_wall(self, wall):
        """Add wall to this sector.

        Args:
            wall: Wall object
        """
        self.walls.append(wall)

    def get_height(self):
        """Get sector height (ceiling - floor).

        Returns:
            Height of sector
        """
        return self.ceiling_height - self.floor_height

    def contains_point(self, x, z):
        """Check if 2D point is inside sector.

        Args:
            x: X coordinate
            z: Z coordinate

        Returns:
            True if point is inside sector
        """
        # Use ray casting algorithm
        # Cast ray from point to the right, count intersections
        intersections = 0

        for wall in self.walls:
            x1, z1 = wall.start[0], wall.start[2]
            x2, z2 = wall.end[0], wall.end[2]

            # Check if ray intersects wall segment
            if ((z1 > z) != (z2 > z)) and (x < (x2 - x1) * (z - z1) / (z2 - z1) + x1):
                intersections += 1

        return intersections % 2 == 1

    def __repr__(self):
        """String representation."""
        return f"Sector(id={self.id}, floor={self.floor_height}, ceiling={self.ceiling_height})"
