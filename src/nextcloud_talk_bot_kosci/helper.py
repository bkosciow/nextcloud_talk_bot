import json
import os
import requests
import hashlib
import hmac


def send_message(url, secret, message, channel_id, message_id=None):
    """Send a message back to Nextcloud Talk"""
    url = f"{url}/ocs/v2.php/apps/spreed/api/v1/bot/{channel_id}/message"
    payload = {
        "message": message
    }

    if message_id:
        payload["replyTo"] = message_id

    random_value = hashlib.sha256(os.urandom(32)).hexdigest()
    request_body = json.dumps(payload)

    signature_data = random_value + message
    signature = hmac.new(
        secret.encode('utf-8'),
        signature_data.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()

    headers = {
        "OCS-APIRequest": "true",
        "Content-Type": "application/json",
        "X-Nextcloud-Talk-Bot-Random": random_value,
        "X-Nextcloud-Talk-Bot-Signature": signature
    }

    response = requests.post(url, data=request_body, headers=headers)
    response.raise_for_status()
    print(response.content)
