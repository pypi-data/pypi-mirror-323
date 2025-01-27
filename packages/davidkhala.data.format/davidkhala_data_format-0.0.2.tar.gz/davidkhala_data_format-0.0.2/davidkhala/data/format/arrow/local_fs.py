from pyarrow import NativeFile
from pyarrow.fs import LocalFileSystem

from davidkhala.data.format.arrow.fs import FS


class LocalFS(FS):
    fs = LocalFileSystem()
    overwrite = False
    def open_output_stream(self, uri: str, *args) -> NativeFile:
        if self.overwrite:
            return super().open_output_stream(uri)
        else:
            return self.fs.open_append_stream(uri)
