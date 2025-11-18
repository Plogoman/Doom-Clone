"""Base weapon class with upgrade system."""
import numpy as np


class WeaponUpgrade:
    """Weapon upgrade definition."""

    def __init__(self, name, description, damage_mult=1.0, fire_rate_mult=1.0, 
                 spread_reduction=0.0, special_effect=None):
        """Initialize weapon upgrade.

        Args:
            name: Upgrade name
            description: Upgrade description
            damage_mult: Damage multiplier (e.g., 1.2 = +20% damage)
            fire_rate_mult: Fire rate multiplier (e.g., 1.3 = +30% fire rate)
            spread_reduction: Spread reduction in radians
            special_effect: Special effect name (e.g., 'explosive', 'piercing')
        """
        self.name = name
        self.description = description
        self.damage_mult = damage_mult
        self.fire_rate_mult = fire_rate_mult
        self.spread_reduction = spread_reduction
        self.special_effect = special_effect


class Weapon:
    """Base weapon class with upgrade system."""

    def __init__(self, name, damage, fire_rate, ammo_type=None, ammo_per_shot=1):
        """Initialize weapon.

        Args:
            name: Weapon name
            damage: Base damage per shot
            fire_rate: Base shots per second
            ammo_type: Ammo type required (None for infinite)
            ammo_per_shot: Ammo consumed per shot
        """
        self.name = name
        self.base_damage = damage
        self.base_fire_rate = fire_rate
        self.ammo_type = ammo_type
        self.ammo_per_shot = ammo_per_shot

        self.sprite_name = 'weapon_' + name.lower().replace(' ', '_')

        # Upgrade system
        self.upgrades = []  # List of applied upgrades
        self.upgrade_level = 0
        self.max_upgrade_level = 3

        # State
        self.cooldown = 0.0
        self.firing = False
        self.reload_time = 0.0

    @property
    def damage(self):
        """Get current damage with upgrades applied."""
        damage = self.base_damage
        for upgrade in self.upgrades:
            damage *= upgrade.damage_mult
        return damage

    @property
    def fire_rate(self):
        """Get current fire rate with upgrades applied."""
        rate = self.base_fire_rate
        for upgrade in self.upgrades:
            rate *= upgrade.fire_rate_mult
        return rate

    def add_upgrade(self, upgrade):
        """Add upgrade to weapon.

        Args:
            upgrade: WeaponUpgrade instance

        Returns:
            True if upgrade added successfully
        """
        if self.upgrade_level >= self.max_upgrade_level:
            print(f"⚠️  {self.name} is already at maximum upgrade level!")
            return False

        self.upgrades.append(upgrade)
        self.upgrade_level += 1
        print(f"✨ {self.name} upgraded to Level {self.upgrade_level}!")
        print(f"   {upgrade.name}: {upgrade.description}")
        return True

    def has_special_effect(self, effect_name):
        """Check if weapon has a special effect.

        Args:
            effect_name: Effect name to check

        Returns:
            True if weapon has the effect
        """
        return any(u.special_effect == effect_name for u in self.upgrades)

    def get_upgrade_info(self):
        """Get formatted upgrade information.

        Returns:
            String describing current upgrades
        """
        if not self.upgrades:
            return f"{self.name} (No upgrades)"

        info = f"{self.name} +{self.upgrade_level}\n"
        info += f"  Damage: {self.base_damage} → {self.damage:.1f}\n"
        info += f"  Fire Rate: {self.base_fire_rate:.1f} → {self.fire_rate:.1f}\n"

        effects = [u.special_effect for u in self.upgrades if u.special_effect]
        if effects:
            info += f"  Effects: {', '.join(effects)}"

        return info

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
    """Hitscan weapon (instant hit) with upgrade support."""

    def __init__(self, name, damage, fire_rate, spread=0.0, **kwargs):
        """Initialize hitscan weapon.

        Args:
            name: Weapon name
            damage: Damage per shot
            fire_rate: Fire rate
            spread: Base bullet spread angle in radians
            **kwargs: Additional weapon parameters
        """
        super().__init__(name, damage, fire_rate, **kwargs)
        self.base_spread = spread

    @property
    def spread(self):
        """Get current spread with upgrades applied."""
        spread = self.base_spread
        for upgrade in self.upgrades:
            spread -= upgrade.spread_reduction
        return max(0.0, spread)  # Spread can't be negative

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
            direction[0] += spread_x
            direction[1] += spread_y
            direction = direction / np.linalg.norm(direction)

        print(f"💥 {self.name} fired!")
        if self.upgrade_level > 0:
            print(f"   Level {self.upgrade_level} | Damage: {self.damage:.1f}")

        # Store firing info for game to process
        if not hasattr(player, '_weapon_fire_data'):
            player._weapon_fire_data = []

        fire_data = {
            'origin': player.camera.position.copy(),
            'direction': direction,
            'damage': self.damage,
            'weapon': self.name,
            'has_explosive': self.has_special_effect('explosive'),
            'has_piercing': self.has_special_effect('piercing')
        }

        player._weapon_fire_data.append(fire_data)


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
        print(f"{self.name} fired projectile!")
        if self.upgrade_level > 0:
            print(f"   Level {self.upgrade_level} | Damage: {self.damage:.1f}")


# Predefined upgrade tiers
UPGRADE_TIER_1 = WeaponUpgrade(
    name="Tier 1: Enhanced Barrel",
    description="+20% damage",
    damage_mult=1.2
)

UPGRADE_TIER_2 = WeaponUpgrade(
    name="Tier 2: Rapid Fire Mechanism",
    description="+30% fire rate, +10% damage",
    damage_mult=1.1,
    fire_rate_mult=1.3
)

UPGRADE_TIER_3 = WeaponUpgrade(
    name="Tier 3: Explosive Rounds",
    description="+15% damage, explosive effect",
    damage_mult=1.15,
    special_effect='explosive'
)

UPGRADE_ACCURACY = WeaponUpgrade(
    name="Precision Barrel",
    description="Greatly reduced spread",
    spread_reduction=0.05
)

UPGRADE_PIERCING = WeaponUpgrade(
    name="Armor-Piercing Rounds",
    description="Bullets pierce through enemies",
    damage_mult=1.1,
    special_effect='piercing'
)
