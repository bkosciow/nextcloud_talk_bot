from typing import Dict, Optional

import json
import os
import requests
import hashlib
import hmac


def send_message(
    url: str, 
    secret: str, 
    message: str, 
    channel_id: str, 
    message_id: Optional[str] = None
) -> None:
    """Send a message back to Nextcloud Talk"""
    url = f"{url}/ocs/v2.php/apps/spreed/api/v1/bot/{channel_id}/message"
    payload: Dict[str, str] = {
        "message": message
    }

    if message_id:
        payload["replyTo"] = message_id

    random_value: str = hashlib.sha256(os.urandom(32)).hexdigest()
    request_body: str = json.dumps(payload)

    signature_data: str = random_value + message
    signature: str = hmac.new(
        secret.encode('utf-8'),
        signature_data.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()

    headers: Dict[str, str] = {
        "OCS-APIRequest": "true",
        "Content-Type": "application/json",
        "X-Nextcloud-Talk-Bot-Random": random_value,
        "X-Nextcloud-Talk-Bot-Signature": signature
    }

    response: requests.Response = requests.post(url, data=request_body, headers=headers)
    response.raise_for_status()
    # print(response.content)


def add_reaction(url: str, secret: str, emoji: str, channel_id: str, message_id: str) -> None:
    api_url = f"{url}/ocs/v2.php/apps/spreed/api/v1/bot/{channel_id}/reaction/{message_id}"

    payload: Dict[str, str] = {
        "reaction": emoji
    }

    random_value: str = hashlib.sha256(os.urandom(32)).hexdigest()
    request_body: str = json.dumps(payload)
    signature_data: str = random_value + emoji
    signature: str = hmac.new(
        secret.encode('utf-8'),
        signature_data.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()

    headers: Dict[str, str] = {
        "OCS-APIRequest": "true",
        "Content-Type": "application/json",
        "X-Nextcloud-Talk-Bot-Random": random_value,
        "X-Nextcloud-Talk-Bot-Signature": signature
    }

    response: requests.Response = requests.post(api_url, data=request_body, headers=headers)
    response.raise_for_status()
