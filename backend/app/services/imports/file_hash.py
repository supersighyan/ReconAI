import hashlib
from typing import BinaryIO


def sha256_file(file: BinaryIO, chunk_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    while chunk := file.read(chunk_size):
        digest.update(chunk)
    return digest.hexdigest()
