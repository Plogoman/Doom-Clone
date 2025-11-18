"""Physics system for movement and gravity."""
import numpy as np
from core.config import GRAVITY


class PhysicsComponent:
    """Physics component for entities."""

    def __init__(self, mass=1.0, use_gravity=True):
        """Initialize physics component.

        Args:
            mass: Entity mass
            use_gravity: Whether to apply gravity
        """
        self.velocity = np.array([0.0, 0.0, 0.0], dtype=np.float32)
        self.acceleration = np.array([0.0, 0.0, 0.0], dtype=np.float32)
        self.mass = mass
        self.use_gravity = use_gravity
        self.on_ground = False

    def apply_force(self, force):
        """Apply force to entity.

        Args:
            force: Force vector [x, y, z]
        """
        self.acceleration += np.array(force, dtype=np.float32) / self.mass

    def apply_impulse(self, impulse):
        """Apply instantaneous impulse.

        Args:
            impulse: Impulse vector [x, y, z]
        """
        self.velocity += np.array(impulse, dtype=np.float32) / self.mass

    def update(self, dt):
        """Update physics.

        Args:
            dt: Delta time in seconds
        """
        # Apply gravity
        if self.use_gravity and not self.on_ground:
            self.acceleration[1] -= GRAVITY

        # Update velocity
        self.velocity += self.acceleration * dt

        # Reset acceleration
        self.acceleration.fill(0.0)

        # Apply damping on ground
        if self.on_ground:
            self.velocity[0] *= 0.9
            self.velocity[2] *= 0.9

    def get_displacement(self, dt):
        """Get displacement for this frame.

        Args:
            dt: Delta time

        Returns:
            Displacement vector
        """
        return self.velocity * dt


class PhysicsSystem:
    """Manages physics for all entities."""

    def __init__(self, level):
        """Initialize physics system.

        Args:
            level: Level for collision detection
        """
        self.level = level
        self.entities = []

    def add_entity(self, entity):
        """Add entity to physics system.

        Args:
            entity: Entity with physics component
        """
        if hasattr(entity, 'physics'):
            self.entities.append(entity)

    def remove_entity(self, entity):
        """Remove entity from physics system.

        Args:
            entity: Entity to remove
        """
        if entity in self.entities:
            self.entities.remove(entity)

    def update(self, dt):
        """Update all physics entities.

        Args:
            dt: Delta time
        """
        for entity in self.entities:
            if hasattr(entity, 'physics'):
                # Update physics
                entity.physics.update(dt)

                # Apply velocity to position (THIS WAS MISSING!)
                entity.position += entity.physics.get_displacement(dt)

                # Check ground collision
                self._check_ground_collision(entity)

    def _check_ground_collision(self, entity):
        """Check if entity is on ground.

        Args:
            entity: Entity to check
        """
        if not hasattr(entity, 'position'):
            return

        # Find sector entity is in
        sector = self.level.bsp_tree.find_sector_at(entity.position[0], entity.position[2])

        if sector:
            # Check if on floor
            if entity.position[1] <= sector.floor_height:
                entity.position[1] = sector.floor_height
                entity.physics.velocity[1] = 0
                entity.physics.on_ground = True
            else:
                entity.physics.on_ground = False

            # Check if hitting ceiling
            if hasattr(entity, 'aabb'):
                entity_top = entity.position[1] + entity.aabb.get_size()[1]
                if entity_top >= sector.ceiling_height:
                    entity.position[1] = sector.ceiling_height - entity.aabb.get_size()[1]
                    entity.physics.velocity[1] = 0
