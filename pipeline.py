from typing import Generic, List, TypeVar

from .emitter import Emitter, FunctionEmitter
from .sink import Sink
from .source import Source
from .stage import Stage

R = TypeVar("R")


class Pipeline(Generic[R]):
    """Source -> [Stage ...] -> Sink.

    Pipeline yalnizca arayuzleri bilir; dosya mi, ag mi, konsol mu oldugunu bilmez.
    """

    def __init__(self, source: Source[R], sink: Sink[R]) -> None:
        self._source = source
        self._sink = sink
        self._stages: List[Stage[R, R]] = []

    def add_stage(self, stage: Stage[R, R]) -> "Pipeline[R]":
        self._stages.append(stage)
        return self

    def run(self) -> None:
        opened: List[Stage[R, R]] = []
        try:
            for stage in self._stages:
                stage.open()
                opened.append(stage)
            self._source.produce(self._build_chain())
        finally:
            # Hata olsa bile acilan stage'ler ters sirada kapanir.
            for stage in reversed(opened):
                stage.close()

    def _build_chain(self) -> Emitter[R]:
        # Sondan basa kur: sink <- stage[n-1] <- ... <- stage[0]
        head: Emitter[R] = FunctionEmitter(self._sink.consume)
        for stage in reversed(self._stages):
            head = FunctionEmitter(self._link(stage, head))
        return head

    @staticmethod
    def _link(stage: Stage[R, R], nxt: Emitter[R]):
        return lambda item: stage.process(item, nxt)
