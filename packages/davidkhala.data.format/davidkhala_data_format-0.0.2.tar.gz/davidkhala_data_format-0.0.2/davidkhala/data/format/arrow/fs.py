from typing import Iterable

from pyarrow import RecordBatchFileWriter, RecordBatch, NativeFile, Table, RecordBatchStreamWriter
from pyarrow.fs import FileSystem, FileInfo, FileSelector


def write_batch(sink: str | NativeFile, table_or_batch: RecordBatch | Table):
    """
    :param sink: Either a file path, or a writable file object [pyarrow.NativeFile].
    :param table_or_batch:
    :return:
    """
    with RecordBatchFileWriter(sink, table_or_batch.schema) as writer:
        writer.write(table_or_batch)


def write_stream(sink: str | NativeFile, tables_or_batches: Iterable[RecordBatch | Table]):
    writer: RecordBatchStreamWriter | None = None
    for table_or_batch in tables_or_batches:
        if not writer:
            writer = RecordBatchStreamWriter(sink, table_or_batch.schema)
        writer.write(table_or_batch)
    if writer:
        writer.close()


class FS:
    """
    Abstract FileSystem
    """
    fs: FileSystem

    def open_output_stream(self, path, compression=None, buffer_size=None, metadata=None) -> NativeFile:
        return self.fs.open_output_stream(path)

    def open_input_stream(self, file: FileInfo) -> NativeFile:
        return self.fs.open_input_stream(file.path)

    def ls(self, base_dir: str) -> FileInfo | list[FileInfo]:
        return self.fs.get_file_info(FileSelector(base_dir, recursive=True))

    def write_stream(self, uri, tables_or_batches: Iterable[RecordBatch | Table]):
        with self.open_output_stream(uri) as stream:
            write_stream(stream, tables_or_batches)

    def write_batch(self, uri, table_or_batch: RecordBatch | Table):
        with self.open_output_stream(uri) as stream:
            write_batch(stream, table_or_batch)
