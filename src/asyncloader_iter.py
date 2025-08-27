import os
import typing as t
import asyncio
import utils
import aiohttp
from PIL import Image
import dataclasses
from numpy.typing import NDArray
import numpy as np


@dataclasses.dataclass
class Row:
    image: NDArray[np.uint8]
    name: str


async def maybe_download_sprite(session: aiohttp.ClientSession, sprite_url: str):
    async with session.get(sprite_url) as response:
        if response.status == 200:
            return await response.read()



async def download_and_save_pokemon(session, pokemon, output_dir):
    """Download and save a single pokemon."""
    content =  await maybe_download_sprite(session, pokemon["Sprite"])
    if content is not None:
        target_dir = os.path.join(output_dir, pokemon["Type1"])
        utils.maybe_create_dir(target_dir)
        filepath = os.path.join(target_dir, pokemon["Pokemon"] + ".png")
        utils.write_binary(filepath, content)
        print(f"Donwloading {pokemon['Pokemon']}")
        return Row(image = np.array(Image.open(filepath)), name=pokemon['Pokemon'])
    

async def dowload_and_save_all_pokemons(pokemons, output_dir):
    """Download and save all pokemons using a sequentially."""
    async with aiohttp.ClientSession() as session:
        tasks = [download_and_save_pokemon(session, p, output_dir) for p in pokemons]
        await asyncio.gather(*tasks, return_exceptions=True)

@utils.timeit
def main(output_dir: str, inputs: t.List[str]):
    """Download for all intpus and place them in output_dir."""
    utils.maybe_create_dir(output_dir)
    asyncio.run(dowload_and_save_all_pokemons(utils.read_pokemons(inputs), output_dir))
    
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("output_dir", help="directory to store the data")
    parser.add_argument("inputs", nargs="+", help="list of files with metadata")
    args = parser.parse_args()
    utils.maybe_remove_dir(args.output_dir)
    main(args.output_dir, args.inputs)