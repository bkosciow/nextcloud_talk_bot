# Nextcloud Bot
Nextcloud Bot is a Python script that allows you to interact with the Nextcloud Talk app.
When you register bot via:

```
occ talk:bot:install <bot-name> <bot-secret> <webhook-url>
```


# Installation

```
pip install git+https://github.com/bkosciow/nextcloud_talk_bot.git
``` 

You can use it in your Nextcloud Talk conversations.

Each message on channel is sent to the bot.
Package takes care of signature verification and sending reply.

Configuration goes to the .env file, simplest one:

```
BOT_SECRET=<bot-secret>
NEXTCLOUD_URL=https://cloud.local
WEBHOOK_PORT=10002
```


All your code goes into a function that is passed as argument for the server. 
This function is started as a new thread, so it can work for a long time.

There is a Flask version.

Example:

```
from nextcloud_talk_bot_kosci.flask import init_server, app
import time
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()


def action(request):
    if request.data.message.startswith('!time'):
        request.send_response(
            " Executing...",
            request.data['target']['id'],
            request.data['object']['id']
        )
        time.sleep(10)
        request.send_response(
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            request.data['target']['id']
        )


init_server(
    os.environ.get('NEXTCLOUD_URL'),
    os.environ.get('BOT_SECRET'),
    action
)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=os.environ.get('WEBHOOK_PORT'), debug=True)

```