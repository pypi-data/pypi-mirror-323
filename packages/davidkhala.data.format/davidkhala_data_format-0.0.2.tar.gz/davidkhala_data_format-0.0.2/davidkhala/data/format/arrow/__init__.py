from pyarrow import Buffer, BufferReader


def read_data(buffer: bytes | Buffer):
    return BufferReader(buffer)
