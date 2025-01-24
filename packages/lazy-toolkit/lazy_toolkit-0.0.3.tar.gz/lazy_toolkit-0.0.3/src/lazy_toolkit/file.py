import base64
import os
import zipfile
from io import BytesIO
from mimetypes import guess_extension, guess_type
from typing import Generator

from PIL import Image


def list_folder_content(directory: str,
                        include_files: bool = False,
                        include_dirs: bool = False,
                        ascend: bool | None = None,
                        remove_ext: bool = False) -> list[str]:
    """List content of given directory

    Args:
        directory (str): The directory to list content
        include_files (bool, optional): If include files in the result. Defaults to False.
        include_dirs (bool, optional): If include directories in the result. Defaults to False.
        ascend (bool | None, optional): How to sort the result, if None then no sorting, otherwise True for ascending and False for descending
        remove_ext (bool, optional): If the file extension should be removed (if `include_files`)
    """
    if not include_dirs and not include_files or not os.path.isdir(directory):
        return list()

    res: list[str] = [
        item if not remove_ext else os.path.splitext(item)[0] for item in os.listdir(directory)
        if (include_files and os.path.isfile(os.path.join(directory, item))) or
           (include_dirs and os.path.isdir(os.path.join(directory, item)))
    ]

    if ascend is not None:
        if ascend:
            return sorted(res)
        return sorted(res, reverse=True)
    return res


def chunk_read(file_path: str, start: int, end: int | None = None) -> tuple[bytes, int, int, int]:
    """Read a chunk of file at given path, starting from byte position start and ending at byte position end

    Returns: (chunk of content, start, length, file_size)
    """
    if not file_path or not os.path.isfile(file_path):
        return b'', 0, 0, 0

    file_size: int = os.stat(file_path).st_size
    if end is not None:
        length: int = end + 1 - start
    else:
        length: int = file_size - start

    with open(file_path, 'rb') as f:
        f.seek(start)
        chunk: bytes = f.read(length)
    return chunk, start, length, file_size


def chunk_read_yield(file_path: str, chunk_size: int) -> Generator[tuple[bytes, int, int, int], None, None]:
    """Read a file in chunks of given size, return a generator to iterate over the chunks

    Returns: (chunk of content, start, length, file_size)
    """
    if not file_path or not os.path.isfile(file_path):
        return

    file_size: int = os.stat(file_path).st_size
    with open(file_path, 'rb') as f:
        for start in range(0, file_size, chunk_size):
            f.seek(start)
            chunk: bytes = f.read(min(chunk_size, file_size - start))
            yield chunk, start, len(chunk), file_size


def zip_directory(dir: str, zip_file_path: str):
    """Compress given directory into a zip file
    """
    root: str = os.path.abspath(os.path.join(dir, os.pardir))
    with zipfile.ZipFile(zip_file_path, "w", zipfile.ZIP_DEFLATED) as zip:
        for parent_path, _, files in os.walk(dir):
            zip.write(parent_path, os.path.relpath(parent_path, root))
            for filename in files:
                file_path: str = os.path.join(parent_path, filename)
                if os.path.isfile(file_path):
                    zip.write(file_path, os.path.join(os.path.relpath(parent_path, root), filename))


def open_image_as_base64(path: str) -> str | None:
    """Open given image and convert to base64 string with file type header
    """
    if not path:
        return None

    _, extension = os.path.splitext(path)
    if not extension:
        return None

    extension = extension[1:].lower()
    try:
        buffer: BytesIO = BytesIO()
        img = Image.open(path)
        img.save(buffer, format=extension)
        base64_bytes: bytes = base64.b64encode(buffer.getvalue())
        return f'data:image/{extension};base64,{base64_bytes.decode("utf-8")}'
    except Exception:
        return None


def open_base64_as_image(base64_image: str) -> tuple[Image.Image | None, str | None]:
    """Convert a base64 image to PIL image and return with file extension info
    - The given base64 string MUST have file type header
    """
    if not base64_image:
        return None, None

    try:
        file_type, _ = guess_type(base64_image)
        if not file_type:
            return None, None

        # A special case: jpg is not a valid MINE type (but it is a valid extension), convert to jpeg manually
        if file_type == 'image/jpg':
            file_type = 'image/jpeg'
        extension: str | None = guess_extension(file_type)
        if not extension:
            return None, None
    except BaseException:
        return None, None

    try:
        _, body = base64_image.split(',')
        return Image.open(BytesIO(base64.b64decode(body))), extension
    except BaseException:
        return None, None
