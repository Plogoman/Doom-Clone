"""Base monster class."""
import numpy as np
from entities.entity import Entity
from physics.aabb import AABB
from physics.physics import PhysicsComponent


class Monster(Entity):
    """Base class for monsters/enemies."""

    def __init__(self, position=None):
        """Initialize monster.

        Args:
            position: Initial position [x, y, z]
        """
        super().__init__(position)

        # Stats
        self.health = 100
        self.max_health = 100
        self.damage = 10
        self.move_speed = 2.0

        # AI state
        self.ai_state = 'idle'  # idle, chase, death (simplified state machine)
        self.target = None
        self.attack_cooldown = 0.0
        self.attack_rate = 1.0  # Attacks per second
        self.attack_range = 1.5
        self.sight_range = 15.0

        # AI behavior flags
        self.is_ranged = False  # Override in subclass for ranged monsters
        self.preferred_range = 1.5  # Preferred distance from target
        self.min_range = 0.5  # Minimum distance (personal space)

        # Physics
        self.physics = PhysicsComponent()

        # Rendering
        self.sprite_size = np.array([1.0, 1.0], dtype=np.float32)

    def update(self, dt):
        """Update monster.

        Args:
            dt: Delta time
        """
        if self.attack_cooldown > 0:
            self.attack_cooldown -= dt

        # Update based on AI state (simplified: idle, chase, death)
        if self.ai_state == 'idle':
            self._update_idle(dt)
        elif self.ai_state == 'chase':
            self._update_chase(dt)
        elif self.ai_state == 'death':
            self._update_death(dt)

        # Update physics
        self.physics.update(dt)

    def _update_idle(self, dt):
        """Update idle state.

        Args:
            dt: Delta time
        """
        # Check for player in sight range
        if self.target and self.distance_to(self.target) < self.sight_range:
            self.ai_state = 'chase'

    def _update_chase(self, dt):
        """Update chase state with smart range management.

        Args:
            dt: Delta time
        """
        if not self.target:
            self.ai_state = 'idle'
            return

        distance = self.distance_to(self.target)

        if distance > self.sight_range * 1.5:
            # Lost target
            self.ai_state = 'idle'
            self.target = None
            return

        # Calculate direction to target
        direction = self.target.position - self.position
        direction[1] = 0  # Stay on XZ plane
        direction_length = np.linalg.norm(direction)

        if direction_length > 0:
            direction = direction / direction_length

        # RANGED MONSTER BEHAVIOR (Imp)
        if self.is_ranged:
            if distance < self.min_range:
                # Too close! Back away while maintaining line of sight
                self.physics.velocity[0] = -direction[0] * self.move_speed * 0.8
                self.physics.velocity[2] = -direction[2] * self.move_speed * 0.8
                # Still attack while backing up
                if self.attack_cooldown <= 0:
                    self.perform_attack()
                    self.attack_cooldown = 1.0 / self.attack_rate
            elif distance <= self.attack_range:
                # In optimal range - STRAFE and attack (keep moving!)
                # Calculate perpendicular direction for strafing
                strafe_dir = np.array([-direction[2], 0, direction[0]], dtype=np.float32)

                # Alternate strafe direction based on position
                import time
                strafe_sign = 1.0 if (time.time() % 4.0) < 2.0 else -1.0

                # Strafe sideways while maintaining distance
                self.physics.velocity[0] = strafe_dir[0] * self.move_speed * 0.6 * strafe_sign
                self.physics.velocity[2] = strafe_dir[2] * self.move_speed * 0.6 * strafe_sign

                # If too close, also back away slightly
                if distance < self.preferred_range:
                    self.physics.velocity[0] -= direction[0] * self.move_speed * 0.3
                    self.physics.velocity[2] -= direction[2] * self.move_speed * 0.3

                # Attack from this range
                if self.attack_cooldown <= 0:
                    self.perform_attack()
                    self.attack_cooldown = 1.0 / self.attack_rate
            else:
                # Too far, move closer
                self.physics.velocity[0] = direction[0] * self.move_speed
                self.physics.velocity[2] = direction[2] * self.move_speed

        # MELEE MONSTER BEHAVIOR (Demon)
        else:
            if distance <= self.attack_range:
                # In attack range - stop and attack
                self.physics.velocity[0] = 0
                self.physics.velocity[2] = 0

                # Attack!
                if self.attack_cooldown <= 0:
                    self.perform_attack()
                    self.attack_cooldown = 1.0 / self.attack_rate
            else:
                # Chase target with moderate speed
                speed_multiplier = 1.0

                # Slow down when getting close (give player space)
                if distance < 3.0:
                    speed_multiplier = 0.8
                # Speed up when far
                elif distance > 5.0:
                    speed_multiplier = 1.2

                self.physics.velocity[0] = direction[0] * self.move_speed * speed_multiplier
                self.physics.velocity[2] = direction[2] * self.move_speed * speed_multiplier

        # Always face target
        if direction_length > 0:
            self.rotation = np.arctan2(direction[2], direction[0])

    def _update_death(self, dt):
        """Update death state.

        Args:
            dt: Delta time
        """
        # TODO: Implement death animation
        pass

    def perform_attack(self):
        """Perform attack on target."""
        if self.target and hasattr(self.target, 'take_damage'):
            print(f"{self.__class__.__name__} attacks for {self.damage} damage!")
            self.target.take_damage(self.damage)

    def take_damage(self, amount, attacker=None):
        """Take damage.

        Args:
            amount: Damage amount
            attacker: Entity that dealt damage
        """
        self.health -= amount

        if self.health <= 0:
            self.health = 0
            self.die()
        else:
            # Set attacker as target and start chasing
            if attacker and not self.target:
                self.target = attacker
                if self.ai_state == 'idle':
                    self.ai_state = 'chase'

    def die(self):
        """Monster death."""
        print(f"{self.__class__.__name__} died!")
        self.ai_state = 'death'
        self.destroy()

    def set_target(self, target):
        """Set attack target.

        Args:
            target: Target entity (usually player)
        """
        self.target = target
        if self.ai_state == 'idle':
            self.ai_state = 'chase'
