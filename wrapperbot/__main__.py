import asyncio
import click
import os
from mastodon import Mastodon
import logging
from wrapperbot.command import generate_toot

from wrapperbot.reply import reply_loop


logger = logging.getLogger(__name__)


def main():
    cli()


@click.group()
@click.option("--log-level", default="info")
def cli(log_level: str):
    setup_logging(log_level)


@cli.command()
@click.argument("command")
def post(command: str):
    m = get_mastodon()

    result = generate_toot(command)
    if result is None:
        logger.info("No toot was generated, will not post")
        return

    logger.info("Tooting: %r", result)
    m.toot(result)


@cli.command()
@click.argument("command")
def reply(command: str):
    m = get_mastodon()
    asyncio.run(reply_loop(m, lambda: generate_toot(command)))


def get_mastodon() -> Mastodon:
    base_url: str = os.environ["WRAPPERBOT_API_BASE_URL"]
    email: str = os.environ["WRAPPERBOT_EMAIL"]
    password: str = os.environ["WRAPPERBOT_PASSWORD"]
    client_name: str = os.environ.get("WRAPPERBOT_CLIENT_NAME", "Wrapperbot")

    logger.info(
        "Setting up with email=%r, base_url=%r, client_name=%r",
        email,
        base_url,
        client_name,
    )

    (client_id, client_secret) = Mastodon.create_app(
        client_name=client_name,
        api_base_url=base_url,
    )

    m = Mastodon(
        api_base_url=base_url,
        client_id=client_id,
        client_secret=client_secret,
    )
    m.log_in(
        username=email,
        password=password,
        scopes=["read", "write"],
    )
    return m


def setup_logging(log_level: str):
    # following https://docs.python.org/3/howto/logging.html#logging-to-a-file
    logging.basicConfig(level=getattr(logging, log_level.upper()))


if __name__ == "__main__":
    main()
