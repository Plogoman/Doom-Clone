"""Billboard sprite rendering for entities."""
import numpy as np
from OpenGL.GL import *
from renderer.vertex_buffer import DynamicVertexBuffer


class SpriteRenderer:
    """Renders billboard sprites that always face camera."""

    def __init__(self, shader, max_sprites=256):
        """Initialize sprite renderer.

        Args:
            shader: Shader program for sprite rendering
            max_sprites: Maximum number of sprites per batch
        """
        self.shader = shader
        self.max_sprites = max_sprites
        self.vertex_buffer = DynamicVertexBuffer(max_sprites * 6)  # 6 vertices per sprite
        self.sprites = []

    def add_sprite(self, position, size, texture_name, rotation=0.0):
        """Add sprite to render batch.

        Args:
            position: World position [x, y, z]
            size: Sprite size [width, height]
            texture_name: Texture to use
            rotation: Rotation angle in radians (optional)
        """
        self.sprites.append({
            'position': position,
            'size': size,
            'texture': texture_name,
            'rotation': rotation
        })

    def render(self, camera, texture_manager):
        """Render all sprites.

        Args:
            camera: Camera for view/projection matrices
            texture_manager: Texture manager for binding textures
        """
        if not self.sprites:
            return

        self.shader.use()

        # Sort sprites back-to-front for proper transparency
        cam_pos = camera.position
        self.sprites.sort(key=lambda s: np.linalg.norm(s['position'] - cam_pos), reverse=True)

        # Batch render sprites by texture
        current_texture = None
        vertices_list = []

        for sprite in self.sprites:
            if current_texture != sprite['texture'] and vertices_list:
                # Render current batch
                self._render_batch(vertices_list, current_texture, camera, texture_manager)
                vertices_list = []

            current_texture = sprite['texture']

            # Generate billboard quad
            vertices = self._create_billboard(sprite, camera)
            vertices_list.append(vertices)

        # Render remaining batch
        if vertices_list:
            self._render_batch(vertices_list, current_texture, camera, texture_manager)

        self.sprites.clear()

    def _create_billboard(self, sprite, camera):
        """Create billboard quad vertices.

        Args:
            sprite: Sprite data dict
            camera: Camera for billboard orientation

        Returns:
            Numpy array of 6 vertices (2 triangles)
        """
        pos = sprite['position']
        size = sprite['size']

        # Get camera right and up vectors
        right = camera.right * size[0] * 0.5
        up = camera.up * size[1] * 0.5

        # Create quad corners
        v0 = pos - right - up  # bottom-left
        v1 = pos + right - up  # bottom-right
        v2 = pos + right + up  # top-right
        v3 = pos - right + up  # top-left

        # Create two triangles with position + texcoord
        vertices = np.array([
            # Triangle 1
            [*v0, 0.0, 0.0],
            [*v1, 1.0, 0.0],
            [*v2, 1.0, 1.0],
            # Triangle 2
            [*v0, 0.0, 0.0],
            [*v2, 1.0, 1.0],
            [*v3, 0.0, 1.0],
        ], dtype=np.float32)

        return vertices

    def _render_batch(self, vertices_list, texture_name, camera, texture_manager):
        """Render batch of sprites with same texture.

        Args:
            vertices_list: List of vertex arrays
            texture_name: Texture to bind
            camera: Camera for matrices
            texture_manager: Texture manager
        """
        # Concatenate all vertices
        all_vertices = np.concatenate(vertices_list, axis=0)

        # Update vertex buffer
        self.vertex_buffer.update(all_vertices)

        # Set uniforms
        view_matrix = camera.get_view_matrix()
        # Use window aspect ratio if available
        from core.config import WINDOW_WIDTH, WINDOW_HEIGHT
        aspect_ratio = WINDOW_WIDTH / WINDOW_HEIGHT
        proj_matrix = camera.get_projection_matrix(aspect_ratio)
        self.shader.set_mat4('view', view_matrix)
        self.shader.set_mat4('projection', proj_matrix)

        # Bind texture - fallback to 'missing' if texture doesn't exist
        if texture_manager.get_texture(texture_name):
            texture_manager.bind_texture(texture_name, 0)
        else:
            print(f"Warning: Texture '{texture_name}' not found, using 'missing' texture")
            texture_manager.bind_texture('missing', 0)
        self.shader.set_int('textureSampler', 0)

        # Draw
        glDisable(GL_CULL_FACE)  # Don't cull sprites
        self.vertex_buffer.draw()
        glEnable(GL_CULL_FACE)

    def cleanup(self):
        """Clean up resources."""
        self.vertex_buffer.delete()
