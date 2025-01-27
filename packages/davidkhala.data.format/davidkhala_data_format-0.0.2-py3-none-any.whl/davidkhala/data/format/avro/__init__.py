from typing import Iterator, IO

import fastavro


def read(content) -> Iterator[dict]:
    reader = fastavro.reader(content)
    for record in reader:
        yield record


def is_avro(file_path: str):
    return fastavro.is_avro(file_path)


def is_avro_data(buffer: IO):
    return fastavro.is_avro(buffer)
