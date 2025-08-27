import dataclasses
import pathlib
import requests
import aiohttp
import os
import time
import utils
from typing import Annotated, Callable, Iterator, Sequence
import numpy as np
from PIL import Image
import asyncio
from asyncio.queues import Queue
from numpy.typing import NDArray
from typing import Optional, List


@dataclasses.dataclass
class Row:
    image: NDArray[np.uint8]
    name: str

async def maybe_download_sprite(session, sprite_url: str):
    async with session.get(sprite_url) as response:
        if response.status == 200:
            return await response.read()


async def download_and_save_pokemon(session, pokemon, output_dir) -> Optional[Row]:
    """Download and save a single pokemon."""

    content =  await maybe_download_sprite(session, pokemon["Sprite"])

    if content is not None:
        target_dir = os.path.join(output_dir, pokemon["Type1"])
        utils.maybe_create_dir(target_dir)
        filepath = os.path.join(target_dir, pokemon["Pokemon"] + ".png")
        utils.write_binary(filepath, content)
        print(f"Donwloading {pokemon['Pokemon']}")
        return Row(image = np.array(Image.open(filepath)), name=pokemon['Pokemon'])

async def image_downloader(queue: Queue, pokemons, output_dir: str):
    async with aiohttp.ClientSession() as session:
        tasks = [asyncio.create_task(download_and_save_pokemon(session, pokemon, output_dir)) for pokemon in pokemons]
        for task in asyncio.as_completed(tasks):
            row = await task
            if isinstance(row, Row):
                await queue.put(row)
        await queue.put(None)


async def image_loader(queue: Queue):
    
    while True:
        start = time.perf_counter()
        row: Row = await queue.get()
        if row is None:
            queue.task_done()
            break 
        end = time.perf_counter()
        print(f"Loaded {row.name} ({row.image.shape})")
        print(f"Carga de {row.name}  en {end - start:.2f} s")
        queue.task_done()


@utils.timeit
async def main(inputs: List[str], output_dir: str):
    """Download for all intpus and place them in output_dir."""
    utils.maybe_create_dir(output_dir)
    queue = Queue(1)
    pokemons = utils.read_pokemons(inputs)
    print(pokemons)
    downloader_tasks = asyncio.create_task(image_downloader(queue, pokemons, output_dir))
    loader_tasks = asyncio.create_task(image_loader(queue))
    await asyncio.gather(downloader_tasks, loader_tasks)
    await queue.join()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--output_dir", help="directory to store the data")
    parser.add_argument("--inputs", nargs="+", help="list of files with metadata")
    args = parser.parse_args()
    utils.maybe_remove_dir(args.output_dir)
    asyncio.run(main(args.inputs, args.output_dir))