"""Raycasting for hitscan weapons and line-of-sight."""
import numpy as np


class RaycastHit:
    """Raycast hit information."""

    def __init__(self, hit=False, distance=float('inf'), point=None, normal=None, entity=None):
        """Initialize raycast hit.

        Args:
            hit: Whether ray hit something
            distance: Distance to hit point
            point: Hit point [x, y, z]
            normal: Surface normal at hit point
            entity: Entity that was hit (if any)
        """
        self.hit = hit
        self.distance = distance
        self.point = point
        self.normal = normal
        self.entity = entity


class Raycast:
    """Raycasting utilities."""

    @staticmethod
    def cast_ray(origin, direction, max_distance, level, entities=None):
        """Cast ray through level.

        Args:
            origin: Ray origin [x, y, z]
            direction: Ray direction [x, y, z] (normalized)
            max_distance: Maximum ray distance
            level: Level to cast ray through
            entities: List of entities to check (optional)

        Returns:
            RaycastHit object
        """
        origin = np.array(origin, dtype=np.float32)
        direction = np.array(direction, dtype=np.float32)
        direction = direction / np.linalg.norm(direction)

        closest_hit = RaycastHit()

        # Check walls
        for wall in level.walls:
            hit, distance, point = wall.intersects_ray(origin, direction)
            if hit and distance < closest_hit.distance and distance <= max_distance:
                closest_hit.hit = True
                closest_hit.distance = distance
                closest_hit.point = point
                closest_hit.normal = wall.normal
                closest_hit.entity = None

        # Check entities
        if entities:
            for entity in entities:
                if hasattr(entity, 'aabb'):
                    hit, t_near, t_far = entity.aabb.intersect_ray(origin, direction)
                    if hit and t_near < closest_hit.distance and t_near <= max_distance:
                        closest_hit.hit = True
                        closest_hit.distance = t_near
                        closest_hit.point = origin + direction * t_near
                        # Simple normal approximation
                        closest_hit.normal = (closest_hit.point - entity.position)
                        if np.linalg.norm(closest_hit.normal) > 0:
                            closest_hit.normal /= np.linalg.norm(closest_hit.normal)
                        closest_hit.entity = entity

        return closest_hit

    @staticmethod
    def line_of_sight(start, end, level, entities=None):
        """Check if there's clear line of sight between two points.

        Args:
            start: Start point [x, y, z]
            end: End point [x, y, z]
            level: Level to check
            entities: Entities to check against (optional)

        Returns:
            True if clear line of sight
        """
        direction = end - start
        distance = np.linalg.norm(direction)
        direction = direction / distance

        hit = Raycast.cast_ray(start, direction, distance, level, entities)

        # If hit distance is less than desired distance, line of sight is blocked
        return not hit.hit or hit.distance >= distance
