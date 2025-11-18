"""Player entity."""
import numpy as np
from entities.entity import Entity
from core.camera import Camera
from physics.aabb import AABB
from physics.physics import PhysicsComponent
from core.config import (
    PLAYER_SPEED, PLAYER_SPRINT_MULTIPLIER, PLAYER_RADIUS,
    PLAYER_HEIGHT, PLAYER_MAX_HEALTH, PLAYER_MAX_ARMOR,
    CAMERA_HEIGHT, JUMP_VELOCITY
)


class Player(Entity):
    """Player entity with camera and input handling."""

    def __init__(self, position=None):
        """Initialize player.

        Args:
            position: Initial position [x, y, z]
        """
        super().__init__(position)

        # Camera
        self.camera = Camera(self.position + np.array([0, CAMERA_HEIGHT, 0], dtype=np.float32))

        # Collision
        self.aabb = AABB.from_center_size([0, PLAYER_HEIGHT / 2, 0],
                                         [PLAYER_RADIUS * 2, PLAYER_HEIGHT, PLAYER_RADIUS * 2])

        # Stats
        self.health = PLAYER_MAX_HEALTH
        self.armor = 0
        self.max_health = PLAYER_MAX_HEALTH
        self.max_armor = PLAYER_MAX_ARMOR

        # Movement
        self.move_speed = PLAYER_SPEED
        self.sprint_multiplier = PLAYER_SPRINT_MULTIPLIER
        self.physics = PhysicsComponent()

        # Input state
        self.move_forward = 0.0
        self.move_right = 0.0
        self.sprinting = False

        # Weapons
        self.weapons = []
        self.current_weapon = None
        self.weapon_slots = [None] * 7  # Doom-style weapon slots

        # Inventory
        self.ammo = {
            'bullets': 50,
            'shells': 0,
            'rockets': 0,
            'cells': 0
        }
        self.keys = set()

        # Stats
        self.kills = 0

        # Damage flash effect
        self.damage_flash = 0.0  # Timer for red screen flash

    def update(self, dt):
        """Update player.

        Args:
            dt: Delta time
        """
        # Update damage flash timer
        if self.damage_flash > 0:
            self.damage_flash -= dt

        # Calculate movement velocity
        move_dir = np.array([self.move_forward, 0.0, self.move_right], dtype=np.float32)

        if np.linalg.norm(move_dir) > 0:
            move_dir = move_dir / np.linalg.norm(move_dir)

            # Transform to world space based on camera rotation
            forward = self.camera.forward
            right = self.camera.right

            # Flatten to XZ plane for movement
            forward[1] = 0
            right[1] = 0
            if np.linalg.norm(forward) > 0:
                forward = forward / np.linalg.norm(forward)
            if np.linalg.norm(right) > 0:
                right = right / np.linalg.norm(right)

            world_move = forward * move_dir[0] + right * move_dir[2]

            # Apply speed
            speed = self.move_speed
            if self.sprinting:
                speed *= self.sprint_multiplier

            self.physics.velocity[0] = world_move[0] * speed
            self.physics.velocity[2] = world_move[2] * speed
        else:
            # Stop horizontal movement when no input
            self.physics.velocity[0] = 0
            self.physics.velocity[2] = 0

        # Update physics
        self.physics.update(dt)

        # Update camera position
        self.camera.position = self.position + np.array([0, CAMERA_HEIGHT, 0], dtype=np.float32)

        # Update current weapon
        if self.current_weapon:
            self.current_weapon.update(dt)

    def move(self, forward, right):
        """Set movement input.

        Args:
            forward: Forward/backward (-1 to 1)
            right: Left/right (-1 to 1)
        """
        self.move_forward = forward
        self.move_right = right

    def rotate(self, delta_x, delta_y):
        """Rotate player camera.

        Args:
            delta_x: Mouse X delta
            delta_y: Mouse Y delta
        """
        self.camera.rotate(delta_x, delta_y)
        self.rotation = self.camera.yaw

    def jump(self):
        """Make player jump."""
        if self.physics.on_ground:
            self.physics.velocity[1] = JUMP_VELOCITY

    def take_damage(self, amount):
        """Take damage.

        Args:
            amount: Damage amount
        """
        # Trigger damage flash effect
        self.damage_flash = 0.3  # Flash for 0.3 seconds

        # Armor absorbs some damage
        if self.armor > 0:
            armor_absorb = min(amount * 0.5, self.armor)
            self.armor -= armor_absorb
            amount -= armor_absorb

        self.health -= amount
        print(f"  💢 Player took {amount:.1f} damage! Health: {self.health:.0f}")

        if self.health <= 0:
            self.health = 0
            self.die()

    def heal(self, amount):
        """Heal player.

        Args:
            amount: Heal amount
        """
        self.health = min(self.health + amount, self.max_health)

    def add_armor(self, amount):
        """Add armor.

        Args:
            amount: Armor amount
        """
        self.armor = min(self.armor + amount, self.max_armor)

    def add_ammo(self, ammo_type, amount):
        """Add ammo.

        Args:
            ammo_type: Ammo type ('bullets', 'shells', etc.)
            amount: Amount to add
        """
        if ammo_type in self.ammo:
            self.ammo[ammo_type] += amount

    def equip_weapon(self, weapon, slot):
        """Equip weapon in slot.

        Args:
            weapon: Weapon object
            slot: Weapon slot (1-7)
        """
        if 0 < slot <= 7:
            self.weapon_slots[slot - 1] = weapon
            if not self.current_weapon:
                self.switch_weapon(slot)

    def switch_weapon(self, slot):
        """Switch to weapon in slot.

        Args:
            slot: Weapon slot (1-7)
        """
        if 0 < slot <= 7 and self.weapon_slots[slot - 1]:
            self.current_weapon = self.weapon_slots[slot - 1]

    def fire_weapon(self):
        """Fire current weapon."""
        if self.current_weapon:
            self.current_weapon.fire(self)

    def die(self):
        """Player death."""
        print("Player died!")
        # TODO: Implement death screen

    def is_alive(self):
        """Check if player is alive.

        Returns:
            True if alive
        """
        return self.health > 0
