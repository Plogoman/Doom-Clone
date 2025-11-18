"""Pistol weapon."""
from entities.weapon import HitscanWeapon


class Pistol(HitscanWeapon):
    """Basic pistol."""

    def __init__(self):
        """Initialize pistol."""
        super().__init__(
            name="Pistol",
            damage=10,
            fire_rate=3.0,
            spread=0.05,
            ammo_type="bullets",
            ammo_per_shot=1
        )
        self.sprite_name = "weapon_pistol"
