"""Enhanced heads-up display with upgrade info and damage indicators."""
import pygame
import numpy as np


class HUD:
    """Enhanced Doom-style HUD."""

    def __init__(self, screen_width, screen_height):
        """Initialize HUD."""
        self.width = screen_width
        self.height = screen_height
        self.font = None

        # Damage direction indicators
        self.damage_indicators = []  # List of (angle, time_remaining)
        self.indicator_duration = 0.8  # How long indicators stay visible

        # Initialize pygame font
        pygame.font.init()
        self.font = pygame.font.Font(None, 36)

    def add_damage_indicator(self, damage_source_position, player_position):
        """Add damage direction indicator.

        Args:
            damage_source_position: Position of damage source
            player_position: Player position
        """
        # Calculate angle to damage source
        direction = damage_source_position - player_position
        direction[1] = 0  # Ignore Y
        angle = np.arctan2(direction[2], direction[0])
        
        self.damage_indicators.append({
            'angle': angle,
            'time': self.indicator_duration,
            'intensity': 1.0
        })

    def update(self, dt):
        """Update HUD elements.

        Args:
            dt: Delta time
        """
        # Update damage indicators
        for indicator in self.damage_indicators[:]:
            indicator['time'] -= dt
            indicator['intensity'] = indicator['time'] / self.indicator_duration
            if indicator['time'] <= 0:
                self.damage_indicators.remove(indicator)

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

        # Damage direction indicators
        self._render_damage_indicators(surface, player)

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

        # Weapon info with upgrade display (bottom-right)
        self._render_weapon_info(surface, player)

        # Low ammo warning
        self._render_ammo_warning(surface, player)

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

    def _render_damage_indicators(self, surface, player):
        """Render directional damage indicators around screen edges.

        Args:
            surface: Pygame surface
            player: Player entity
        """
        center_x = self.width // 2
        center_y = self.height // 2
        radius = min(self.width, self.height) // 2 - 50

        for indicator in self.damage_indicators:
            angle = indicator['angle']
            intensity = indicator['intensity']

            # Convert to screen position
            # Adjust angle relative to player's camera yaw
            if hasattr(player, 'camera'):
                relative_angle = angle - player.camera.yaw
            else:
                relative_angle = angle

            # Calculate position on edge
            x = center_x + int(np.cos(relative_angle) * radius)
            y = center_y + int(np.sin(relative_angle) * radius)

            # Draw indicator (triangle pointing inward)
            alpha = int(255 * intensity)
            color = (255, 50, 50, alpha)

            # Triangle points
            size = 30
            tip_x = x
            tip_y = y
            base_angle = relative_angle + np.pi  # Point towards center

            points = [
                (tip_x, tip_y),
                (tip_x + int(np.cos(base_angle + 0.5) * size), 
                 tip_y + int(np.sin(base_angle + 0.5) * size)),
                (tip_x + int(np.cos(base_angle - 0.5) * size), 
                 tip_y + int(np.sin(base_angle - 0.5) * size))
            ]

            # Draw with alpha
            temp_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            pygame.draw.polygon(temp_surface, color, points)
            surface.blit(temp_surface, (0, 0))

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
        """Render weapon information with upgrade level.

        Args:
            surface: Pygame surface
            player: Player entity
        """
        x = self.width - 250
        y = self.height - 120

        if player.current_weapon:
            weapon = player.current_weapon

            # Weapon name with upgrade level
            if hasattr(weapon, 'upgrade_level') and weapon.upgrade_level > 0:
                weapon_name = f"{weapon.name} +{weapon.upgrade_level}"
                name_color = (255, 215, 0)  # Gold for upgraded weapons
            else:
                weapon_name = weapon.name
                name_color = (255, 255, 255)

            weapon_text = self.font.render(weapon_name, True, name_color)
            surface.blit(weapon_text, (x, y))

            # Upgrade effects (if any)
            if hasattr(weapon, 'upgrades') and weapon.upgrades:
                font_tiny = pygame.font.Font(None, 20)
                y_offset = y + 35
                
                # Show damage boost
                if hasattr(weapon, 'base_damage'):
                    damage_text = font_tiny.render(
                        f"DMG: {weapon.base_damage} → {weapon.damage:.0f}",
                        True, (100, 255, 100)
                    )
                    surface.blit(damage_text, (x, y_offset))
                    y_offset += 18

                # Show special effects
                effects = [u.special_effect for u in weapon.upgrades if u.special_effect]
                if effects:
                    effect_text = font_tiny.render(
                        f"[{', '.join(effects).upper()}]",
                        True, (255, 150, 50)
                    )
                    surface.blit(effect_text, (x, y_offset))

            # Ammo (if weapon uses ammo)
            if weapon.ammo_type:
                ammo = player.ammo.get(weapon.ammo_type, 0)
                
                # Color based on ammo level
                if ammo == 0:
                    ammo_color = (255, 0, 0)  # Red when empty
                elif ammo <= 10:
                    ammo_color = (255, 150, 0)  # Orange when low
                else:
                    ammo_color = (255, 255, 255)  # White when good
                
                ammo_text = self.font.render(f"{ammo}", True, ammo_color)
                surface.blit(ammo_text, (x, y + 45))

                # Ammo type label (small)
                font_small = pygame.font.Font(None, 24)
                type_text = font_small.render(weapon.ammo_type.upper(), True, (180, 180, 180))
                surface.blit(type_text, (x + 60, y + 53))
        else:
            # No weapon equipped
            no_weapon_text = self.font.render("No Weapon", True, (128, 128, 128))
            surface.blit(no_weapon_text, (x, y))

    def _render_ammo_warning(self, surface, player):
        """Render low ammo warning.

        Args:
            surface: Pygame surface
            player: Player entity
        """
        if not player.current_weapon or not player.current_weapon.ammo_type:
            return

        ammo = player.ammo.get(player.current_weapon.ammo_type, 0)

        if ammo == 0:
            # Out of ammo - critical warning
            font_large = pygame.font.Font(None, 48)
            warning_text = font_large.render("OUT OF AMMO!", True, (255, 0, 0))
            text_rect = warning_text.get_rect(center=(self.width // 2, self.height - 150))
            
            # Flashing effect
            import time
            if int(time.time() * 4) % 2 == 0:
                surface.blit(warning_text, text_rect)
        elif ammo <= 5:
            # Very low ammo - warning
            font_med = pygame.font.Font(None, 36)
            warning_text = font_med.render("LOW AMMO", True, (255, 150, 0))
            text_rect = warning_text.get_rect(center=(self.width // 2, self.height - 150))
            surface.blit(warning_text, text_rect)

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

        # Health bar with gradient effect
        if health_pct > 0:
            health_width = int(bar_width * health_pct)

            # Color based on health percentage
            if health_pct > 0.6:
                color1 = (50, 200, 50)
                color2 = (30, 150, 30)
            elif health_pct > 0.3:
                color1 = (255, 200, 0)
                color2 = (200, 150, 0)
            else:
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

        # Health text
        health_value = int(player.health)
        font_large = pygame.font.Font(None, 42)
        health_text = font_large.render(f"{health_value}", True, (255, 255, 255))
        text_rect = health_text.get_rect(center=(x + bar_width // 2, y + bar_height // 2))

        # Text shadow
        shadow_text = font_large.render(f"{health_value}", True, (0, 0, 0))
        shadow_rect = shadow_text.get_rect(center=(x + bar_width // 2 + 2, y + bar_height // 2 + 2))
        surface.blit(shadow_text, shadow_rect)
        surface.blit(health_text, text_rect)

        # Label
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

        # Armor bar with gradient effect
        if armor_pct > 0:
            armor_width = int(bar_width * armor_pct)
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

        # Armor text
        armor_value = int(player.armor)
        font_med = pygame.font.Font(None, 32)
        armor_text = font_med.render(f"{armor_value}", True, (255, 255, 255))
        text_rect = armor_text.get_rect(center=(x + bar_width // 2, y + bar_height // 2))

        # Text shadow
        shadow_text = font_med.render(f"{armor_value}", True, (0, 0, 0))
        shadow_rect = shadow_text.get_rect(center=(x + bar_width // 2 + 1, y + bar_height // 2 + 1))
        surface.blit(shadow_text, shadow_rect)
        surface.blit(armor_text, text_rect)

        # Label
        font_small = pygame.font.Font(None, 20)
        label_text = font_small.render("ARMOR", True, (255, 255, 255))
        surface.blit(label_text, (x, y - 20))
