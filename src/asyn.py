import csv
import io
import pathlib
import uuid

import pytest
import numpy as np
from PIL import Image
from src import loader

from typing import Iterator


class ImageLoader:
    def __init__(self, image_path: str):
        self.image_path =  image_path
        image_name = []

    def _load_image(self):
        Image.open(self.image_path)




def _build_source(
    dir: pathlib.Path, image: np.ndarray, name: str
) -> tuple[pathlib.Path, str, bytes]:
    source = dir / f"{uuid.uuid4()}.csv"
    sprite = dir / f"{uuid.uuid4()}.png"
    im = Image.fromarray(image)
    image_bytes = io.BytesIO()
    im.save(image_bytes, format="png")
    with open(source, "w", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=["Pokemon", "Sprite"])
        writer.writeheader()
        writer.writerow({"Pokemon": name, "Sprite": sprite})
    return source, str(sprite), image_bytes.getvalue()