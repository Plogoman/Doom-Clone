"""Base entity class."""
import numpy as np
from physics.aabb import AABB


class Entity:
    """Base class for all game entities."""

    def __init__(self, position=None):
        """Initialize entity.

        Args:
            position: Initial position [x, y, z]
        """
        self.position = np.array(position if position is not None else [0.0, 0.0, 0.0], dtype=np.float32)
        self.rotation = 0.0  # Yaw angle in radians

        # Rendering
        self.sprite_name = None
        self.sprite_size = np.array([1.0, 1.0], dtype=np.float32)

        # Collision
        self.aabb = AABB.from_center_size([0, 0, 0], [0.5, 1.0, 0.5])
        self.solid = True

        # State
        self.active = True
        self._dead = False

    def update(self, dt):
        """Update entity.

        Args:
            dt: Delta time in seconds
        """
        pass

    def is_dead(self):
        """Check if entity is dead.

        Returns:
            True if dead
        """
        return self._dead

    def destroy(self):
        """Mark entity for removal."""
        self._dead = True
        self.active = False

    def get_forward(self):
        """Get forward direction vector.

        Returns:
            Forward vector [x, y, z]
        """
        return np.array([
            np.cos(self.rotation),
            0.0,
            np.sin(self.rotation)
        ], dtype=np.float32)

    def get_right(self):
        """Get right direction vector.

        Returns:
            Right vector [x, y, z]
        """
        return np.array([
            np.cos(self.rotation + np.pi / 2),
            0.0,
            np.sin(self.rotation + np.pi / 2)
        ], dtype=np.float32)

    def distance_to(self, other):
        """Get distance to another entity.

        Args:
            other: Another entity

        Returns:
            Distance
        """
        if hasattr(other, 'position'):
            return np.linalg.norm(self.position - other.position)
        return float('inf')

    def __repr__(self):
        """String representation."""
        return f"{self.__class__.__name__}(pos={self.position})"
