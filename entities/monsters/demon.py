"""Demon (Pinky) - fast melee enemy."""
from entities.monster import Monster
from physics.aabb import AABB
import numpy as np


class Demon(Monster):
    """Demon/Pinky - fast melee attacker."""

    def __init__(self, position=None):
        """Initialize Demon.

        Args:
            position: Initial position
        """
        super().__init__(position)

        # Stats
        self.health = 60
        self.max_health = 60
        self.damage = 15
        self.move_speed = 3.0  # Slower, more manageable

        # Combat - Melee behavior
        self.is_ranged = False
        self.attack_range = 2.0  # Melee range - not too close
        self.preferred_range = 1.5  # Same as attack range for melee
        self.min_range = 0.0  # No personal space, gets right in your face
        self.attack_rate = 1.5

        # Collision
        self.aabb = AABB.from_center_size([0, 0.7, 0], [0.8, 1.4, 0.8])

        # Rendering
        self.sprite_name = "monster_demon"
        self.sprite_size = np.array([1.8, 1.8], dtype=np.float32)  # Larger for better visibility
