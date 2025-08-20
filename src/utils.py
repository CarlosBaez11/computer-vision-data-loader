import csv
import functools
import os
import shutil
import time
import typing as t

def maybe_remove_dir(dirpath: str):
    """Remove a directory if it exists."""
    if os.path.isdir(dirpath):
        shutil.rmtree(dirpath)

def maybe_create_dir(dirpath: str):
    """Create a directory if if does not exists already."""
    if not os.path.isdir(dirpath):
        try:
            os.makedirs(dirpath)
        except FileExistsError:
            pass

def timeit(f: t.Callable):
    """Measure the execution time of a function."""
    @functools.wraps(f)
    def timed(*args, **kwargs):
        ts = time.time()
        result = f(*args, **kwargs)
        elapsed_time = time.time() - ts
        print(f"Elapsed is {elapsed_time:2.4f}")
        return result
    return timed


def read_csv_rows_as_dict(filepath: str):
    """Iterate over the rows of a single csv."""
    with open(filepath, mode="r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            yield row

def read_all_csv_rows_as_dict(inputs: t.List[str]):
    """Iterate over all rows from all csvs."""
    for fpath in inputs:
        for row in read_csv_rows_as_dict(fpath):
            yield row


def read_pokemons(inputs: t.List[str]):
    """Read all csv inputs and make lowercase."""
    for row in read_all_csv_rows_as_dict(inputs):
        row["Type1"] = row["Type1"].lower()
        row["Pokemon"] = row["Pokemon"].lower()
        yield row

def write_binary(filepath: str, content: bytes):
    """Write binary contents to a file."""
    with open(filepath, mode="wb") as f:
        f.write(content)


def maybe_download_sprite(session, sprite_url: str):
    """Return the content of a sprite if the get request is successfull.

    Note that this function is noy asynchronous, so it may be inneficient to called it
    withing an async function.
    """
    content = None
    with session.get(sprite_url) as response:
        if response.status_code == 200:
            content = response.content
    return content