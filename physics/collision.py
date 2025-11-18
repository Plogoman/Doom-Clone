"""Collision detection and response."""
import numpy as np
from physics.aabb import AABB


class CollisionSystem:
    """Handles collision detection and response."""

    @staticmethod
    def check_aabb_wall_collision(aabb, wall):
        """Check collision between AABB and wall.

        Args:
            aabb: AABB object
            wall: Wall object

        Returns:
            (collides, penetration, normal) tuple
        """
        # Simple 2D collision in XZ plane
        center = aabb.get_center()
        size = aabb.get_size()
        radius = max(size[0], size[2]) * 0.5

        # Check distance from center to wall line segment
        x1, z1 = wall.start[0], wall.start[2]
        x2, z2 = wall.end[0], wall.end[2]
        cx, cz = center[0], center[2]

        # Vector from wall start to end
        dx = x2 - x1
        dz = z2 - z1
        length_sq = dx * dx + dz * dz

        if length_sq < 1e-6:
            return False, 0.0, np.array([0.0, 0.0, 0.0])

        # Project point onto line segment
        t = max(0, min(1, ((cx - x1) * dx + (cz - z1) * dz) / length_sq))
        proj_x = x1 + t * dx
        proj_z = z1 + t * dz

        # Distance from center to closest point on line
        dist_x = cx - proj_x
        dist_z = cz - proj_z
        distance = np.sqrt(dist_x * dist_x + dist_z * dist_z)

        if distance < radius:
            # Collision detected
            penetration = radius - distance
            if distance > 1e-6:
                normal = np.array([dist_x / distance, 0.0, dist_z / distance], dtype=np.float32)
            else:
                normal = wall.normal
            return True, penetration, normal

        return False, 0.0, np.array([0.0, 0.0, 0.0])

    @staticmethod
    def resolve_aabb_wall_collision(position, aabb, wall):
        """Resolve collision between AABB and wall.

        Args:
            position: Current position [x, y, z]
            aabb: AABB object at position
            wall: Wall object

        Returns:
            New position after resolution
        """
        aabb_at_pos = aabb.translate(position)
        collides, penetration, normal = CollisionSystem.check_aabb_wall_collision(aabb_at_pos, wall)

        if collides:
            # Push out along normal
            position = position + normal * (penetration + 0.001)  # Small epsilon

        return position

    @staticmethod
    def check_aabb_collision(aabb1, aabb2):
        """Check collision between two AABBs.

        Args:
            aabb1: First AABB
            aabb2: Second AABB

        Returns:
            True if colliding
        """
        return aabb1.intersects(aabb2)

    @staticmethod
    def check_entity_collisions(entity1, entity2):
        """Check collision between two entities.

        Args:
            entity1: First entity (must have aabb attribute)
            entity2: Second entity (must have aabb attribute)

        Returns:
            True if colliding
        """
        if not hasattr(entity1, 'aabb') or not hasattr(entity2, 'aabb'):
            return False

        aabb1 = entity1.aabb.translate(entity1.position)
        aabb2 = entity2.aabb.translate(entity2.position)

        return aabb1.intersects(aabb2)

    @staticmethod
    def slide_collision(position, velocity, aabb, walls, dt):
        """Sliding collision response.

        Args:
            position: Current position
            velocity: Velocity vector
            aabb: Entity AABB
            walls: List of walls
            dt: Delta time

        Returns:
            (new_position, new_velocity) tuple
        """
        new_position = position + velocity * dt

        # Check collision with each wall
        for wall in walls:
            aabb_at_new_pos = aabb.translate(new_position)
            collides, penetration, normal = CollisionSystem.check_aabb_wall_collision(
                aabb_at_new_pos, wall
            )

            if collides:
                # Slide along wall
                new_position = new_position + normal * (penetration + 0.001)

                # Remove velocity component along normal
                vel_along_normal = np.dot(velocity, normal)
                if vel_along_normal < 0:
                    velocity = velocity - normal * vel_along_normal

        return new_position, velocity
