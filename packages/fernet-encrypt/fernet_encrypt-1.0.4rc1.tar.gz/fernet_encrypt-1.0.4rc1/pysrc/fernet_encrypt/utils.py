from collections.abc import Generator
from glob import glob
from pathlib import Path
from time import time

from fernet_encrypt import logger

KEY_PATH = Path(__file__).parent / "keys"


def key_getter() -> Generator[bytes, None, None]:
    keyfiles = sorted(glob(str(KEY_PATH / "*.key")), reverse=True)

    if len(keyfiles) == 0:
        raise Exception("No keyfiles found. Create a key first.")

    for keyfile in keyfiles:
        with open(keyfile, "rb") as f:
            yield f.read()


def key_setter(key: bytes):
    keyfile = KEY_PATH / f"{int(time())}.key"

    with open(keyfile, "wb") as f:
        f.write(key)

    logger.info(f"Created keyfile: {keyfile}")
