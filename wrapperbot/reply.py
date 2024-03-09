import logging
import os
from typing import Any
from mastodon import Mastodon
from pleroma import Pleroma

from wrapperbot.command import PostGenerator


MAX_THREAD_LENGTH: int = int(os.environ.get("WRAPPERBOT_MAX_THREAD_LENGTH", "10"))
REPLY_TO_BOTS: bool = os.environ.get("WRAPPERBOT_REPLY_TO_BOTS", "0") == "1"

logger = logging.getLogger(__name__)


async def reply_loop(m: Mastodon, generator: PostGenerator):
    p = Pleroma(api_base_url=m.api_base_url, access_token=m.access_token)

    myself = (await p.me())["id"]
    logger.info("I am ID %r", myself)
    logger.info(
        "MAX_THREAD_LENGTH=%s, REPLY_TO_BOTS=%s", MAX_THREAD_LENGTH, REPLY_TO_BOTS
    )

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
        logger.info("Received notification")
        logger.debug("Full notification: %r", n)

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
        logger.info(
            "Reached max thread length (%s >= %s), refusing to reply",
            length,
            MAX_THREAD_LENGTH,
        )
        return

    if notification["account"]["bot"] and not REPLY_TO_BOTS:
        logger.info("Account is bot, refusing to reply")
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
