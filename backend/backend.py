from abc import abstractmethod
from typing import Tuple


class Backend:

    @abstractmethod
    def get_vscreen_size(self) -> Tuple[int, int]:
        """Return the width and height of the virtual screen in pixels.

        The virtual screen is the bounding rectangle of all display monitors.
        """

    @abstractmethod
    def get_vscreen_normalize_offset(self) -> Tuple[int, int]:
        """Returns the coordinates for the top left corner of the virtual screen.

        The virtual screen is the bounding rectangle of all display monitors.
        """