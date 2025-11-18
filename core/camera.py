"""First-person camera controller."""
import numpy as np
from core.config import FOV, NEAR_PLANE, FAR_PLANE, MOUSE_SENSITIVITY


class Camera:
    """First-person camera with position and rotation."""

    def __init__(self, position=None):
        """Initialize camera.

        Args:
            position: Initial position [x, y, z], defaults to origin
        """
        if position is None:
            self.position = np.array([0.0, 0.0, 0.0], dtype=np.float32)
        else:
            self.position = np.array(position, dtype=np.float32)
        self.yaw = 0.0  # Horizontal rotation (radians)
        self.pitch = 0.0  # Vertical rotation (radians)

        self.fov = FOV
        self.near = NEAR_PLANE
        self.far = FAR_PLANE

        self._forward = np.array([1.0, 0.0, 0.0], dtype=np.float32)
        self._right = np.array([0.0, 0.0, 1.0], dtype=np.float32)
        self._up = np.array([0.0, 1.0, 0.0], dtype=np.float32)

        self._update_vectors()

    def _update_vectors(self):
        """Update forward, right, and up vectors based on yaw and pitch."""
        # Calculate forward vector
        self._forward[0] = np.cos(self.yaw) * np.cos(self.pitch)
        self._forward[1] = np.sin(self.pitch)
        self._forward[2] = np.sin(self.yaw) * np.cos(self.pitch)
        self._forward = self._forward / np.linalg.norm(self._forward)

        # Calculate right vector
        world_up = np.array([0.0, 1.0, 0.0], dtype=np.float32)
        self._right = np.cross(self._forward, world_up)
        self._right = self._right / np.linalg.norm(self._right)

        # Calculate up vector
        self._up = np.cross(self._right, self._forward)

    def rotate(self, delta_x, delta_y):
        """Rotate camera by mouse delta.

        Args:
            delta_x: Mouse movement in x (horizontal)
            delta_y: Mouse movement in y (vertical)
        """
        self.yaw += delta_x * MOUSE_SENSITIVITY
        self.pitch -= delta_y * MOUSE_SENSITIVITY

        # Clamp pitch to prevent gimbal lock
        max_pitch = np.pi / 2 - 0.01
        self.pitch = np.clip(self.pitch, -max_pitch, max_pitch)

        self._update_vectors()

    def get_view_matrix(self):
        """Get view matrix for rendering.

        Returns:
            4x4 view matrix as numpy array
        """
        target = self.position + self._forward
        return self._look_at(self.position, target, self._up)

    def get_projection_matrix(self, aspect_ratio):
        """Get projection matrix.

        Args:
            aspect_ratio: Screen width / height

        Returns:
            4x4 projection matrix as numpy array
        """
        return self._perspective(np.radians(self.fov), aspect_ratio, self.near, self.far)

    @staticmethod
    def _look_at(eye, center, up):
        """Create look-at view matrix."""
        f = center - eye
        f = f / np.linalg.norm(f)

        s = np.cross(f, up)
        s = s / np.linalg.norm(s)

        u = np.cross(s, f)

        result = np.identity(4, dtype=np.float32)
        result[0, 0:3] = s
        result[1, 0:3] = u
        result[2, 0:3] = -f
        result[0, 3] = -np.dot(s, eye)
        result[1, 3] = -np.dot(u, eye)
        result[2, 3] = np.dot(f, eye)

        return result

    @staticmethod
    def _perspective(fovy, aspect, near, far):
        """Create perspective projection matrix."""
        f = 1.0 / np.tan(fovy / 2.0)

        result = np.zeros((4, 4), dtype=np.float32)
        result[0, 0] = f / aspect
        result[1, 1] = f
        result[2, 2] = (far + near) / (near - far)
        result[2, 3] = (2.0 * far * near) / (near - far)
        result[3, 2] = -1.0

        return result

    @property
    def forward(self):
        """Get forward direction vector."""
        return self._forward.copy()

    @property
    def right(self):
        """Get right direction vector."""
        return self._right.copy()

    @property
    def up(self):
        """Get up direction vector."""
        return self._up.copy()
