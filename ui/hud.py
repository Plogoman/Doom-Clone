"""Heads-up display."""
import pygame


class HUD:
    """Doom-style HUD."""

    def __init__(self, screen_width, screen_height):
        """Initialize HUD."""
        self.width = screen_width
        self.height = screen_height
        self.font = None

        # Initialize pygame font
        pygame.font.init()
        self.font = pygame.font.Font(None, 36)

    def render(self, player):
        """Render HUD to offscreen surface.

        Args:
            player: Player entity

        Returns:
            Pygame surface with HUD rendered
        """
        if not player:
            return None

        # Create offscreen surface with alpha channel
        surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        surface.fill((0, 0, 0, 0))  # Transparent background

        # Damage flash (full screen red overlay)
        if player.damage_flash > 0:
            self._render_damage_flash(surface, player.damage_flash)

        # Crosshair
        self._render_crosshair(surface)

        # Color legend (top-right)
        self._render_color_legend(surface)

        # Position info (top-left)
        self._render_position_info(surface, player)

        # Kill counter (top-center)
        self._render_kill_counter(surface, player)

        # Modern health and armor bars
        self._render_health_bar(surface, player)
        self._render_armor_bar(surface, player)

        # Weapon info (bottom-right)
        self._render_weapon_info(surface, player)

        return surface

    def _render_damage_flash(self, surface, flash_time):
        """Render red damage flash overlay.

        Args:
            surface: Pygame surface
            flash_time: Time remaining for flash
        """
        # Calculate alpha based on remaining time (fade out)
        alpha = int(min(255, flash_time / 0.3 * 120))  # Max 120 alpha

        # Create semi-transparent red overlay
        overlay = pygame.Surface((self.width, self.height))
        overlay.set_alpha(alpha)
        overlay.fill((255, 0, 0))
        surface.blit(overlay, (0, 0))

    def _render_crosshair(self, surface):
        """Render crosshair in center of screen.

        Args:
            surface: Pygame surface
        """
        center_x = self.width // 2
        center_y = self.height // 2
        size = 10
        thickness = 3

        # Draw black outline
        pygame.draw.line(surface, (0, 0, 0),
                        (center_x - size - 1, center_y),
                        (center_x + size + 1, center_y),
                        thickness + 2)
        pygame.draw.line(surface, (0, 0, 0),
                        (center_x, center_y - size - 1),
                        (center_x, center_y + size + 1),
                        thickness + 2)

        # Draw white crosshair
        pygame.draw.line(surface, (255, 255, 255),
                        (center_x - size, center_y),
                        (center_x + size, center_y),
                        thickness)
        pygame.draw.line(surface, (255, 255, 255),
                        (center_x, center_y - size),
                        (center_x, center_y + size),
                        thickness)

    def _render_color_legend(self, surface):
        """Render monster color legend.

        Args:
            surface: Pygame surface
        """
        font_small = pygame.font.Font(None, 28)
        x = self.width - 180
        y = 10

        # Title
        title = font_small.render("MONSTERS:", True, (255, 255, 255))
        surface.blit(title, (x, y))
        y += 30

        # Imp - Red
        pygame.draw.rect(surface, (200, 50, 50), (x, y, 20, 20))
        text = font_small.render("Imp (Red)", True, (255, 255, 255))
        surface.blit(text, (x + 25, y))
        y += 25

        # Demon - Pink
        pygame.draw.rect(surface, (220, 120, 180), (x, y, 20, 20))
        text = font_small.render("Demon (Pink)", True, (255, 255, 255))
        surface.blit(text, (x + 25, y))
        y += 25

        # Fireball - Orange
        pygame.draw.circle(surface, (255, 180, 0), (x + 10, y + 10), 10)
        text = font_small.render("Fireball", True, (255, 255, 255))
        surface.blit(text, (x + 25, y))

    def _render_position_info(self, surface, player):
        """Render player position and debug info.

        Args:
            surface: Pygame surface
            player: Player entity
        """
        font_small = pygame.font.Font(None, 24)
        x, y, z = player.position
        pos_text = font_small.render(f"Pos: ({x:.1f}, {y:.1f}, {z:.1f})", True, (255, 255, 255))
        surface.blit(pos_text, (10, 10))

    def _render_weapon_info(self, surface, player):
        """Render weapon information.

        Args:
            surface: Pygame surface
            player: Player entity
        """
        x = self.width - 200
        y = self.height - 100

        if player.current_weapon:
            # Weapon name (large)
            weapon_text = self.font.render(player.current_weapon.name, True, (255, 255, 255))
            surface.blit(weapon_text, (x, y))

            # Ammo (if weapon uses ammo)
            if player.current_weapon.ammo_type:
                ammo = player.ammo.get(player.current_weapon.ammo_type, 0)
                ammo_color = (255, 255, 255) if ammo > 10 else (255, 100, 100)  # Red when low
                ammo_text = self.font.render(f"{ammo}", True, ammo_color)
                surface.blit(ammo_text, (x, y + 40))

                # Ammo type label (small)
                font_small = pygame.font.Font(None, 24)
                type_text = font_small.render(player.current_weapon.ammo_type.upper(), True, (180, 180, 180))
                surface.blit(type_text, (x + 60, y + 48))
        else:
            # No weapon equipped
            no_weapon_text = self.font.render("No Weapon", True, (128, 128, 128))
            surface.blit(no_weapon_text, (x, y))

    def _render_kill_counter(self, surface, player):
        """Render kill counter at top-center.

        Args:
            surface: Pygame surface
            player: Player entity
        """
        kills = player.kills if hasattr(player, 'kills') else 0
        kill_text = self.font.render(f"💀 Kills: {kills}", True, (255, 200, 0))
        text_rect = kill_text.get_rect(center=(self.width // 2, 20))
        surface.blit(kill_text, text_rect)

    def _render_health_bar(self, surface, player):
        """Render modern health bar with gradient.

        Args:
            surface: Pygame surface
            player: Player entity
        """
        x = 20
        y = self.height - 80
        bar_width = 250
        bar_height = 30

        # Calculate health percentage
        health_pct = max(0.0, min(1.0, player.health / player.max_health))

        # Background (dark)
        bg_rect = pygame.Rect(x, y, bar_width, bar_height)
        pygame.draw.rect(surface, (20, 20, 20), bg_rect)

        # Health bar with gradient effect (red)
        if health_pct > 0:
            health_width = int(bar_width * health_pct)

            # Color based on health percentage
            if health_pct > 0.6:
                # Green zone (60-100%)
                color1 = (50, 200, 50)
                color2 = (30, 150, 30)
            elif health_pct > 0.3:
                # Yellow zone (30-60%)
                color1 = (255, 200, 0)
                color2 = (200, 150, 0)
            else:
                # Red zone (0-30%) - critical
                color1 = (255, 50, 50)
                color2 = (200, 20, 20)

            # Draw gradient
            for i in range(health_width):
                ratio = i / bar_width
                r = int(color1[0] + (color2[0] - color1[0]) * ratio)
                g = int(color1[1] + (color2[1] - color1[1]) * ratio)
                b = int(color1[2] + (color2[2] - color1[2]) * ratio)
                pygame.draw.line(surface, (r, g, b), (x + i, y), (x + i, y + bar_height))

        # Border
        pygame.draw.rect(surface, (255, 255, 255), bg_rect, 2)

        # Health text (large, inside bar)
        health_value = int(player.health)
        font_large = pygame.font.Font(None, 42)
        health_text = font_large.render(f"{health_value}", True, (255, 255, 255))
        text_rect = health_text.get_rect(center=(x + bar_width // 2, y + bar_height // 2))

        # Text shadow for readability
        shadow_text = font_large.render(f"{health_value}", True, (0, 0, 0))
        shadow_rect = shadow_text.get_rect(center=(x + bar_width // 2 + 2, y + bar_height // 2 + 2))
        surface.blit(shadow_text, shadow_rect)
        surface.blit(health_text, text_rect)

        # "HEALTH" label
        font_small = pygame.font.Font(None, 20)
        label_text = font_small.render("HEALTH", True, (255, 255, 255))
        surface.blit(label_text, (x, y - 20))

    def _render_armor_bar(self, surface, player):
        """Render modern armor bar with gradient.

        Args:
            surface: Pygame surface
            player: Player entity
        """
        x = 20
        y = self.height - 40
        bar_width = 250
        bar_height = 25

        # Calculate armor percentage
        armor_pct = max(0.0, min(1.0, player.armor / player.max_armor))

        # Background (dark)
        bg_rect = pygame.Rect(x, y, bar_width, bar_height)
        pygame.draw.rect(surface, (20, 20, 20), bg_rect)

        # Armor bar with gradient effect (blue)
        if armor_pct > 0:
            armor_width = int(bar_width * armor_pct)

            # Blue gradient
            color1 = (50, 150, 255)
            color2 = (20, 80, 180)

            # Draw gradient
            for i in range(armor_width):
                ratio = i / bar_width
                r = int(color1[0] + (color2[0] - color1[0]) * ratio)
                g = int(color1[1] + (color2[1] - color1[1]) * ratio)
                b = int(color1[2] + (color2[2] - color1[2]) * ratio)
                pygame.draw.line(surface, (r, g, b), (x + i, y), (x + i, y + bar_height))

        # Border
        pygame.draw.rect(surface, (255, 255, 255), bg_rect, 2)

        # Armor text (inside bar)
        armor_value = int(player.armor)
        font_med = pygame.font.Font(None, 32)
        armor_text = font_med.render(f"{armor_value}", True, (255, 255, 255))
        text_rect = armor_text.get_rect(center=(x + bar_width // 2, y + bar_height // 2))

        # Text shadow
        shadow_text = font_med.render(f"{armor_value}", True, (0, 0, 0))
        shadow_rect = shadow_text.get_rect(center=(x + bar_width // 2 + 1, y + bar_height // 2 + 1))
        surface.blit(shadow_text, shadow_rect)
        surface.blit(armor_text, text_rect)

        # "ARMOR" label
        font_small = pygame.font.Font(None, 20)
        label_text = font_small.render("ARMOR", True, (255, 255, 255))
        surface.blit(label_text, (x, y - 20))
