"""Cacodemon - flying ranged enemy."""
from entities.monster import Monster
from physics.aabb import AABB
import numpy as np


class Cacodemon(Monster):
    """Cacodemon - floating ball of hate."""

    def __init__(self, position=None):
        """Initialize Cacodemon.

        Args:
            position: Initial position
        """
        super().__init__(position)

        # Stats
        self.health = 400
        self.max_health = 400
        self.damage = 15
        self.move_speed = 3.0

        # Combat
        self.attack_range = 12.0
        self.attack_rate = 1.0

        # Physics - cacodemons fly!
        self.physics.use_gravity = False

        # Collision
        self.aabb = AABB.from_center_size([0, 1.0, 0], [1.0, 1.0, 1.0])

        # Rendering
        self.sprite_name = "monster_cacodemon"
        self.sprite_size = np.array([1.5, 1.5], dtype=np.float32)

    def _update_chase(self, dt):
        """Override chase to allow 3D movement.

        Args:
            dt: Delta time
        """
        if not self.target:
            self.ai_state = 'idle'
            return

        distance = self.distance_to(self.target)

        if distance > self.sight_range * 1.5:
            self.ai_state = 'idle'
            self.target = None
            return

        if distance <= self.attack_range:
            self.ai_state = 'attack'
            self.physics.velocity.fill(0)
        else:
            # Move towards target in 3D
            direction = self.target.position - self.position
            if np.linalg.norm(direction) > 0:
                direction = direction / np.linalg.norm(direction)
                self.physics.velocity = direction * self.move_speed

                # Face target
                self.rotation = np.arctan2(direction[2], direction[0])
