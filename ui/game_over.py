"""Game Over Screen UI for Doom Clone."""
import pygame

class GameOverScreen:
    """Handles the Game Over UI display."""
    def __init__(self, width, height):
        self.width = width
        self.height = height
        pygame.font.init()
        self.font_big = pygame.font.Font(None, 90)
        self.font_small = pygame.font.Font(None, 45)

    def render(self, surface, kills=0, restart_hint=True):
        """Render the game over screen onto the given surface.
        Args:
            surface: Pygame surface to draw on
            kills: Number of kills to display
            restart_hint: If True, show a restart hint
        """
        # Semi-transparent black overlay
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        surface.blit(overlay, (0, 0))

        # 'Game Over' text
        text = self.font_big.render("GAME OVER", True, (255, 0, 0))
        text_rect = text.get_rect(center=(self.width // 2, self.height // 2 - 80))
        surface.blit(text, text_rect)

        # Kills text
        kills_text = self.font_small.render(f"Total Kills: {kills}", True, (255, 200, 80))
        kills_rect = kills_text.get_rect(center=(self.width // 2, self.height // 2 + 10))
        surface.blit(kills_text, kills_rect)
        
        # Hint to restart/quit
        if restart_hint:
            hint_text = self.font_small.render("Press [R] to Restart or [ESC] to Quit", True, (220, 220, 220))
            hint_rect = hint_text.get_rect(center=(self.width // 2, self.height // 2 + 80))
            surface.blit(hint_text, hint_rect)
