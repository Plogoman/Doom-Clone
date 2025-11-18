"""Base weapon class."""
import numpy as np


class Weapon:
    """Base weapon class."""

    def __init__(self, name, damage, fire_rate, ammo_type=None, ammo_per_shot=1):
        """Initialize weapon.

        Args:
            name: Weapon name
            damage: Damage per shot
            fire_rate: Shots per second
            ammo_type: Ammo type required (None for infinite)
            ammo_per_shot: Ammo consumed per shot
        """
        self.name = name
        self.damage = damage
        self.fire_rate = fire_rate
        self.ammo_type = ammo_type
        self.ammo_per_shot = ammo_per_shot

        self.sprite_name = 'weapon_' + name.lower().replace(' ', '_')

        # State
        self.cooldown = 0.0
        self.firing = False
        self.reload_time = 0.0

    def update(self, dt):
        """Update weapon.

        Args:
            dt: Delta time
        """
        if self.cooldown > 0:
            self.cooldown -= dt

        if self.reload_time > 0:
            self.reload_time -= dt

    def can_fire(self, player):
        """Check if weapon can fire.

        Args:
            player: Player entity

        Returns:
            True if can fire
        """
        if self.cooldown > 0 or self.reload_time > 0:
            return False

        if self.ammo_type and player.ammo.get(self.ammo_type, 0) < self.ammo_per_shot:
            return False

        return True

    def fire(self, player):
        """Fire weapon.

        Args:
            player: Player entity
        """
        if not self.can_fire(player):
            return

        # Consume ammo
        if self.ammo_type:
            player.ammo[self.ammo_type] -= self.ammo_per_shot

        # Set cooldown
        self.cooldown = 1.0 / self.fire_rate

        # Perform weapon-specific attack
        self._do_fire(player)

    def _do_fire(self, player):
        """Weapon-specific fire logic (override in subclasses).

        Args:
            player: Player entity
        """
        pass


class HitscanWeapon(Weapon):
    """Hitscan weapon (instant hit)."""

    def __init__(self, name, damage, fire_rate, spread=0.0, **kwargs):
        """Initialize hitscan weapon.

        Args:
            name: Weapon name
            damage: Damage per shot
            fire_rate: Fire rate
            spread: Bullet spread angle in radians
            **kwargs: Additional weapon parameters
        """
        super().__init__(name, damage, fire_rate, **kwargs)
        self.spread = spread

    def _do_fire(self, player):
        """Fire hitscan weapon.

        Args:
            player: Player entity
        """
        # Get camera direction with spread
        direction = player.camera.forward.copy()

        if self.spread > 0:
            # Add random spread
            spread_x = np.random.uniform(-self.spread, self.spread)
            spread_y = np.random.uniform(-self.spread, self.spread)

            # Rotate direction by spread
            # (simplified - just perturb the direction)
            direction[0] += spread_x
            direction[1] += spread_y
            direction = direction / np.linalg.norm(direction)

        print(f"💥 {self.name} fired!")

        # Store firing info for game to process
        # Game will need to handle actual raycasting with level/entities
        if not hasattr(player, '_weapon_fire_data'):
            player._weapon_fire_data = []

        player._weapon_fire_data.append({
            'origin': player.camera.position.copy(),
            'direction': direction,
            'damage': self.damage,
            'weapon': self.name
        })


class ProjectileWeapon(Weapon):
    """Projectile weapon (spawns projectile)."""

    def __init__(self, name, damage, fire_rate, projectile_speed, **kwargs):
        """Initialize projectile weapon.

        Args:
            name: Weapon name
            damage: Damage per projectile
            fire_rate: Fire rate
            projectile_speed: Projectile velocity
            **kwargs: Additional parameters
        """
        super().__init__(name, damage, fire_rate, **kwargs)
        self.projectile_speed = projectile_speed

    def _do_fire(self, player):
        """Fire projectile weapon.

        Args:
            player: Player entity
        """
        # Spawn projectile (would need game context)
        print(f"{self.name} fired projectile!")
