"""Shotgun weapon."""
from entities.weapon import HitscanWeapon
import numpy as np


class Shotgun(HitscanWeapon):
    """Shotgun with multiple pellets."""

    def __init__(self):
        """Initialize shotgun."""
        super().__init__(
            name="Shotgun",
            damage=10,  # Per pellet
            fire_rate=1.5,
            spread=0.15,
            ammo_type="shells",
            ammo_per_shot=1
        )
        self.pellet_count = 7
        self.sprite_name = "weapon_shotgun"

    def _do_fire(self, player):
        """Fire shotgun with multiple pellets.

        Args:
            player: Player entity
        """
        print(f"{self.name} fired {self.pellet_count} pellets!")
        # In full implementation, would fire multiple raycasts
