"""Game Over Screen UI for Doom Clone, rendered to an offscreen surface.

Renders a full-screen white background with black text so it can be drawn as
an OpenGL HUD overlay reliably on top of the 3D scene.
"""
import pygame

class GameOverScreen:
    """Handles the Game Over UI display."""
    def __init__(self, width, height):
        self.width = width
        self.height = height
        pygame.font.init()
        self.font_big = pygame.font.Font(None, 90)
        self.font_small = pygame.font.Font(None, 45)
        # Simple cache so we don't re-render identical static frames every tick
        self._cache_surface = None
        self._cache_params = None

    def render(self, surface=None, kills=0, restart_hint=True):
        """Render the game over screen to an offscreen surface.
        Args:
            surface: Optional existing pygame surface to draw on; if None, a new
                full-size surface will be created.
            kills: Number of kills to display
            restart_hint: If True, show a restart hint
        Returns:
            Pygame Surface with the Game Over screen drawn on it.
        """
        # Return cached surface if parameters haven't changed
        cache_key = (self.width, self.height, kills, bool(restart_hint))
        if self._cache_surface is not None and self._cache_params == cache_key and surface is None:
            return self._cache_surface

        # Create surface if not provided; ensure opaque background
        if surface is None:
            surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

        # Fill background with solid white (opaque)
        surface.fill((255, 255, 255, 255))

        # 'Game Over' text (black)
        text = self.font_big.render("GAME OVER", True, (0, 0, 0))
        text_rect = text.get_rect(center=(self.width // 2, self.height // 2 - 80))
        surface.blit(text, text_rect)

        # Kills text (gray)
        kills_text = self.font_small.render(f"Total Kills: {kills}", True, (64, 64, 64))
        kills_rect = kills_text.get_rect(center=(self.width // 2, self.height // 2 + 10))
        surface.blit(kills_text, kills_rect)

        # Hint to restart/quit
        if restart_hint:
            hint_text = self.font_small.render("Press [R] to Restart or [ESC] to Quit", True, (120, 120, 120))
            hint_rect = hint_text.get_rect(center=(self.width // 2, self.height // 2 + 80))
            surface.blit(hint_text, hint_rect)

        # Update cache only when we created the surface ourselves
        if surface is not None and (self._cache_params != cache_key):
            self._cache_surface = surface.copy()
            self._cache_params = cache_key

        return surface
