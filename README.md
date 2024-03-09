# Wrapperbot

Write your bot's logic and let Wrapperbot handle the posting!

## Usage

Let's say you have a script for generating posts that writes the post to stdout:

```
$ python3 ./generate_post.py
nya nya mrp meow
```

First, set some environment variables to configure wrapperbot:

```sh
# fediverse server's URL
export WRAPPERBOT_API_BASE_URL=https://fedi.example.com

# email your account is signed up with
export WRAPPERBOT_EMAIL=catgpt@example.com

# your password, in plaintext
export WRAPPERBOT_PASSWORD=hunter2

# what the field should show up as
export WRAPPERBOT_CLIENT_NAME="Paws"
```

To post _once_ to the fediverse using that script as a generator:

```sh
wrapperbot post 'python3 ./generate_post.py'
```

To schedule the bot to post every hour, you can use cron or systemd timers.

To have wrapperbot reply to people:

```sh
wrapperbot reply 'python3 ./generate_post.py'
```

This will keep running until you cancel it.

Note that the argument is an arbitrary script executable by your system's shell! This can technically work, though it might not look very good:

```sh
wrapperbot post 'fortune | cowsay'
```

## Other environment variables

- `WRAPPERBOT_MAX_THREAD_LENGTH` - Used in replies. If the thread length exceeds this many posts, the bot will not reply. Default is 10.
- `WRAPPERBOT_REPLY_TO_BOTS` - Used in replies. If set to `1` and a bot mentions wrapperbot, then wrapperbot will not reply. Default is `0`.

## API for post generator scripts

### Post mode

Wrapperbot expects your provided script to write posts to stdout.

### Reply mode

Wrapperbot will call your script once every time it has been mentioned. It will expect your provided script to read the message it was mentioned with from stdin, and write its own response to stdout. If your bot does not change its output based on replies, it may ignore stdin.

Your script will be called with the `REPLY_TO` environment variable, containing the username of the user that replied to you (for example, `@astrid@fedi.example.com`).

To _not_ reply to the user, output a single '\0'.
