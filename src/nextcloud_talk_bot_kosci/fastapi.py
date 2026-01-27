from fastapi import FastAPI, Request, HTTPException, status
from fastapi.responses import JSONResponse
from nextcloud_talk_bot_kosci.request_data import RequestData
from nextcloud_talk_bot_kosci.helper import send_message, add_reaction
from nextcloud_talk_bot_kosci.command import Command
from fastapi import BackgroundTasks
import hmac
import hashlib
import functools

app = FastAPI()


def verify_signature(secret):
    """Decorator to verify Nextcloud webhook signature with custom secret"""
    def decorator(f):
        @functools.wraps(f)
        async def decorated_function(*args, **kwargs):
            request: Request = kwargs.get('request')
            signature = request.headers.get('X-Nextcloud-Talk-Signature', '')
            random_header = request.headers.get('X-Nextcloud-Talk-Random', '')
            if not signature:
                raise HTTPException(status_code=401, detail="Missing signature")
            data = await request.body()
            data_str = data.decode('utf-8')
            signature_data = random_header + data_str
            expected_sig = hmac.new(
                secret.encode('utf-8'),
                signature_data.encode('utf-8'),
                hashlib.sha256
            ).hexdigest()
            if not hmac.compare_digest(signature, expected_sig):
                raise HTTPException(status_code=401, detail="Invalid signature")
            return await f(*args, **kwargs)
        return decorated_function
    return decorator


def init_server(nextcloud_url, bot_secret, callback):
    class RequestWrapper:
        def __init__(self, data):
            self.data = data

        def send_response(self, message, channel_id, message_id=None):
            send_message(nextcloud_url, bot_secret, message, channel_id, message_id)

        def post(self, message):
            self.send_response(message, self.data['target']['id'])

        def reply(self, message):
            self.send_response(message, self.data['target']['id'], self.data['object']['id'])

        def react(self, emoji):
            add_reaction(nextcloud_url, bot_secret, emoji, self.data['target']['id'], self.data['object']['id'])

        def parse_command(self, patterns):
            cmd = Command(patterns)
            cmd.parse(self.data.message)
            return cmd

    @app.post("/webhook")
    @verify_signature(bot_secret)
    async def webhook(request: Request, background_tasks: BackgroundTasks):
        data = await request.json()
        background_tasks.add_task(callback, RequestWrapper(RequestData(data)))

        return JSONResponse({"success": True})

    @app.get("/health")
    async def health():
        return JSONResponse({"status": "healthy"})
