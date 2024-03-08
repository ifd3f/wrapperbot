# Wrapperbot

Write your bot's logic and let Wrapperbot handle the posting!

## Usage

Let's say you have a script for generating posts that writes the post to stdout:

```
$ ./generate_post.py
nya nya mrp meow
```

First, set some environment variables to configure wrapperbot:

```sh
export WRAPPERBOT_API_BASE_URL=https://fedi.example.com
export WRAPPERBOT_EMAIL=catgpt@example.com
export WRAPPERBOT_PASSWORD=hunter2
export WRAPPERBOT_CLIENT_NAME="Paws"
```

To post _once_ to the fediverse using that script as a generator, pipe its output into wrapperbot:

```sh
wrapperbot post './generate_post.py'
```

To schedule the bot to post every hour, you can use cron or systemd timers.

To have wrapperbot reply to people:

```sh
wrapperbot reply './generate_post.py'
```

This will keep running until you cancel it.

## API

### Post mode

Wrapperbot expects your provided script to write posts to stdout.

### Reply mode

Wrapperbot will call your script once every time it has been mentioned. It will expect your provided script to read the message it was mentioned with from stdin, and write its own response to stdout. If your bot does not change its output based on replies, it may ignore stdin.

Your script will be called with the `REPLY_TO` environment variable, containing the username of the user that replied to you (for example, `@astrid@fedi.example.com`).

To _not_ reply to the user, output a single '\0'.
