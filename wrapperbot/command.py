import logging
import subprocess
from typing import Callable, Optional

logger = logging.getLogger(__name__)


PostGenerator = Callable[[], Optional[str]]


def generate_toot(command: str) -> Optional[str]:
    logger.debug("Executing command: %r", command)
    stdout = subprocess.check_output(command, shell=True)
    if stdout.startswith(b"\0"):
        return None
    return stdout.decode()


def toot_generator(command: str) -> PostGenerator:
    return lambda: generate_toot(command)
