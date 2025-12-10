from flask import Flask, request, jsonify
from flask import request, abort
from nextcloud_talk_bot_kosci.request_data import RequestData
from nextcloud_talk_bot_kosci.helper import send_message
import hmac
import hashlib
import functools
import threading


app = Flask(__name__)


def verify_signature(secret):
    """Decorator to verify Nextcloud webhook signature with custom secret"""

    def decorator(f):
        @functools.wraps(f)
        def decorated_function(*args, **kwargs):
            signature = request.headers.get('X-Nextcloud-Talk-Signature', '')
            random_header = request.headers.get('X-Nextcloud-Talk-Random', '')
            if not signature:
                abort(401)

            data = request.data

            signature_data = random_header + data.decode('utf-8')
            expected_sig = hmac.new(
                secret.encode('utf-8'),
                signature_data.encode('utf-8'),
                hashlib.sha256
            ).hexdigest()

            if not hmac.compare_digest(signature, expected_sig):
                abort(401)

            return f(*args, **kwargs)

        return decorated_function

    return decorator


def init_server(nextcloud_url, bot_secret, callback):
    class Request:
        def __init__(self, data):
            self.data = data

        def send_response(self, message, channel_id, message_id=None):
            send_message(nextcloud_url, bot_secret, message, channel_id, message_id)

    @app.route('/webhook', methods=['POST'])
    @verify_signature(bot_secret)
    def webhook():
        request_data = RequestData(request.json)
        # print(f"Received webhook: {data}")

        thread = threading.Thread(
            target=callback,
            args=(Request(request_data),)
        )
        thread.daemon = True
        thread.start()

        return jsonify({"success": True}), 200

    @app.route('/health', methods=['GET'])
    def health():
        """Health check endpoint"""
        return jsonify({"status": "healthy"}), 200
