import contextlib
import io
import os
import tempfile
import unittest

from logflow.emitter import Emitter
from logflow.file_line_source import FileLineSource
from logflow.pipeline import Pipeline
from logflow.sink import Sink
from logflow.source import Source
from logflow.stage import Stage, StageException
import main as logflow_main

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAMPLE = os.path.join(ROOT, "data", "access-small.log")


class ListSource(Source[str]):
    def __init__(self, items):
        self.items = items

    def produce(self, out: Emitter[str]) -> None:
        for i in self.items:
            out.emit(i)


class CollectSink(Sink[str]):
    def __init__(self):
        self.items = []

    def consume(self, item: str) -> None:
        self.items.append(item)


class Filter(Stage[str, str]):          # 0 veya 1 cikti
    def process(self, item, out):
        if "404" in item:
            out.emit(item)


class Splitter(Stage[str, str]):        # N cikti
    def process(self, item, out):
        for part in item.split():
            out.emit(part)


class Recorder(Stage[str, str]):
    def __init__(self, name, log, fail=False):
        self.name, self.log, self.fail = name, log, fail

    def open(self):
        self.log.append(f"open {self.name}")

    def close(self):
        self.log.append(f"close {self.name}")

    def process(self, item, out):
        if self.fail:
            raise StageException("bozuk")
        out.emit(item)


class PipelineTests(unittest.TestCase):
    def run_pipe(self, items, *stages):
        sink = CollectSink()
        p = Pipeline(ListSource(items), sink)
        for s in stages:
            p.add_stage(s)
        p.run()
        return sink.items

    def test_passthrough_without_stages(self):
        self.assertEqual(self.run_pipe(["a", "b"]), ["a", "b"])

    def test_filter_emits_zero_or_one(self):
        self.assertEqual(self.run_pipe(["x 200", "y 404"], Filter()), ["y 404"])

    def test_splitter_emits_many(self):
        self.assertEqual(self.run_pipe(["a b c"], Splitter()), ["a", "b", "c"])

    def test_stage_order(self):
        self.assertEqual(self.run_pipe(["a 404 b"], Filter(), Splitter()), ["a", "404", "b"])

    def test_lifecycle_open_in_order_close_reversed(self):
        log = []
        self.run_pipe(["a"], Recorder("1", log), Recorder("2", log))
        self.assertEqual(log, ["open 1", "open 2", "close 2", "close 1"])

    def test_close_called_on_error(self):
        log = []
        with self.assertRaises(StageException):
            self.run_pipe(["a"], Recorder("1", log, fail=True))
        self.assertEqual(log, ["open 1", "close 1"])


class FileSourceTests(unittest.TestCase):
    def test_strips_crlf(self):
        with tempfile.NamedTemporaryFile("wb", suffix=".log", delete=False) as f:
            f.write(b"one\r\ntwo\r\n")
        try:
            sink = CollectSink()
            Pipeline(FileLineSource(f.name), sink).run()
            self.assertEqual(sink.items, ["one", "two"])
        finally:
            os.remove(f.name)

    def test_missing_file_raises(self):
        with self.assertRaises(StageException):
            Pipeline(FileLineSource("yok.log"), CollectSink()).run()


class EndToEndTests(unittest.TestCase):
    def test_main_prints_every_line(self):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            code = logflow_main.main([SAMPLE])
        with open(SAMPLE, encoding="utf-8") as f:
            expected = f.read()
        self.assertEqual(code, 0)
        self.assertEqual(buf.getvalue(), expected)
        self.assertEqual(len(expected.splitlines()), 200)

    def test_main_missing_file_returns_1(self):
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            self.assertEqual(logflow_main.main(["yok.log"]), 1)
        self.assertIn("Hata", err.getvalue())


if __name__ == "__main__":
    unittest.main()
