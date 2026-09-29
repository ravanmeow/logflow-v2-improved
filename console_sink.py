from .sink import Sink


class ConsoleSink(Sink[str]):
    """Her kaydi konsola yazar."""

    def consume(self, item: str) -> None:
        print(item)
