import logging
from typing import Any, Callable, Optional
from mastodon import Mastodon
from pleroma import Pleroma

from wrapperbot.command import PostGenerator


LOOP_COOLDOWN_TIME = 5
MAX_THREAD_LENGTH = 10
MAX_RETRIES = 5

logger = logging.getLogger(__name__)


async def reply_loop(m: Mastodon, generator: PostGenerator):
    p = Pleroma(api_base_url=m.api_base_url, access_token=m.access_token)

    myself = (await p.me())["id"]
    logger.info("I am ID %r", myself)

    while True:
        logger.info("Running stream loop")
        try:
            await stream_and_handle_notifs(generator, p, myself)
        except Exception as e:
            logger.warn(
                "Exception encountered while streaming mentions! "
                "Backing off and trying again",
                exc_info=e,
            )


async def stream_and_handle_notifs(generator, p, myself):
    async for n in p.stream_mentions():
        logger.debug("Got notification: %r", n)

        try:
            await handle_notif(p, myself, n, generator)
        except Exception as e:
            logger.warn("Failed to handle notification!", exc_info=e)


async def handle_notif(
    pleroma: Pleroma,
    myself: str,
    notification: Any,
    generator: PostGenerator,
):
    post_id = notification["status"]["id"]

    context = await pleroma.status_context(post_id)
    length = get_thread_length(context, myself)
    logger.debug("Thread length is %s", length)
    if length >= MAX_THREAD_LENGTH:
        logger.info("Reached max thread length, refusing to reply")
        return

    try:
        toot = generator()
    except Exception as e:
        logger.warn("Failed to generate toot!", exc_info=e)
        return

    if toot is None:
        logger.info("No toot was generated, will not reply")
        return

    logger.info("Replying %r", toot)
    await pleroma.reply(notification["status"], toot)


def get_thread_length(context: Any, myself: str) -> int:
    posts = 0
    for post in context["ancestors"]:
        if post["account"]["id"] == myself:
            posts += 1
    return posts
