"""HUD renderer - converts pygame surfaces to OpenGL texture overlays."""
from OpenGL.GL import *
import pygame
import numpy as np

class HUDRenderer:
    """Renders pygame surfaces as OpenGL texture overlays."""

    def __init__(self):
        """Initialize HUD renderer."""
        self.texture_id = None
        self.vao = None
        self.vbo = None
        self.width = 0
        self.height = 0
        self._initialized = False

    def initialize(self, width, height):
        """Initialize OpenGL resources for HUD rendering.

        Args:
            width: Screen width
            height: Screen height
        """
        self.width = width
        self.height = height

        # Create fullscreen quad vertices (2D screen space)
        # Position (x, y) and TexCoord (u, v)
        vertices = np.array([
            # Positions    # TexCoords
            -1.0, -1.0,    0.0, 0.0,  # Bottom-left
             1.0, -1.0,    1.0, 0.0,  # Bottom-right
             1.0,  1.0,    1.0, 1.0,  # Top-right

            -1.0, -1.0,    0.0, 0.0,  # Bottom-left
             1.0,  1.0,    1.0, 1.0,  # Top-right
            -1.0,  1.0,    0.0, 1.0,  # Top-left
        ], dtype=np.float32)

        # Create VAO and VBO
        self.vao = glGenVertexArrays(1)
        self.vbo = glGenBuffers(1)

        glBindVertexArray(self.vao)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)

        # Position attribute
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 4 * 4, ctypes.c_void_p(0))

        # TexCoord attribute
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 4 * 4, ctypes.c_void_p(2 * 4))

        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindVertexArray(0)

        # Create texture
        self.texture_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.texture_id)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        glBindTexture(GL_TEXTURE_2D, 0)

        self._initialized = True
        print("✓ HUD Renderer initialized")

    def render_surface(self, surface, shader):
        """Render pygame surface as OpenGL overlay.

        Args:
            surface: Pygame surface to render
            shader: Shader to use for rendering
        """
        if not self._initialized:
            print("⚠️  HUDRenderer not initialized!")
            return

        if surface is None:
            return

        # Convert pygame surface to OpenGL texture
        texture_data = pygame.image.tostring(surface, 'RGBA', True)

        glBindTexture(GL_TEXTURE_2D, self.texture_id)
        glTexImage2D(
            GL_TEXTURE_2D, 0, GL_RGBA,
            surface.get_width(), surface.get_height(),
            0, GL_RGBA, GL_UNSIGNED_BYTE, texture_data
        )

        # Disable depth test (HUD always on top)
        glDisable(GL_DEPTH_TEST)

        # Enable alpha blending
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        # Use shader
        shader.use()

        # Bind texture
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, self.texture_id)
        shader.set_int('hudTexture', 0)

        # Draw fullscreen quad
        glBindVertexArray(self.vao)
        glDrawArrays(GL_TRIANGLES, 0, 6)
        glBindVertexArray(0)

        # Re-enable depth test for 3D rendering
        glEnable(GL_DEPTH_TEST)

    def cleanup(self):
        """Clean up OpenGL resources."""
        if self.vao:
            glDeleteVertexArrays(1, [self.vao])
        if self.vbo:
            glDeleteBuffers(1, [self.vbo])
        if self.texture_id:
            glDeleteTextures([self.texture_id])
