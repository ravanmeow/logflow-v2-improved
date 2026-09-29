"""Main uc is yapar: argumanlari oku, hatti kur, run() cagir. Baska hicbir sey."""
import argparse
import sys

from logflow.console_sink import ConsoleSink
from logflow.file_line_source import FileLineSource
from logflow.pipeline import Pipeline


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        prog="logflow", description="Bir log dosyasini hat uzerinden konsola yazar.")
    parser.add_argument("path", help="okunacak log dosyasi (ornek: data/access-small.log)")
    args = parser.parse_args(argv)                                   # 1) arguman oku

    pipeline = Pipeline(FileLineSource(args.path), ConsoleSink())    # 2) hatti kur
    try:
        pipeline.run()                                               # 3) calistir
    except Exception as e:
        print(f"Hata: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
