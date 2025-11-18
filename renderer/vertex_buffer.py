"""Vertex buffer object management."""
from OpenGL.GL import *
import numpy as np
import ctypes


class VertexBuffer:
    """Manages VBO and VAO for geometry."""

    def __init__(self, vertices, indices=None, layout=None):
        """Create vertex buffer.

        Args:
            vertices: Numpy array of vertex data
            indices: Numpy array of indices (optional)
            layout: List of (size, type, normalized, stride, offset) tuples
        """
        self.vao = glGenVertexArrays(1)
        self.vbo = glGenBuffers(1)
        self.ebo = None
        self.vertex_count = 0
        self.index_count = 0

        glBindVertexArray(self.vao)

        # Upload vertex data (flatten to ensure contiguous 1D array)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        vertices_flat = vertices.flatten() if vertices.ndim > 1 else vertices
        glBufferData(GL_ARRAY_BUFFER, vertices_flat.nbytes, vertices_flat, GL_STATIC_DRAW)

        # Setup vertex attributes
        if layout is None:
            # Default layout: position (3) + texcoord (2)
            layout = [
                (3, GL_FLOAT, GL_FALSE, 5 * 4, 0),  # position
                (2, GL_FLOAT, GL_FALSE, 5 * 4, 3 * 4),  # texcoord
            ]

        for i, (size, dtype, normalized, stride, offset) in enumerate(layout):
            glEnableVertexAttribArray(i)
            glVertexAttribPointer(i, size, dtype, normalized, stride,
                                ctypes.c_void_p(offset))

        self.vertex_count = len(vertices)

        # Upload index data if provided
        if indices is not None:
            self.ebo = glGenBuffers(1)
            glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.ebo)
            glBufferData(GL_ELEMENT_ARRAY_BUFFER, indices.nbytes, indices, GL_STATIC_DRAW)
            self.index_count = len(indices)

        glBindVertexArray(0)

    def bind(self):
        """Bind this vertex buffer for rendering."""
        glBindVertexArray(self.vao)

    def unbind(self):
        """Unbind vertex buffer."""
        glBindVertexArray(0)

    def draw(self, mode=GL_TRIANGLES):
        """Draw this vertex buffer.

        Args:
            mode: OpenGL draw mode (GL_TRIANGLES, GL_LINES, etc.)
        """
        self.bind()
        if self.ebo is not None:
            glDrawElements(mode, self.index_count, GL_UNSIGNED_INT, None)
        else:
            glDrawArrays(mode, 0, self.vertex_count)
        self.unbind()

    def delete(self):
        """Delete buffers."""
        glDeleteBuffers(1, [self.vbo])
        if self.ebo is not None:
            glDeleteBuffers(1, [self.ebo])
        glDeleteVertexArrays(1, [self.vao])


class DynamicVertexBuffer:
    """Dynamic vertex buffer for frequently changing geometry."""

    def __init__(self, max_vertices, layout=None):
        """Create dynamic vertex buffer.

        Args:
            max_vertices: Maximum number of vertices
            layout: Vertex attribute layout
        """
        self.vao = glGenVertexArrays(1)
        self.vbo = glGenBuffers(1)
        self.max_vertices = max_vertices
        self.vertex_count = 0

        glBindVertexArray(self.vao)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)

        # Allocate buffer
        if layout is None:
            stride = 5 * 4  # 3 pos + 2 uv
            layout = [
                (3, GL_FLOAT, GL_FALSE, stride, 0),
                (2, GL_FLOAT, GL_FALSE, stride, 3 * 4),
            ]
        else:
            stride = sum(attr[0] for attr in layout) * 4

        glBufferData(GL_ARRAY_BUFFER, max_vertices * stride, None, GL_DYNAMIC_DRAW)

        # Setup attributes
        for i, (size, dtype, normalized, stride, offset) in enumerate(layout):
            glEnableVertexAttribArray(i)
            glVertexAttribPointer(i, size, dtype, normalized, stride,
                                ctypes.c_void_p(offset))

        glBindVertexArray(0)

    def update(self, vertices):
        """Update vertex data.

        Args:
            vertices: Numpy array of vertex data
        """
        self.vertex_count = len(vertices)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferSubData(GL_ARRAY_BUFFER, 0, vertices.nbytes, vertices)
        glBindBuffer(GL_ARRAY_BUFFER, 0)

    def bind(self):
        """Bind for rendering."""
        glBindVertexArray(self.vao)

    def draw(self, mode=GL_TRIANGLES):
        """Draw buffer."""
        self.bind()
        glDrawArrays(mode, 0, self.vertex_count)
        glBindVertexArray(0)

    def delete(self):
        """Delete buffers."""
        glDeleteBuffers(1, [self.vbo])
        glDeleteVertexArrays(1, [self.vao])
