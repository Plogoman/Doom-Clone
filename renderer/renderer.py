"""Main rendering system."""
from OpenGL.GL import *
import pygame
import numpy as np
from renderer.shader import Shader
from renderer.texture_manager import TextureManager
from renderer.sprite_renderer import SpriteRenderer
from renderer.hud_renderer import HUDRenderer


class Renderer:
    """Main renderer coordinating all rendering systems."""

    def __init__(self):
        """Initialize renderer."""
        self.texture_manager = TextureManager()

        # Shaders (to be loaded)
        self.world_shader = None
        self.sprite_shader = None
        self.ui_shader = None
        self.hud_shader = None

        # Sub-renderers
        self.sprite_renderer = None
        self.hud_renderer = None

        # Window reference (set by game)
        self.window = None

        self._initialized = False

    def initialize(self):
        """Load shaders and initialize rendering systems."""
        if self._initialized:
            return

        # Load shaders
        try:
            self.world_shader = Shader.load_from_files(
                'assets/shaders/world.vert',
                'assets/shaders/world.frag'
            )
            self.sprite_shader = Shader.load_from_files(
                'assets/shaders/sprite.vert',
                'assets/shaders/sprite.frag'
            )
            self.ui_shader = Shader.load_from_files(
                'assets/shaders/ui.vert',
                'assets/shaders/ui.frag'
            )
        except FileNotFoundError as e:
            print(f"Warning: Could not load shaders: {e}")
            print("Using placeholder shaders")
            # Create simple fallback shaders if files don't exist
            self.world_shader = self._create_simple_shader()
            self.sprite_shader = self._create_simple_shader()
            self.ui_shader = self._create_simple_shader()

        # Create simple HUD shader
        self.hud_shader = self._create_hud_shader()

        # Initialize sub-renderers
        self.sprite_renderer = SpriteRenderer(self.sprite_shader)
        self.hud_renderer = HUDRenderer()

        # Initialize HUD renderer with window dimensions
        if self.window:
            self.hud_renderer.initialize(self.window.width, self.window.height)

        # Create default textures
        self.texture_manager.create_solid_color_texture('white', (255, 255, 255, 255))
        self.texture_manager.create_solid_color_texture('missing', (255, 0, 255, 255))

        self._initialized = True
        print("✓ Renderer initialized successfully")
        print(f"  - World shader: {'loaded' if self.world_shader else 'failed'}")
        print(f"  - Sprite shader: {'loaded' if self.sprite_shader else 'failed'}")
        print(f"  - HUD shader: {'loaded' if self.hud_shader else 'failed'}")

    def _create_simple_shader(self):
        """Create simple fallback shader."""
        vertex_src = """
        #version 330 core
        layout (location = 0) in vec3 aPos;
        layout (location = 1) in vec2 aTexCoord;

        out vec2 TexCoord;

        uniform mat4 model;
        uniform mat4 view;
        uniform mat4 projection;

        void main() {
            gl_Position = projection * view * model * vec4(aPos, 1.0);
            TexCoord = aTexCoord;
        }
        """

        fragment_src = """
        #version 330 core
        in vec2 TexCoord;
        out vec4 FragColor;

        uniform sampler2D textureSampler;

        void main() {
            FragColor = texture(textureSampler, TexCoord);
        }
        """

        return Shader(vertex_src, fragment_src)

    def _create_hud_shader(self):
        """Create simple HUD overlay shader."""
        vertex_src = """
        #version 330 core
        layout (location = 0) in vec2 aPos;
        layout (location = 1) in vec2 aTexCoord;

        out vec2 TexCoord;

        void main() {
            gl_Position = vec4(aPos, 0.0, 1.0);
            TexCoord = aTexCoord;
        }
        """

        fragment_src = """
        #version 330 core
        in vec2 TexCoord;
        out vec4 FragColor;

        uniform sampler2D hudTexture;

        void main() {
            FragColor = texture(hudTexture, TexCoord);
        }
        """

        return Shader(vertex_src, fragment_src)

    def render(self, level, player, entities):
        """Render complete scene.

        Args:
            level: Level to render
            player: Player entity (has camera)
            entities: List of entities to render
        """
        if not self._initialized:
            self.initialize()

        camera = player.camera if player else None
        if not camera:
            return

        # Render world geometry
        if level:
            self._render_level(level, camera)

        # Render entities as sprites
        self._render_entities(entities, camera)

        # Render UI
        # self._render_ui(player)

    def _render_level(self, level, camera):
        """Render level geometry.

        Args:
            level: Level data
            camera: Camera for rendering
        """
        if not hasattr(level, 'render'):
            return

        self.world_shader.use()

        # Get actual aspect ratio from window
        aspect_ratio = self.window.get_aspect_ratio() if self.window else 16.0 / 9.0

        view_matrix = camera.get_view_matrix()
        proj_matrix = camera.get_projection_matrix(aspect_ratio)

        # Debug output (only first frame to avoid spam)
        if not hasattr(self, '_debug_printed'):
            self._debug_printed = True
            print(f"\n🎨 RENDERING DEBUG:")
            print(f"  Camera pos: {camera.position}")
            print(f"  Camera forward: {camera.forward}")
            print(f"  Vertex buffers: {len(level.vertex_buffers)}")
            print(f"  Aspect ratio: {aspect_ratio:.2f}\n")

        self.world_shader.set_mat4('view', view_matrix)
        self.world_shader.set_mat4('projection', proj_matrix)

        level.render(self.world_shader, self.texture_manager)

    def _render_entities(self, entities, camera):
        """Render all entities.

        Args:
            entities: List of entities
            camera: Camera for rendering
        """
        for entity in entities:
            # Skip inactive/dead entities
            if not entity.active:
                continue

            if hasattr(entity, 'sprite_name') and hasattr(entity, 'position'):
                self.sprite_renderer.add_sprite(
                    entity.position,
                    entity.sprite_size if hasattr(entity, 'sprite_size') else [1.0, 1.0],
                    entity.sprite_name
                )

        self.sprite_renderer.render(camera, self.texture_manager)

        # Render health bars for monsters
        self._render_health_bars(entities, camera)

    def render_hud_overlay(self, hud_surface):
        """Render HUD pygame surface as OpenGL overlay.

        Args:
            hud_surface: Pygame surface with HUD rendered
        """
        if not self._initialized:
            self.initialize()

        if hud_surface and self.hud_renderer and self.hud_shader:
            self.hud_renderer.render_surface(hud_surface, self.hud_shader)

    def _render_health_bars(self, entities, camera):
        """Render health bars above monsters.

        Args:
            entities: List of entities
            camera: Camera for rendering
        """
        # Switch to 2D rendering temporarily
        glDisable(GL_DEPTH_TEST)

        for entity in entities:
            # Skip inactive/dead entities
            if not entity.active:
                continue

            # Only render health bars for monsters
            if not hasattr(entity, 'health') or not hasattr(entity, 'max_health'):
                continue
            if not hasattr(entity, 'position'):
                continue

            # Skip if entity is player or projectile
            if hasattr(entity, 'camera') or entity.__class__.__name__ in ['Projectile', 'Fireball']:
                continue

            # Calculate screen position (above monster)
            health_bar_pos = entity.position + np.array([0, entity.sprite_size[1] + 0.3, 0], dtype=np.float32) if hasattr(entity, 'sprite_size') else entity.position + np.array([0, 2.0, 0], dtype=np.float32)

            # Project to screen space
            screen_pos = self._world_to_screen(health_bar_pos, camera)

            if screen_pos is None:
                continue  # Behind camera

            # Draw health bar using pygame
            if self.window:
                self._draw_health_bar_2d(screen_pos, entity.health, entity.max_health)

        glEnable(GL_DEPTH_TEST)

    def _world_to_screen(self, world_pos, camera):
        """Convert world position to screen coordinates.

        Args:
            world_pos: 3D world position
            camera: Camera

        Returns:
            (x, y) screen coordinates or None if behind camera
        """
        # Get view and projection matrices
        aspect_ratio = self.window.get_aspect_ratio() if self.window else 16.0 / 9.0
        view_matrix = camera.get_view_matrix()
        proj_matrix = camera.get_projection_matrix(aspect_ratio)

        # Transform to clip space
        pos_h = np.array([world_pos[0], world_pos[1], world_pos[2], 1.0], dtype=np.float32)
        pos_view = view_matrix @ pos_h
        pos_clip = proj_matrix @ pos_view

        # Check if behind camera
        if pos_clip[3] == 0 or pos_clip[2] < 0:
            return None

        # Perspective divide
        ndc = pos_clip[:3] / pos_clip[3]

        # Check if outside screen
        if abs(ndc[0]) > 1.5 or abs(ndc[1]) > 1.5:
            return None

        # Convert to screen coordinates
        screen_x = (ndc[0] + 1.0) * 0.5 * self.window.width
        screen_y = (1.0 - ndc[1]) * 0.5 * self.window.height  # Flip Y

        return (int(screen_x), int(screen_y))

    def _draw_health_bar_2d(self, screen_pos, health, max_health):
        """Draw health bar on pygame surface.

        Args:
            screen_pos: (x, y) screen position
            health: Current health
            max_health: Maximum health
        """
        x, y = screen_pos
        bar_width = 50
        bar_height = 6

        # Background (black)
        bg_rect = pygame.Rect(x - bar_width // 2, y, bar_width, bar_height)
        pygame.draw.rect(self.window.screen, (0, 0, 0), bg_rect)

        # Health bar (red to green based on health percentage)
        health_pct = max(0, min(1, health / max_health))
        health_width = int(bar_width * health_pct)

        if health_width > 0:
            # Color interpolation: green at full health, yellow at 50%, red at low
            if health_pct > 0.5:
                color = (int(255 * (1 - health_pct) * 2), 255, 0)  # Green to yellow
            else:
                color = (255, int(255 * health_pct * 2), 0)  # Yellow to red

            health_rect = pygame.Rect(x - bar_width // 2, y, health_width, bar_height)
            pygame.draw.rect(self.window.screen, color, health_rect)

        # Border (white)
        pygame.draw.rect(self.window.screen, (255, 255, 255), bg_rect, 1)

    def cleanup(self):
        """Clean up renderer resources."""
        if self.world_shader:
            self.world_shader.delete()
        if self.sprite_shader:
            self.sprite_shader.delete()
        if self.ui_shader:
            self.ui_shader.delete()

        if self.sprite_renderer:
            self.sprite_renderer.cleanup()

        self.texture_manager.cleanup()
