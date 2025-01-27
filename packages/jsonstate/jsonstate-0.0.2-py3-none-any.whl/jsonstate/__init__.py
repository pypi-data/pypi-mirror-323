"""Store and modify global app state in JSON (Python dictionary) to re-render front-end components."""

__version__ = '0.0.2'


class State:
    def __init__(self, state: dict) -> None:
        self.state = state
