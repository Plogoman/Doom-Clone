"""Pickup items."""
import numpy as np
from entities.entity import Entity
from physics.aabb import AABB


class Item(Entity):
    """Base pickup item."""

    def __init__(self, position):
        """Initialize item.

        Args:
            position: Item position
        """
        super().__init__(position)

        self.solid = False  # Players can walk through
        self.pickup_range = 1.0
        self.aabb = AABB.from_center_size([0, 0.3, 0], [0.5, 0.6, 0.5])

    def on_pickup(self, player):
        """Called when player picks up item.

        Args:
            player: Player entity

        Returns:
            True if item was picked up
        """
        return True

    def update(self, dt):
        """Update item.

        Args:
            dt: Delta time
        """
        # TODO: Bobbing animation
        pass


class HealthPack(Item):
    """Health pickup."""

    def __init__(self, position, amount=25):
        """Initialize health pack.

        Args:
            position: Item position
            amount: Health restored
        """
        super().__init__(position)
        self.amount = amount
        self.sprite_name = "item_health"
        self.sprite_size = np.array([0.5, 0.5], dtype=np.float32)

    def on_pickup(self, player):
        """Heal player.

        Args:
            player: Player entity

        Returns:
            True if picked up
        """
        if player.health < player.max_health:
            player.heal(self.amount)
            self.destroy()
            return True
        return False


class ArmorBonus(Item):
    """Armor pickup."""

    def __init__(self, position, amount=50):
        """Initialize armor.

        Args:
            position: Item position
            amount: Armor provided
        """
        super().__init__(position)
        self.amount = amount
        self.sprite_name = "item_armor"
        self.sprite_size = np.array([0.5, 0.5], dtype=np.float32)

    def on_pickup(self, player):
        """Give armor to player.

        Args:
            player: Player entity

        Returns:
            True if picked up
        """
        if player.armor < player.max_armor:
            player.add_armor(self.amount)
            self.destroy()
            return True
        return False


class AmmoBox(Item):
    """Ammo pickup."""

    def __init__(self, position, ammo_type, amount):
        """Initialize ammo box.

        Args:
            position: Item position
            ammo_type: Type of ammo
            amount: Amount of ammo
        """
        super().__init__(position)
        self.ammo_type = ammo_type
        self.amount = amount
        self.sprite_name = f"item_ammo_{ammo_type}"
        self.sprite_size = np.array([0.4, 0.4], dtype=np.float32)

    def on_pickup(self, player):
        """Give ammo to player.

        Args:
            player: Player entity

        Returns:
            True if picked up
        """
        player.add_ammo(self.ammo_type, self.amount)
        self.destroy()
        return True
