import logging
from typing import Any, Callable, Optional
from mastodon import Mastodon
from pleroma import Pleroma


LOOP_COOLDOWN_TIME = 5
MAX_THREAD_LENGTH = 10
MAX_RETRIES = 5

logger = logging.getLogger(__name__)


async def reply_loop(
    m: Mastodon,
    generator: Callable[[], Optional[str]],
):
    p = Pleroma(api_base_url=m.api_base_url, access_token=m.access_token)

    myself = (await p.me())["id"]
    logger.info("I am ID %r", myself)

    async for n in p.stream_mentions():
        logger.debug("Got notification: %r", n)

        await handle_notif(p, myself, n, generator)


async def handle_notif(
    pleroma: Pleroma,
    myself: str,
    notification: Any,
    generator: Callable[[], Optional[str]],
):
    post_id = notification["status"]["id"]

    context = await pleroma.status_context(post_id)
    length = get_thread_length(context, myself)
    logger.debug("Thread length is %s", length)
    if length >= MAX_THREAD_LENGTH:
        logger.info("Reached max thread length, refusing to reply")
        return

    toot = generator()
    if toot is None:
        logger.info("Not replying because the process returned a null byte")
        return

    logger.info("Replying %r", toot)
    await pleroma.reply(notification["status"], toot)


def get_thread_length(context: Any, myself: str) -> int:
    posts = 0
    for post in context["ancestors"]:
        if post["account"]["id"] == myself:
            posts += 1
    return posts
