import pathlib
from typing import Iterator

from pyarrow import NativeFile, Table, RecordBatch
from pyarrow.parquet import ParquetFile, ParquetSchema


class Parquet:
    def __init__(self, file_path: str | pathlib.Path | NativeFile):
        self.file = ParquetFile(file_path)

    @property
    def schema(self) -> ParquetSchema:
        return self.file.schema

    def read_batch(self) -> Table:
        return self.file.read()
    def read_stream(self)-> Iterator[RecordBatch]:
        return self.file.iter_batches()
