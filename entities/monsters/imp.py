"""Imp monster - basic ranged enemy."""
from entities.monster import Monster
from entities.projectile import Fireball
from physics.aabb import AABB
import numpy as np


class Imp(Monster):
    """Imp - throws fireballs."""

    def __init__(self, position=None):
        """Initialize Imp.

        Args:
            position: Initial position
        """
        super().__init__(position)

        # Stats
        self.health = 60
        self.max_health = 60
        self.damage = 3
        self.move_speed = 2.5

        # Combat - Ranged behavior
        self.is_ranged = True
        self.attack_range = 7.0  # Can shoot from 7 units away
        self.preferred_range = 6.0  # Likes to stay at 6 units
        self.min_range = 4.0  # Backs away if player gets closer than 4 units
        self.attack_rate = 0.8

        # Collision
        self.aabb = AABB.from_center_size([0, 0.8, 0], [0.6, 1.6, 0.6])

        # Rendering
        self.sprite_name = "monster_imp"
        self.sprite_size = np.array([1.5, 2.0], dtype=np.float32)  # Larger for better visibility

        # Store reference to entity list for spawning projectiles
        self.entity_list = None

    def perform_attack(self):
        """Throw fireball at target."""
        if self.target:
            print("Imp throws fireball!")

            # Calculate direction to target
            direction = self.target.position - self.position
            direction[1] = 0  # Keep fireball horizontal
            if np.linalg.norm(direction) > 0:
                direction = direction / np.linalg.norm(direction)

            # Spawn fireball slightly in front of Imp
            spawn_pos = self.position + direction * 0.5
            spawn_pos[1] = self.position[1] + 1.0  # Chest height

            fireball = Fireball(spawn_pos, direction, owner=self)

            # Add to entity list if we have reference
            if self.entity_list is not None:
                self.entity_list.append(fireball)
