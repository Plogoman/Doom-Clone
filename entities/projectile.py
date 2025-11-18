"""Projectile entities."""
import numpy as np
from entities.entity import Entity
from physics.aabb import AABB


class Projectile(Entity):
    """Base projectile class."""

    def __init__(self, position, direction, speed, damage, owner=None):
        """Initialize projectile.

        Args:
            position: Starting position
            direction: Direction vector
            speed: Movement speed
            damage: Damage on hit
            owner: Entity that fired projectile
        """
        super().__init__(position)

        self.direction = np.array(direction, dtype=np.float32)
        if np.linalg.norm(self.direction) > 0:
            self.direction = self.direction / np.linalg.norm(self.direction)

        self.speed = speed
        self.damage = damage
        self.owner = owner
        self.lifetime = 5.0  # Seconds before despawn

        # Collision
        self.aabb = AABB.from_center_size([0, 0, 0], [0.2, 0.2, 0.2])

    def update(self, dt):
        """Update projectile.

        Args:
            dt: Delta time
        """
        # Move projectile
        self.position += self.direction * self.speed * dt

        # Decrease lifetime
        self.lifetime -= dt
        if self.lifetime <= 0:
            self.destroy()

    def on_hit(self, entity):
        """Called when projectile hits entity.

        Args:
            entity: Entity that was hit
        """
        if entity != self.owner and hasattr(entity, 'take_damage'):
            entity.take_damage(self.damage, self.owner)
        self.destroy()


class Fireball(Projectile):
    """Imp fireball projectile."""

    def __init__(self, position, direction, owner=None):
        """Initialize fireball.

        Args:
            position: Starting position
            direction: Direction vector
            owner: Entity that fired
        """
        super().__init__(position, direction, speed=10.0, damage=3, owner=owner)

        self.sprite_name = "projectile_fireball"
        self.sprite_size = np.array([0.8, 0.8], dtype=np.float32)  # Larger for visibility


class Rocket(Projectile):
    """Rocket projectile."""

    def __init__(self, position, direction, owner=None):
        """Initialize rocket.

        Args:
            position: Starting position
            direction: Direction vector
            owner: Entity that fired
        """
        super().__init__(position, direction, speed=20.0, damage=100, owner=owner)

        self.sprite_name = "projectile_rocket"
        self.sprite_size = np.array([0.6, 0.3], dtype=np.float32)
        self.explosion_radius = 3.0

    def on_hit(self, entity):
        """Rocket explodes on impact.

        Args:
            entity: Entity that was hit
        """
        print("Rocket explodes!")
        # TODO: Apply splash damage to nearby entities
        super().on_hit(entity)
