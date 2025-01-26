from pyarrow.fs import LocalFileSystem

from davidkhala.data.format.arrow.fs import FS


class LocalFS(FS):
    fs = LocalFileSystem()
