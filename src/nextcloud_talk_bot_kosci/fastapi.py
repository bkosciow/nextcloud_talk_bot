from fastapi import FastAPI, Request, HTTPException, status
from nextcloud_talk_bot_kosci.request_data import RequestData
from nextcloud_talk_bot_kosci.helper import send_message
import hmac
import hashlib
import threading
from typing import Callable

app = FastAPI()

nextcloud_url = ""
bot_secret = ""
callback_func: Callable = None


def verify_signature(secret: str):
    """Dependency to verify Nextcloud webhook signature with custom secret"""
    async def verify(request: Request):
        signature = request.headers.get('X-Nextcloud-Talk-Signature', '')
        random_header = request.headers.get('X-Nextcloud-Talk-Random', '')
        if not signature:
            raise HTTPException(status_code=401, detail="Missing signature")

        body = await request.body()
        data = body.decode('utf-8')
        signature_data = random_header + data

        expected_sig = hmac.new(
            secret.encode('utf-8'),
            signature_data.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()

        if not hmac.compare_digest(signature, expected_sig):
            raise HTTPException(status_code=401, detail="Invalid signature")

    return verify


class RequestWrapper:
    def __init__(self, data):
        self.data = data

    def send_response(self, message: str, channel_id: str, message_id: str = None):
        send_message(nextcloud_url, bot_secret, message, channel_id, message_id)


def init_server(nextcloud_url_param: str, bot_secret_param: str, callback: Callable):
    global nextcloud_url, bot_secret, callback_func
    nextcloud_url = nextcloud_url_param
    bot_secret = bot_secret_param
    callback_func = callback

    @app.post("/webhook")
    async def webhook(request: Request, verify=verify_signature(bot_secret)):
        await verify(request)
        body = await request.body()
        json_data = await request.json()

        request_data = RequestData(json_data)

        wrapped_request = RequestWrapper(request_data)

        # Process in background thread
        def process_callback():
            callback_func(wrapped_request)

        # Run in background thread
        thread = threading.Thread(target=process_callback)
        thread.daemon = True
        thread.start()

        return {"success": True}

    @app.get("/health")
    async def health():
        """Health check endpoint"""
        return {"status": "healthy"}
