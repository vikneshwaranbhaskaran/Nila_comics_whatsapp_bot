import logging
from flask import current_app, jsonify
import json
import requests

from app.services.openai_service import generate_response
import re


def log_http_response(response):
    logging.info(f"Status: {response.status_code}")
    logging.info(f"Content-type: {response.headers.get('content-type')}")
    logging.info(f"Body: {response.text}")


def get_text_message_input(recipient, text):
    return json.dumps(
        {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": recipient,
            "type": "text",
            "text": {"preview_url": False, "body": text},
        }
    )

def get_image_message_input(recipient, link):
    return json.dumps(
        {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": recipient,
            "type": "image",
            "image": {
                "link": link
            }
        }
    )

def get_interactive_button_message(recipient, text, buttons):
    """
    Constructs an interactive button message (max 3 buttons allowed).
    """
    button_list = []
    for i, btn_text in enumerate(buttons):
        button_list.append({
            "type": "reply",
            "reply": {
                "id": f"btn_{i}",
                "title": btn_text
            }
        })
        
    return json.dumps(
        {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": recipient,
            "type": "interactive",
            "interactive": {
                "type": "button",
                "body": {
                    "text": text
                },
                "action": {
                    "buttons": button_list
                }
            }
        }
    )

def get_interactive_list_message(recipient, text, button_text, options):
    """
    Constructs an interactive list message (max 10 options).
    """
    rows = []
    for i, opt_text in enumerate(options):
        rows.append({
            "id": f"list_opt_{i}",
            "title": opt_text
        })
        
    return json.dumps(
        {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": recipient,
            "type": "interactive",
            "interactive": {
                "type": "list",
                "body": {
                    "text": text
                },
                "action": {
                    "button": button_text,
                    "sections": [
                        {
                            "title": "Options",
                            "rows": rows
                        }
                    ]
                }
            }
        }
    )


def send_message(data):
    headers = {
        "Content-type": "application/json",
        "Authorization": f"Bearer {current_app.config['ACCESS_TOKEN']}",
    }

    url = f"https://graph.facebook.com/{current_app.config['VERSION']}/{current_app.config['PHONE_NUMBER_ID']}/messages"

    logging.info(f"Sending message to Graph API URL: {url}")
    logging.info(f"Outgoing payload: {data}")

    try:
        response = requests.post(
            url, data=data, headers=headers, timeout=10
        )  # 10 seconds timeout as an example
        response.raise_for_status()  # Raises an HTTPError if the HTTP request returned an unsuccessful status code
    except requests.Timeout:
        logging.error("Timeout occurred while sending message")
        return jsonify({"status": "error", "message": "Request timed out"}), 408
    except (
        requests.RequestException
    ) as e:  # This will catch any general request exception
        logging.error(f"Request failed due to: {e}")
        if hasattr(e, 'response') and e.response is not None:
            logging.error(f"Graph API error response body: {e.response.text}")

        return jsonify({"status": "error", "message": "Failed to send message"}), 500
    else:
        # Process the response as normal
        logging.info(f"Graph API response status: {response.status_code}")
        log_http_response(response)
        return response


def process_text_for_whatsapp(text):
    # Remove brackets
    pattern = r"\【.*?\】"
    # Substitute the pattern with an empty string
    text = re.sub(pattern, "", text).strip()

    # Pattern to find double asterisks including the word(s) in between
    pattern = r"\*\*(.*?)\*\*"

    # Replacement pattern with single asterisks
    replacement = r"*\1*"

    # Substitute occurrences of the pattern with the replacement
    whatsapp_style_text = re.sub(pattern, replacement, text)

    return whatsapp_style_text


def process_whatsapp_message(body):
    from app.services.bot_service import process_incoming_message
    process_incoming_message(body)

def is_valid_whatsapp_message(body):
    """
    Check if the incoming webhook event has a valid WhatsApp message structure.
    """
    return (
        body.get("object")
        and body.get("entry")
        and body["entry"][0].get("changes")
        and body["entry"][0]["changes"][0].get("value")
        and body["entry"][0]["changes"][0]["value"].get("messages")
        and body["entry"][0]["changes"][0]["value"]["messages"][0]
    )

