"""Audio management."""
import pygame.mixer as mixer


class AudioManager:
    """Manages sound effects and music."""

    def __init__(self):
        """Initialize audio system."""
        mixer.init()
        self.sounds = {}
        self.music_volume = 0.7
        self.sfx_volume = 0.8

    def load_sound(self, name, path):
        """Load sound effect.

        Args:
            name: Sound name
            path: Path to sound file
        """
        try:
            sound = mixer.Sound(path)
            sound.set_volume(self.sfx_volume)
            self.sounds[name] = sound
        except:
            print(f"Failed to load sound: {path}")

    def play_sound(self, name):
        """Play sound effect.

        Args:
            name: Sound name
        """
        if name in self.sounds:
            self.sounds[name].play()

    def play_music(self, path, loop=-1):
        """Play background music.

        Args:
            path: Path to music file
            loop: Loop count (-1 for infinite)
        """
        try:
            mixer.music.load(path)
            mixer.music.set_volume(self.music_volume)
            mixer.music.play(loop)
        except:
            print(f"Failed to load music: {path}")

    def stop_music(self):
        """Stop background music."""
        mixer.music.stop()

    def cleanup(self):
        """Clean up audio resources."""
        mixer.quit()
