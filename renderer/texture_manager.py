"""Texture loading and management."""
from OpenGL.GL import *
from PIL import Image
import numpy as np


class TextureManager:
    """Manages texture loading and caching."""

    def __init__(self):
        """Initialize texture manager."""
        self.textures = {}  # name -> texture_id
        self.texture_info = {}  # name -> (width, height)

    def load_texture(self, name, path, flip=True):
        """Load texture from file.

        Args:
            name: Texture name for retrieval
            path: Path to image file
            flip: Flip image vertically (default True for OpenGL)

        Returns:
            OpenGL texture ID
        """
        if name in self.textures:
            return self.textures[name]

        # Load image
        img = Image.open(path)
        if flip:
            img = img.transpose(Image.FLIP_TOP_BOTTOM)

        # Convert to RGBA
        img = img.convert('RGBA')
        img_data = np.array(img, dtype=np.uint8)

        # Generate texture
        texture_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texture_id)

        # Set texture parameters
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

        # Upload texture data
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, img.width, img.height,
                     0, GL_RGBA, GL_UNSIGNED_BYTE, img_data)
        glGenerateMipmap(GL_TEXTURE_2D)

        glBindTexture(GL_TEXTURE_2D, 0)

        # Cache texture
        self.textures[name] = texture_id
        self.texture_info[name] = (img.width, img.height)

        return texture_id

    def get_texture(self, name):
        """Get texture ID by name.

        Args:
            name: Texture name

        Returns:
            OpenGL texture ID or None if not found
        """
        return self.textures.get(name)

    def bind_texture(self, name, unit=0):
        """Bind texture to texture unit.

        Args:
            name: Texture name
            unit: Texture unit (0-31)
        """
        if name in self.textures:
            glActiveTexture(GL_TEXTURE0 + unit)
            glBindTexture(GL_TEXTURE_2D, self.textures[name])

    def get_texture_info(self, name):
        """Get texture dimensions.

        Args:
            name: Texture name

        Returns:
            Tuple of (width, height) or None
        """
        return self.texture_info.get(name)

    def create_solid_color_texture(self, name, color):
        """Create 1x1 solid color texture.

        Args:
            name: Texture name
            color: RGBA color tuple (0-255)

        Returns:
            OpenGL texture ID
        """
        if name in self.textures:
            return self.textures[name]

        # Create 1x1 texture
        img_data = np.array([color], dtype=np.uint8)

        texture_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texture_id)

        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)

        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, 1, 1, 0, GL_RGBA, GL_UNSIGNED_BYTE, img_data)

        glBindTexture(GL_TEXTURE_2D, 0)

        self.textures[name] = texture_id
        self.texture_info[name] = (1, 1)

        return texture_id

    def cleanup(self):
        """Delete all textures."""
        for texture_id in self.textures.values():
            glDeleteTextures(1, [texture_id])
        self.textures.clear()
        self.texture_info.clear()
