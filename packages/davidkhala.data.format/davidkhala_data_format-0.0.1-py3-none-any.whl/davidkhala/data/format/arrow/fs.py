from pyarrow import RecordBatchFileWriter, RecordBatch, NativeFile
from pyarrow.fs import FileSystem, FileInfo, FileSelector


class FS:
    """
    Abstract FileSystem
    """
    fs: FileSystem

    def open_input_stream(self, file: FileInfo):
        return self.fs.open_input_stream(file.path)

    def ls(self, base_dir: str) -> FileInfo | list[FileInfo]:
        return self.fs.get_file_info(FileSelector(base_dir, recursive=True))

    @staticmethod
    def write(sink:str|NativeFile, record_batch: RecordBatch):
        """
        :param sink: Either a file path, or a writable file object [pyarrow.NativeFile].
        :param record_batch:
        :return:
        """
        with RecordBatchFileWriter(sink, record_batch.schema) as writer:
            writer.write(record_batch)