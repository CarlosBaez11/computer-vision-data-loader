import dataclasses
import pathlib
import requests
from typing import Annotated, Callable, Iterator, Sequence

import numpy as np


@dataclasses.dataclass
class Row:
    image: np.ndarray
    name: str


def download(source: str) -> bytes:
    response = requests.get(source)
    return response.content


def load(
    sources: Sequence[Annotated[pathlib.Path, "CSV File"]],
    *,
    downloader: Callable[[str], bytes] = download,
) -> Iterator[Row]:
    raise NotImplementedError
