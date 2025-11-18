"""Input management."""
import pygame
from pygame.locals import *


class InputManager:
    """Manages keyboard and mouse input."""

    def __init__(self, player):
        """Initialize input manager.

        Args:
            player: Player entity to control
        """
        self.player = player
        self.keys = {}

    def on_key_down(self, key):
        """Handle key down event.

        Args:
            key: Key code
        """
        self.keys[key] = True

        # Weapon switching
        if K_1 <= key <= K_7:
            slot = key - K_1 + 1
            self.player.switch_weapon(slot)

    def on_key_up(self, key):
        """Handle key up event.

        Args:
            key: Key code
        """
        self.keys[key] = False

    def on_mouse_motion(self, rel):
        """Handle mouse motion.

        Args:
            rel: (dx, dy) mouse movement
        """
        self.player.rotate(rel[0], rel[1])

    def on_mouse_button_down(self, button):
        """Handle mouse button down.

        Args:
            button: Button number
        """
        if button == 1:  # Left click
            self.player.fire_weapon()

    def on_mouse_button_up(self, button):
        """Handle mouse button up.

        Args:
            button: Button number
        """
        pass

    def update(self, dt):
        """Update input state.

        Args:
            dt: Delta time
        """
        # Movement
        forward = 0.0
        right = 0.0

        if self.keys.get(K_w, False) or self.keys.get(K_UP, False):
            forward += 1.0
        if self.keys.get(K_s, False) or self.keys.get(K_DOWN, False):
            forward -= 1.0
        if self.keys.get(K_a, False) or self.keys.get(K_LEFT, False):
            right -= 1.0
        if self.keys.get(K_d, False) or self.keys.get(K_RIGHT, False):
            right += 1.0

        self.player.sprinting = self.keys.get(K_LSHIFT, False)

        # Jump
        if self.keys.get(K_SPACE, False):
            self.player.jump()

        self.player.move(forward, right)
