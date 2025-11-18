"""Chaingun weapon."""
from entities.weapon import HitscanWeapon


class Chaingun(HitscanWeapon):
    """Fast-firing chaingun."""

    def __init__(self):
        """Initialize chaingun."""
        super().__init__(
            name="Chaingun",
            damage=10,
            fire_rate=10.0,  # 10 shots per second
            spread=0.08,
            ammo_type="bullets",
            ammo_per_shot=1
        )
        self.sprite_name = "weapon_chaingun"
