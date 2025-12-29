# Nextcloud Bot
Framework for Nextcloud bots, handles auth, signing and command patters.


# Installation

```
pip install git+https://github.com/bkosciow/nextcloud_talk_bot.git
``` 

Register bot @ NC

```
occ talk:bot:install <bot-name> <bot-secret> <webhook-url>
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

Example (FLASK):

```
from nextcloud_talk_bot_kosci.flask import init_server, app
import time
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

patterns = [
    '!time',
]

def action(request):
    cmd = request.parse_command(patterns)
    if cmd.result:
        if cmd.command == "!time":
            request.reply(" Executing...")
            time.sleep(10)
            request.post(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))


init_server(
    os.environ.get('NEXTCLOUD_URL'),
    os.environ.get('BOT_SECRET'),
    action
)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=os.environ.get('WEBHOOK_PORT'), debug=True)

```



Example (FastAPI, experimental)

```
from nextcloud_talk_bot_kosci.fastapi import init_server, app
import time
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()


def action(request):
    if request.data.message.startswith('!time'):
        request.send_response(
            "Executing...",
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

if __name__ == "__main__":
    import uvicorn
    # Run the FastAPI app
    uvicorn.run(
        "__main__:app", reload=True, host="0.0.0.0", port=int(os.environ.get('WEBHOOK_PORT', 8000)),
    )
```