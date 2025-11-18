"""Window and OpenGL context management."""
import pygame
from pygame.locals import *
from OpenGL.GL import *
from core.config import (
    WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE,
    OPENGL_MAJOR_VERSION, OPENGL_MINOR_VERSION
)


class Window:
    """Manages pygame window and OpenGL context."""

    def __init__(self):
        """Initialize window and OpenGL context."""
        pygame.init()

        # Set OpenGL attributes before creating window
        pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MAJOR_VERSION, OPENGL_MAJOR_VERSION)
        pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MINOR_VERSION, OPENGL_MINOR_VERSION)
        pygame.display.gl_set_attribute(pygame.GL_CONTEXT_PROFILE_MASK,
                                       pygame.GL_CONTEXT_PROFILE_CORE)
        pygame.display.gl_set_attribute(pygame.GL_DEPTH_SIZE, 24)
        pygame.display.gl_set_attribute(pygame.GL_DOUBLEBUFFER, 1)

        # Create window
        self.width = WINDOW_WIDTH
        self.height = WINDOW_HEIGHT
        self.screen = pygame.display.set_mode(
            (self.width, self.height),
            DOUBLEBUF | OPENGL
        )
        pygame.display.set_caption(WINDOW_TITLE)

        # Capture mouse
        pygame.event.set_grab(True)
        pygame.mouse.set_visible(False)

        # Initialize OpenGL settings
        self._init_opengl()

        self.clock = pygame.time.Clock()

    def _init_opengl(self):
        """Initialize OpenGL state."""
        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LESS)

        glEnable(GL_CULL_FACE)
        glCullFace(GL_BACK)
        glFrontFace(GL_CCW)

        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        glClearColor(0.1, 0.1, 0.1, 1.0)

        # Set viewport
        glViewport(0, 0, self.width, self.height)

        # Check for OpenGL errors after initialization
        self._check_gl_error("OpenGL initialization")

    def _check_gl_error(self, location=""):
        """Check for OpenGL errors and print if found.

        Args:
            location: Description of where the check is happening
        """
        err = glGetError()
        if err != GL_NO_ERROR:
            error_messages = {
                GL_INVALID_ENUM: "GL_INVALID_ENUM",
                GL_INVALID_VALUE: "GL_INVALID_VALUE",
                GL_INVALID_OPERATION: "GL_INVALID_OPERATION",
                GL_OUT_OF_MEMORY: "GL_OUT_OF_MEMORY",
                GL_INVALID_FRAMEBUFFER_OPERATION: "GL_INVALID_FRAMEBUFFER_OPERATION"
            }
            error_name = error_messages.get(err, f"Unknown error code: {err}")
            print(f"⚠️  OpenGL Error at {location}: {error_name}")

    def clear(self):
        """Clear the screen."""
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    def swap_buffers(self):
        """Swap display buffers."""
        pygame.display.flip()

    def get_aspect_ratio(self):
        """Get window aspect ratio.

        Returns:
            Width / height ratio
        """
        return self.width / self.height

    def tick(self, fps):
        """Limit frame rate.

        Args:
            fps: Target frames per second

        Returns:
            Delta time in seconds
        """
        return self.clock.tick(fps) / 1000.0

    def get_fps(self):
        """Get current FPS.

        Returns:
            Current frames per second
        """
        return self.clock.get_fps()

    def close(self):
        """Clean up and close window."""
        pygame.quit()
