"""OpenGL shader management."""
from OpenGL.GL import *
import numpy as np


class Shader:
    """OpenGL shader program wrapper."""

    def __init__(self, vertex_src, fragment_src):
        """Compile and link shader program.

        Args:
            vertex_src: Vertex shader source code
            fragment_src: Fragment shader source code
        """
        self.program = self._create_program(vertex_src, fragment_src)
        self.uniforms = {}

    def _create_program(self, vertex_src, fragment_src):
        """Compile shaders and link program."""
        # Compile vertex shader
        vertex_shader = glCreateShader(GL_VERTEX_SHADER)
        glShaderSource(vertex_shader, vertex_src)
        glCompileShader(vertex_shader)
        if not glGetShaderiv(vertex_shader, GL_COMPILE_STATUS):
            error = glGetShaderInfoLog(vertex_shader).decode()
            raise RuntimeError(f"Vertex shader compilation failed:\n{error}")

        # Compile fragment shader
        fragment_shader = glCreateShader(GL_FRAGMENT_SHADER)
        glShaderSource(fragment_shader, fragment_src)
        glCompileShader(fragment_shader)
        if not glGetShaderiv(fragment_shader, GL_COMPILE_STATUS):
            error = glGetShaderInfoLog(fragment_shader).decode()
            raise RuntimeError(f"Fragment shader compilation failed:\n{error}")

        # Link program
        program = glCreateProgram()
        glAttachShader(program, vertex_shader)
        glAttachShader(program, fragment_shader)
        glLinkProgram(program)

        if not glGetProgramiv(program, GL_LINK_STATUS):
            error = glGetProgramInfoLog(program).decode()
            raise RuntimeError(f"Shader program linking failed:\n{error}")

        # Clean up shaders (no longer needed after linking)
        glDeleteShader(vertex_shader)
        glDeleteShader(fragment_shader)

        return program

    def use(self):
        """Activate this shader program."""
        glUseProgram(self.program)

    def get_uniform_location(self, name):
        """Get uniform location, cached.

        Args:
            name: Uniform variable name

        Returns:
            Uniform location
        """
        if name not in self.uniforms:
            self.uniforms[name] = glGetUniformLocation(self.program, name)
        return self.uniforms[name]

    def set_int(self, name, value):
        """Set integer uniform."""
        loc = self.get_uniform_location(name)
        glUniform1i(loc, value)

    def set_float(self, name, value):
        """Set float uniform."""
        loc = self.get_uniform_location(name)
        glUniform1f(loc, value)

    def set_vec3(self, name, value):
        """Set vec3 uniform."""
        loc = self.get_uniform_location(name)
        glUniform3fv(loc, 1, value)

    def set_vec4(self, name, value):
        """Set vec4 uniform."""
        loc = self.get_uniform_location(name)
        glUniform4fv(loc, 1, value)

    def set_mat4(self, name, value):
        """Set mat4 uniform."""
        loc = self.get_uniform_location(name)
        # GL_TRUE = transpose from row-major (numpy) to column-major (OpenGL)
        glUniformMatrix4fv(loc, 1, GL_TRUE, value)

    def delete(self):
        """Delete shader program."""
        glDeleteProgram(self.program)

    @staticmethod
    def load_from_files(vertex_path, fragment_path):
        """Load shader from files.

        Args:
            vertex_path: Path to vertex shader file
            fragment_path: Path to fragment shader file

        Returns:
            Compiled Shader object
        """
        with open(vertex_path, 'r') as f:
            vertex_src = f.read()
        with open(fragment_path, 'r') as f:
            fragment_src = f.read()

        return Shader(vertex_src, fragment_src)
