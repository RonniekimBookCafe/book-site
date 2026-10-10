# -*- coding: utf-8 -*-
"""
c01lib_keys.py  |  CORE-01 Educational Library · key input
Release 1.6.3

Reads keyboard input in two ways.

- Drive keys (W/S/A/D/Z/C/Q/E): act while held down. If several are held,
  the most recently pressed key wins; releasing all of them stops the robot.
- Command keys (1/0/2/3/4/5): act once, the moment they are pressed. Holding
  one down does not repeat it.

Official RoboCo API used
- Input.stream(key): reports True once when the key is pressed and False once when it is released.
"""

from inputs import Input


def pressed(stream) -> bool:
    """True if the command key was pressed. Reads and clears all queued input."""
    down = False
    for event in stream:
        if event:
            down = True
    return down


class DriveKeys:
    """Reads several drive keys and decides which action to follow right now."""

    def __init__(self, key_actions: dict):
        """key_actions: {key: action to call when pressed} e.g. {"w": robot.forward}"""
        self.keys = [(key, Input.stream(key), action) for key, action in key_actions.items()]
        self.held = []      # Keys currently held down (in the order pressed)

    def update(self, on_release_all, blocked=None):
        """Handles presses and releases of the drive keys. Called on every pass of the main loop.

        on_release_all: action to call when every key is released (e.g. robot.stop)
        blocked       : function to call when keys are not accepted; it receives the
                        name of the key pressed. None means keys are accepted normally.
        """
        for entry in self.keys:
            key, stream, action = entry
            for event in stream:
                if blocked is not None:          # Not accepting keys right now (e.g. during the mission)
                    if entry in self.held:
                        self.held.remove(entry)
                    if event:
                        blocked(key)
                    continue
                if event:                        # Pressed
                    action()
                    if entry not in self.held:
                        self.held.append(entry)
                else:                            # Released
                    if entry in self.held:
                        self.held.remove(entry)
                    if self.held:
                        self.held[-1][2]()       # Follow the most recently pressed key that is still held
                    else:
                        on_release_all()

    def clear(self):
        """Forgets every held key. They must be pressed again to move (after RESET)."""
        self.held.clear()
