from typing import Callable


class Converter:
    def __init__(
        self, conversion_callback: Callable[[str, str, str], str | None] | None = None
    ):
        pass
